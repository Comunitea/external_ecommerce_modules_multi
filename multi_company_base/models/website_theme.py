# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class WebsiteThemeAsset(models.Model):
    _inherit = "website.theme.asset"

    @api.model
    def _find_and_deactivate_views(self):
        """
        Find available views and make them multiwebsite-only.

        Add a hook for theme assets will be charged in web editor.
        """
        linkable = self.search(["|", ("view_id", "=", False), ("view_id.active", "=", True), ])
        for one in linkable:
            try:
                one.view_id = self.env.ref(one.name)
                _logger.debug("Found view with ref %s: %r", one.name, one.view_id,)
            except ValueError:
                one.view_id = False
                _logger.info("Ref not found: %s", one.name)
            else:
                if one.view_id.active:
                    active = False
                    was_active = True
                    if 'website_assets_frontend' in one.view_id.key:
                        active = True
                        was_active = False
                    _logger.info("MULTI_COMPANY_BASE: Deactivating view %s", one.name)
                    # Disable it and set it to be enabled in multi theme mode
                    # Except for theme assets. To be charged in web editor
                    one.view_id.write({
                        # Now
                        "active": active,
                        "was_active": was_active,
                        # Before
                        # "active": False,
                        # "was_active": True,
                    })
        # Clean Qweb cache
        IrQweb = self.env["ir.qweb"]
        IrQweb._get_asset_content.clear_cache(IrQweb)
