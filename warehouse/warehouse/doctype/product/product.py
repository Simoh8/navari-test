# Copyright (c) 2026, simon muturi and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class Product(WebsiteGenerator):

	def validate(self):
		super().validate()
		self.check_for_quantity_and_rate()

	def check_for_quantity_and_rate(self):
		if self.quantity and not self.standard_rate:
			frappe.throw("Please Enter the Standard Rate Amount")

	pass