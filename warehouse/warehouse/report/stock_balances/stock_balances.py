import frappe
from warehouse.warehouse.doctype.warehouse.warehouse import (
    get_descendant_warehouses,
)
from warehouse.utils.utils import get_stock_balance


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": 120},
        {"label": "Balance Value", "fieldname": "balance_value", "fieldtype": "Currency", "width": 140},
        {"label": "Avg. Valuation Rate", "fieldname": "avg_rate", "fieldtype": "Currency", "width": 140},
    ]

def get_data(filters):
    filters = filters or {}

    warehouses = frappe.get_all(
        "Warehouse",
        fields=["name"],
        ignore_permissions=True
    )

    as_of_date = filters.get("date") or frappe.utils.nowdate()

    if not warehouses:
        frappe.throw("No warehouses found")

    warehouse_names = [w.name for w in warehouses]

    rows = get_stock_balance(
        warehouse_names,
        as_of_date,
        item_code=filters.get("item_code")
    )

    for row in rows:
        row["avg_rate"] = (
            row["balance_value"] / row["balance_qty"]
            if row["balance_qty"]
            else 0
        )

    return rows