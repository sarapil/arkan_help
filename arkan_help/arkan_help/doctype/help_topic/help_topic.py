# Copyright (c) 2026, Arkan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HelpTopic(Document):
	def validate(self):
		if self.topic_key:
			self.topic_key = self.topic_key.strip().lower().replace(" ", "_")
