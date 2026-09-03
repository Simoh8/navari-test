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

        document = frappe.get_doc({
            "doctype": "Product",
            "product_name": "Product Test",
            "product_uom": "UOM",
            "is_published": 1


        })
        document.insert()
        self.assertEqual(
            document.route, "products/product-test"

        )

    def test_product_amount_and_rate(self):
        document = frappe.get_doc({
            "doctype": "Product",
            "product_name": "test_128665",
            "item_code": "GEWRNFERFMER",
            "product_uom": "Box",
            "warehouse":"Showroom Store 1"

        })

        document.insert()
        self.assertEqual(
            document.product_uom, "Box"

        )
