# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from warehouse.warehouse.doctype.stock_ledger_entry.stock_ledger_entry import make_sl_entry
WAREHOUSE_RULES = {
    "Material Receipt": {"from_warehouse": "forbidden", "to_warehouse": "required"},
    "Material Issue": {"from_warehouse": "required", "to_warehouse": "forbidden"},
    "Material Transfer": {"from_warehouse": "required", "to_warehouse": "required"},
}

class StockEntry(Document):



    def validate(self):
        # super().validate()

        self.get_stock_entry_items()


    def on_submit(self):
        for row in self.product_details:
            if self.stock_entry_type=="Material Receipt":
                make_sl_entry(
                    self.posting_date,
                    # row.item_code, 
                    self.posting_time,
                    item_code= row.item_code,
                    warehouse=row.target_warehouse,
                    actual_qty=row.quantity,
                    incoming_rate=row.basic_rate,
                    voucher_type="Stock Entry",
                    voucher_no=self.name,
                    voucher_detail_no=row.name



                )
            elif self.stock_entry_type =="Material Issue":
                make_sl_entry(
                    self.posting_date,
                    self.posting_time,
                    item_code=row.item_code,
                    warehouse=row.source_warehouse,
                    actual_qty=-row.quantity,
                    incoming_rate=row.basic_rate,
                    voucher_type="Stock Entry",
                    voucher_no=self.name,
                    voucher_detail_no=row.name
                    )
                
            else:
                make_sl_entry(
                    self.posting_date,
                    self.posting_time,
                    item_code=row.item_code,
                    warehouse=row.source_warehouse,
                    actual_qty=-row.quantity,
                    incoming_rate=None,
                    voucher_type="Stock Entry",
                    voucher_no=self.name,
                    voucher_detail_no=row.name

                )
    
    








    def get_stock_entry_items(self):
        for row in self.product_details:
            pass


    def on_cancel(self):
        self.is_cancelled=1
    
    
    
    

