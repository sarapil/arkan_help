# Copyright (c) 2026, Arkan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HelpSettings(Document):
	def validate(self):
		if self.cache_ttl and self.cache_ttl < 0:
			frappe.throw(frappe._("Cache TTL cannot be negative"))
