
# Copyright (c) 2026, simon muturi and contributors
# For license information, see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Product",
            "width": 180,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 180,
        },
        {
            "label": _("Quantity"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("date"):
        conditions.append("sle.posting_date <= %(date)s")
        values["date"] = filters["date"]

    if filters.get("item_code"):
        conditions.append("sle.item_code = %(item_code)s")
        values["item_code"] = filters["item_code"]

    if filters.get("warehouse"):
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = filters["warehouse"]

    conditions.append("sle.is_cancelled = 0")

    where = " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            sle.item_code,
            sle.warehouse,
            SUM(sle.actual_qty) AS qty
        FROM `tabStock Ledger Entry` sle
        WHERE {where}
        GROUP BY
            sle.item_code,
            sle.warehouse
        HAVING SUM(sle.actual_qty) != 0
        ORDER BY
            sle.item_code,
            sle.warehouse
        """,
        values,
        as_dict=True,
    )

    return data