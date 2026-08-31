
# Copyright (c) 2026, simon muturi and contributors
# For license information, see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(filters)

    return columns, data, None, chart


def get_columns():
    return [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Product",
            "width": 200,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
        {
            "label": _("Quantity"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 200,
        },
    ]


def get_chart(filters):
    conditions = []
    values = {}

    if filters.get("date"):
        conditions.append("posting_date <= %(date)s")
        values["date"] = filters["date"]

    if filters.get("item_code"):
        conditions.append("item_code = %(item_code)s")
        values["item_code"] = filters["item_code"]

    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = filters["warehouse"]

    conditions.append("is_cancelled = 0")

    where = " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            warehouse,
            SUM(actual_qty) AS qty
        FROM `tabStock Ledger Entry`
        WHERE {where}
        GROUP BY warehouse
        HAVING SUM(actual_qty) != 0
        ORDER BY qty DESC
        """,
        values,
        as_dict=True,
    )

    return {
        "data": {
            "labels": [row.warehouse for row in data],
            "datasets": [
                {
                    "name": _("Stock"),
                    "values": [row.qty for row in data],
                }
            ],
        },
        "type": "bar",
        "colors": ["#2490EF"],
        "axisOptions": {
            "xAxisMode": "tick",
            "xIsSeries": True,
        },
        "barOptions": {
            "spaceRatio": 0.5,
        },
    }


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
