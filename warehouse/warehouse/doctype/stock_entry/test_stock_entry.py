# Copyright (c) 2026, simon muturi and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime
# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

# Copyright (c) 2026, simon muturi and contributors

# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

class IntegrationTestStockEntry(FrappeTestCase):

	@classmethod
	def setUpClass(cls):
		super().setUpClass()

		cls.uom = frappe.get_doc({
			"doctype": "Stock UOM",
			"uom_name": "_Test UOM",
		}).insert(ignore_if_duplicate=True)

		cls.product = frappe.get_doc({
			"doctype": "Product",
			"product_name": "_Test Product",
			"product_uom": "_Test UOM",
		}).insert(ignore_if_duplicate=True)

		cls.warehouse = frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": "_Test Warehouse",
		}).insert(ignore_if_duplicate=True)

	def test_material_receipt(self):
		stock_entry = frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"posting_date": now_datetime().date(),
			"posting_time": now_datetime(),
			"target_warehouse": self.warehouse.name,
			"product_details": [
				{
					"item_code": self.product.name,
					"quantity": 10,
					"basic_rate": 100,
					"target_warehouse": self.warehouse.name,
				}
			],
		})

		stock_entry.insert()
		stock_entry.submit()

		actual_qty = frappe.db.get_value(
			"Stock Ledger Entry",
			{"voucher_no": stock_entry.name},
			"actual_qty",
		)

		self.assertEqual(actual_qty, 10)

	def test_material_issue(self):
		stock_entry = frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Issue",
			"posting_date": now_datetime().date(),
			"posting_time": now_datetime(),
			"source_warehouse": self.warehouse.name,
			"product_details": [
				{
					"item_code": self.product.name,
					"quantity": 5,
					"basic_rate": 100,
					"source_warehouse": self.warehouse.name,
				}
			],
		})

		stock_entry.insert()
		stock_entry.submit()

		actual_qty = frappe.db.get_value(
			"Stock Ledger Entry",
			{"voucher_no": stock_entry.name},
			"actual_qty",
		)

		self.assertEqual(actual_qty, -5)
