import frappe
from warehouse.utils.utils import get_stock_ledger


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Posting Date/Time", "fieldname": "posting_datetime", "fieldtype": "Datetime", "width": 160},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 110},
        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 140},
        {"label": "Actual Qty", "fieldname": "actual_qty", "fieldtype": "Float", "width": 100},
        {"label": "Balance Qty", "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 100},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    item_code = filters.get("item_code")
    warehouse = filters.get("warehouse")

    rows = get_stock_ledger(item_code, warehouse, filters.get("to_date"))

    # Voucher metadata joined in Python (kept out of the CTE for readability)
    for row in rows:
        sle = frappe.db.get_value(
            "Stock Ledger Entry", row.name,
            ["voucher_type", "voucher_no"], as_dict=True
        )
        row.update(sle)
        row["item_code"] = item_code
        row["warehouse"] = warehouse

    if filters.get("from_date"):
        rows = [r for r in rows if str(r.posting_datetime) >= str(filters["from_date"])]

    return rows