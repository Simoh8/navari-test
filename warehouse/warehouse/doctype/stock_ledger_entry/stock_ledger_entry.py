# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import datetime, get_datetime
from frappe.model.document import Document


class StockLedgerEntry(Document):


	def on_trash(self):
		frappe.throw("You cannot Cancel a Sales Ledger Entry")

def make_sl_entry(posting_date,posting_time,item_code,warehouse,voucher_type,voucher_no,	actual_qty,incoming_rate,voucher_detail_no):
		frappe.flags.via_stock_entry=True

		try:
			sle= frappe.get_doc(
				{
					"doctype":"Stock Entry",
					"posting_date":posting_date,
					"posting_time":posting_time,
					"item_code":item_code,
					"warehouse":warehouse,
					"actual_qty":actual_qty,
					"incoming_rate":incoming_rate,
					"voucher_type":voucher_type,
					"voucher_no":voucher_no,
					"voucher_detail_no":voucher_detail_no




				}
			)
			sle.insert(ignore_permissions=True)
			return sle

		finally :
			frappe.flags.via_stock_entry=False








	
