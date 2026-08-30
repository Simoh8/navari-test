# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
WAREHOUSE_RULES = {
    "Material Receipt": {"from_warehouse": "forbidden", "to_warehouse": "required"},
    "Material Issue": {"from_warehouse": "required", "to_warehouse": "forbidden"},
    "Material Transfer": {"from_warehouse": "required", "to_warehouse": "required"},
}

class StockEntry(Document):
	pass
