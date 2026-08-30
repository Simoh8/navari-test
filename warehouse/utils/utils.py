"""
Stateless moving-average valuation.

No running balance or valuation rate is ever stored on a Stock Ledger Entry
row. Every balance / rate is derived at query time from the append-only SLE
log using a recursive CTE (MariaDB 10.2+ / MySQL 8+ / Postgres all support
`WITH RECURSIVE`).

Why recursive and not a plain window function:
  qty_after_transaction is a simple running SUM() -> plain window function
  is fine for that part.

  valuation_rate is NOT a plain running average, because an OUTGOING row's
  value contribution is (actual_qty * valuation_rate_of_the_row_before_it),
  not incoming_rate (outgoing rows don't have one). That's a genuine
  row-depends-on-previous-row's-computed-value recursion, which SQL window
  functions can't express in one pass -- hence WITH RECURSIVE.

The whole thing is still exactly one SQL statement per (item_code,
warehouse) -- no application-level loop, no stored/cached running balance.
"""

import frappe

MOVING_AVERAGE_CTE = """
WITH RECURSIVE ledger AS (
    SELECT
        name,
        posting_datetime,
        actual_qty,
        incoming_rate,
        ROW_NUMBER() OVER (ORDER BY posting_datetime, name) AS rn
    FROM `tabStock Ledger Entry`
    WHERE item_code = %(item_code)s
      AND warehouse = %(warehouse)s
      AND is_cancelled = 0
      {date_filter}
),
running AS (
    -- anchor: first row
    SELECT
        name,
        posting_datetime,
        actual_qty,
        rn,
        actual_qty AS qty_after_transaction,
        CASE WHEN actual_qty > 0 THEN incoming_rate ELSE 0 END AS valuation_rate,
        CASE WHEN actual_qty > 0 THEN actual_qty * incoming_rate ELSE 0 END AS stock_value
    FROM ledger
    WHERE rn = 1

    UNION ALL

    -- recursive step: each row's value depends on the PREVIOUS row's
    -- computed running valuation_rate (that's the part that must be
    -- recursive rather than a plain window function)
    SELECT
        l.name,
        l.posting_datetime,
        l.actual_qty,
        l.rn,
        r.qty_after_transaction + l.actual_qty AS qty_after_transaction,
        CASE
            WHEN (r.qty_after_transaction + l.actual_qty) = 0 THEN 0
            WHEN l.actual_qty > 0 THEN
                (r.stock_value + (l.actual_qty * l.incoming_rate))
                / (r.qty_after_transaction + l.actual_qty)
            ELSE
                -- outgoing: value leaves at the PRIOR average rate
                (r.stock_value + (l.actual_qty * r.valuation_rate))
                / (r.qty_after_transaction + l.actual_qty)
        END AS valuation_rate,
        CASE
            WHEN l.actual_qty > 0 THEN r.stock_value + (l.actual_qty * l.incoming_rate)
            ELSE r.stock_value + (l.actual_qty * r.valuation_rate)
        END AS stock_value
    FROM ledger l
    JOIN running r ON l.rn = r.rn + 1
)
SELECT
    name,
    posting_datetime,
    actual_qty,
    qty_after_transaction,
    valuation_rate,
    stock_value
FROM running
ORDER BY posting_datetime, name
"""


def get_stock_ledger(item_code, warehouse, as_of_datetime=None):
    """Returns every SLE row for (item_code, warehouse) with computed
    qty_after_transaction / valuation_rate / stock_value at each row --
    this powers the 'Stock Ledger' report (line-by-line movement)."""
    date_filter = ""
    params = {"item_code": item_code, "warehouse": warehouse}
    if as_of_datetime:
        date_filter = "AND posting_datetime <= %(as_of_datetime)s"
        params["as_of_datetime"] = as_of_datetime

    query = MOVING_AVERAGE_CTE.format(date_filter=date_filter)
    return frappe.db.sql(query, params, as_dict=True)


def get_current_valuation_rate(item_code, warehouse, as_of_datetime=None):
    """Returns just the latest valuation_rate / qty as of a point in time.
    Used by Stock Entry to auto-fetch the rate for Issue / Transfer rows."""
    rows = get_stock_ledger(item_code, warehouse, as_of_datetime)
    if not rows:
        return {"qty": 0, "valuation_rate": 0}
    last = rows[-1]
    return {"qty": last.qty_after_transaction, "valuation_rate": last.valuation_rate}


def get_stock_balance(warehouse_list, as_of_date, item_code=None):
    """Latest SLE per (item_code, warehouse) as of a date, for a set of
    warehouses (used for tree consolidation in the Stock Balance report).
    One query, no per-item Python loop."""
    conditions = ["sle.warehouse IN %(warehouses)s", "sle.is_cancelled = 0",
                  "sle.posting_datetime <= %(as_of_datetime)s"]
    params = {
        "warehouses": tuple(warehouse_list),
        "as_of_datetime": f"{as_of_date} 23:59:59",
    }
    if item_code:
        conditions.append("sle.item_code = %(item_code)s")
        params["item_code"] = item_code

    where_clause = " AND ".join(conditions)

    # Take the latest SLE per (item_code, warehouse); qty_after_transaction /
    # valuation_rate for that latest row already reflects the full running
    # total, so summing across warehouses gives the consolidated balance.
    query = f"""
        WITH RECURSIVE ledger AS (
            SELECT
                item_code, warehouse, name, posting_datetime,
                actual_qty, incoming_rate,
                ROW_NUMBER() OVER (
                    PARTITION BY item_code, warehouse
                    ORDER BY posting_datetime, name
                ) AS rn
            FROM `tabStock Ledger Entry` sle
            WHERE {where_clause}
        ),
        running AS (
            SELECT
                item_code, warehouse, name, posting_datetime, rn,
                actual_qty AS qty_after_transaction,
                CASE WHEN actual_qty > 0 THEN incoming_rate ELSE 0 END AS valuation_rate,
                CASE WHEN actual_qty > 0 THEN actual_qty * incoming_rate ELSE 0 END AS stock_value
            FROM ledger WHERE rn = 1

            UNION ALL

            SELECT
                l.item_code, l.warehouse, l.name, l.posting_datetime, l.rn,
                r.qty_after_transaction + l.actual_qty,
                CASE
                    WHEN (r.qty_after_transaction + l.actual_qty) = 0 THEN 0
                    WHEN l.actual_qty > 0 THEN
                        (r.stock_value + (l.actual_qty * l.incoming_rate))
                        / (r.qty_after_transaction + l.actual_qty)
                    ELSE
                        (r.stock_value + (l.actual_qty * r.valuation_rate))
                        / (r.qty_after_transaction + l.actual_qty)
                END,
                CASE
                    WHEN l.actual_qty > 0 THEN r.stock_value + (l.actual_qty * l.incoming_rate)
                    ELSE r.stock_value + (l.actual_qty * r.valuation_rate)
                END
            FROM ledger l
            JOIN running r
                ON l.item_code = r.item_code
                AND l.warehouse = r.warehouse
                AND l.rn = r.rn + 1
        ),
        latest AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY item_code, warehouse
                    ORDER BY posting_datetime DESC, name DESC
                ) AS latest_rn
            FROM running
        )
        SELECT
            item_code,
            SUM(qty_after_transaction) AS balance_qty,
            SUM(stock_value) AS balance_value
        FROM latest
        WHERE latest_rn = 1 AND qty_after_transaction != 0
        GROUP BY item_code
    """
    return frappe.db.sql(query, params, as_dict=True)