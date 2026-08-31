# Copyright (c) 2026, simon muturi and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestProduct(IntegrationTestCase):
	"""
	Integration tests for Product.
	Use this class for testing interactions between multiple components.
	"""

	def test_item_route(self):

		document=frappe.get_doc({
			"doctype":"Product",
			"product_name":"Product Test",
			"product_uom": "UOM",
			"is_published":1


		})
		document.insert()
		self.assertEqual(
			document.route,"products/product-test"
			
		)



		
