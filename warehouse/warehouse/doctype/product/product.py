# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, nowtime
from frappe.website.website_generator import WebsiteGenerator

from warehouse.warehouse.doctype.stock_ledger_entry.stock_ledger_entry import (
    make_sl_entry,
)


class Product(WebsiteGenerator):

    def validate(self):
        super().validate()
        self.check_for_quantity_and_rate()

    def after_insert(self):
        frappe.enqueue(
            "warehouse.warehouse.doctype.product.product.make_stock_ledger_entry",
            product_name=self.name,
            enqueue_after_commit=True,
            queue="short",
        )

    def check_for_quantity_and_rate(self):
        if self.quantity and not self.standard_rate:
            frappe.throw("Please Enter the Standard Rate Amount")

def make_stock_ledger_entry(product_name):
    product = frappe.get_doc("Product", product_name)
    print("the product is ", product)

    make_sl_entry(
        posting_date=nowdate(),
        posting_time=nowtime(),
        warehouse=product.warehouse,
        actual_qty=product.quantity,
        incoming_rate=product.standard_rate,
        item_code=product.name,
        voucher_type="Product",
        voucher_no=product.name,
        voucher_detail_no=product.name,
    )