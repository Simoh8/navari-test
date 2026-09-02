# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, nowtime
from frappe.website.website_generator import WebsiteGenerator
from warehouse.warehouse.doctype.stock_ledger_entry.stock_ledger_entry import make_sl_entry


class Product(WebsiteGenerator):

    def validate(self):
        super().validate()
        self.check_for_quantity_and_rate()
        make_stock_ledger_entry(self)
        
        change_submit_state(self)
        



    def check_for_quantity_and_rate(self):
        if self.quantity and not self.standard_rate:
            frappe.throw("Please Enter the Standard Rate Amount")

    pass




def change_submit_state(self):
    self.is_submitted=1 

def make_stock_ledger_entry(self):
    if self.is_submitted :
        return
    elif self.quantity ==0:
        return
    else:
        make_sl_entry(
            posting_date=nowdate(),
            posting_time=nowtime(),
            item_code=self.product_code,
            warehouse=self.warehouse,
            actual_qty=self.quantity,
            incoming_rate=self.standard_rate,
            voucher_type="Product",
            voucher_no=None,
            voucher_detail_no=None
        )
