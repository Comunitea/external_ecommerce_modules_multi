# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class WebsiteTheme(models.Model):
    _inherit = "website.theme"

    def _convert_assets(self):
        """
        Generate assets for converted themes.
        Workaround to prevent duplicate views for custom theme by converted_theme_addon
        and let use it at the same time to enable assets in editor web
        """
        Asset = self.env["website.theme.asset"]

        common_refs = self.env["ir.model.data"]

        # add views with customize_show menu, so we can activate them per
        # website independently
        common_refs |= self.env['ir.ui.view']\
                           .with_context(active_test=False)\
                           .search([
                               ('website_id', '=', False),
                               ('customize_show', '=', True),
                           ]).mapped('model_data_id')
        _logger.debug('common_refs: %s', common_refs.mapped('complete_name'))

        for one in self:
            refs = self.env["ir.model.data"]

            # It prevent duplicate views for custom theme by converted_theme_addon
            # and let use it at the same time to enable assets in editor web

            # if one.converted_theme_addon:
            #     # Get all views owned by the converted theme addon
            #     refs |= self.env["ir.model.data"].search([
            #         ("module", "=", one.converted_theme_addon),
            #         ("model", "=", "ir.ui.view"),
            #     ])

            if refs or one.asset_ids:
                # add common_refs only for installed themes
                refs |= common_refs

            views = self.env["ir.ui.view"].with_context(active_test=False) \
                .search([
                    ("id", "in", refs.mapped("res_id")),
                    ("type", "=", "qweb"),
                ])
            existing = frozenset(
                one
                .mapped("asset_ids")
                .filtered("auto")
                .mapped("name")
            )
            expected = frozenset(views.mapped("xml_id"))

            dangling = tuple(existing - expected)
            # Create a new asset for each theme view
            for ref in expected - existing:
                _logger.info("Creating asset %s for theme %s", ref, one.name)
                one.asset_ids |= Asset.new({
                    "name": ref,
                    "auto": True,
                })
            # Delete all dangling assets
            if dangling:
                _logger.info(
                    "Removing dangling assets for theme %s: %s",
                    one.name, dangling)
                Asset.search([("name", "in", dangling)]).unlink()
        # Turn all assets multiwebsite-only
        Asset._find_and_deactivate_views()


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
                _logger.info("MULTI_COMPANY_BASE - FOUND VIEW with name: %s - view_id: %s - key: %s",
                             one.name, one.view_id.id, one.view_id.key)
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
                        _logger.info(
                            "MULTI_COMPANY_BASE - ACTIVATING THEME ASSETS VIEW with name: %s - view_id: %s - key: %s",
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
