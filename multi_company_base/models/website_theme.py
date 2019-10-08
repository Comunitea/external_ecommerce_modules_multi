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
        linkable = self.search(["|", "|", ("view_id", "=", False),
                                ("view_id.active", "=", True),
                                ("view_id.active", "=", False)
                                ])
        for one in linkable:
            try:
                one.view_id = self.env.ref(one.name)
                _logger.debug("FOUND VIEW with name: %s - view_id: %s - key: %s",
                              one.name, one.view_id.id, one.view_id.key)
            except ValueError:
                one.view_id = False
                _logger.debug("Ref not found: %s", one.name)
            else:
                theme = one.theme_id.converted_theme_addon
                if one.view_id.active or (theme and theme in one.view_id.key and not one.view_id.active
                                          and not one.view_id.inherit_id):
                    active = False
                    was_active = True
                    if 'website_assets_frontend' in one.view_id.key or (theme and theme in one.view_id.key
                                                                        and not one.view_id.inherit_id):
                        active = True
                        was_active = False
                        _logger.info("ACTIVATE VIEW with name: %s - view_id: %s - key: %s",
                                     one.name, one.view_id.id, one.view_id.key)
                    else:
                        _logger.info("DEACTIVATE VIEW with name: %s - view_id: %s - key: %s",
                                     one.name, one.view_id.id, one.view_id.key)
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
