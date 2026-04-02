"""
Arkan Help — Permission Tests
Role-based access control and CAPS capability tests.
"""

import frappe
from frappe.tests import IntegrationTestCase


class TestAHPermissions(IntegrationTestCase):
    """Permission and CAPS capability tests for Arkan Help."""

    def test_guest_cannot_access(self):
        """Guest users cannot access protected endpoints."""
        pass  # TODO: Implement
