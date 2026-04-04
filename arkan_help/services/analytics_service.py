# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
Arkan Help — AnalyticsService
Track help page views, search queries, feedback.
"""

import frappe
from frappe import _


class AnalyticsService:
    """Track help page views, search queries, feedback."""

    @staticmethod
    def get_list(**filters):
        """Return filtered list of records."""
        raise NotImplementedError

    @staticmethod
    def get_detail(name: str) -> dict:
        """Return single record detail."""
        raise NotImplementedError

    @staticmethod
    def create(**kwargs) -> str:
        """Create new record. Returns document name."""
        raise NotImplementedError

    @staticmethod
    def update(name: str, **kwargs) -> None:
        """Update existing record."""
        raise NotImplementedError
