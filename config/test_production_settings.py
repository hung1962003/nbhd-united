"""Regression pins for production settings safety."""

from django.test import SimpleTestCase


class ProductionSettingsSafetyTests(SimpleTestCase):
    def test_production_debug_is_false(self):
        """DEBUG-gated routes must stay off in production settings."""
        from config.settings import production

        self.assertIs(production.DEBUG, False)
