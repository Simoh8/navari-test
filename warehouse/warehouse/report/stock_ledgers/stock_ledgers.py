# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

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
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Posting Time"),
            "fieldname": "posting_time",
            "fieldtype": "Time",
            "width": 90,
        },
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Product",
            "width": 150,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 120,
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 150,
        },
        {
            "label": _("Qty"),
            "fieldname": "actual_qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Rate"),
            "fieldname": "incoming_rate",
            "fieldtype": "Currency",
            "width": 100,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append("sle.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("sle.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    if filters.get("item_code"):
        conditions.append("sle.item_code = %(item_code)s")
        values["item_code"] = filters["item_code"]

    if filters.get("warehouse"):
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = filters["warehouse"]

    conditions.append("sle.is_cancelled = 0")

    where = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            sle.posting_date,
            sle.posting_time,
            sle.item_code,
            sle.warehouse,
            sle.voucher_type,
            sle.voucher_no,
            sle.actual_qty,
            sle.incoming_rate
        FROM `tabStock Ledger Entry` sle
        WHERE {where}
        ORDER BY
            sle.posting_date,
            sle.posting_time,
            sle.creation
        """,
        values,
        as_dict=True,
    )
