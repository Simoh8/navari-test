# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

"""
Stateless moving-average valuation.

No running balance or valuation rate is ever stored on a Stock Ledger Entry
row -- it's derived at query time from the append-only, submittable SLE log
using a recursive CTE. Only docstatus == 1 (submitted, not cancelled) rows
count.
"""

import frappe

MOVING_AVERAGE_CTE = """
WITH RECURSIVE ledger AS (
    SELECT
        name,
        posting_date_and_time,
        actual_qty,
        incoming_rate,
        ROW_NUMBER() OVER (ORDER BY posting_date_and_time, name) AS rn
    FROM `tabStock Ledger Entry`
    WHERE item_code = %(item_code)s
      AND warehouse = %(warehouse)s
      AND docstatus = 1
      {date_filter}
),
running AS (
    SELECT
        name, posting_date_and_time, actual_qty, rn,
        actual_qty AS qty_after_transaction,
        CASE WHEN actual_qty > 0 THEN incoming_rate ELSE 0 END AS valuation_rate,
        CASE WHEN actual_qty > 0 THEN actual_qty * incoming_rate ELSE 0 END AS stock_value
    FROM ledger
    WHERE rn = 1

    UNION ALL

    SELECT
        l.name, l.posting_date_and_time, l.actual_qty, l.rn,
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
    JOIN running r ON l.rn = r.rn + 1
)
SELECT name, posting_date_and_time, actual_qty, qty_after_transaction, valuation_rate, stock_value
FROM running
ORDER BY posting_date_and_time, name
"""


def get_stock_ledger(item_code, warehouse, as_of_datetime=None):
    date_filter = ""
    params = {"item_code": item_code, "warehouse": warehouse}
    if as_of_datetime:
        date_filter = "AND posting_date_and_time <= %(as_of_datetime)s"
        params["as_of_datetime"] = as_of_datetime

    query = MOVING_AVERAGE_CTE.format(date_filter=date_filter)
    return frappe.db.sql(query, params, as_dict=True)


def get_current_valuation_rate(item_code, warehouse, as_of_datetime=None):
    """Returns the latest {qty, valuation_rate} as of a point in time.
    Used by Stock Entry to auto-fetch the rate for Issue / Transfer rows."""
    rows = get_stock_ledger(item_code, warehouse, as_of_datetime)
    if not rows:
        return {"qty": 0, "valuation_rate": 0}
    last = rows[-1]
    return {"qty": last.qty_after_transaction, "valuation_rate": last.valuation_rate}