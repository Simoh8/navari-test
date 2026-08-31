# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet



class Warehouse(NestedSet):

	def validate (self):
		pass







def get_descendant_warehouses(warehouse):
		"""Used by Stock Balance report for tree consolidation.
		Returns all leaf + group descendants (inclusive) using lft/rgt."""
		lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
		return frappe.db.sql(
			"""
			SELECT name FROM `tabWarehouse`
			WHERE lft >= %s AND rgt <= %s
			""",
			(lft, rgt),
			as_dict=False,
		)



