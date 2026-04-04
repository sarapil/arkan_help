# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HelpContent(Document):
	def validate(self):
		self.validate_unique_topic_language()

	def validate_unique_topic_language(self):
		"""Ensure only one content entry per topic + language combination."""
		if not self.topic or not self.language:
			return

		existing = frappe.db.exists(
			"Help Content",
			{
				"topic": self.topic,
				"language": self.language,
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				frappe._("Help Content for topic {0} in language {1} already exists: {2}").format(
					self.topic, self.language, existing
				),
				frappe.DuplicateEntryError,
			)
