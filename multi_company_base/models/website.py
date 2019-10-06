# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models
from odoo.tools import config


MODULE = "website_multi_theme"
LAYOUT_KEY = MODULE + ".auto_layout_website_%s"
ASSETS_KEY = MODULE + ".auto_assets_website_%s"
VIEW_KEY = MODULE + ".auto_view_%s_%s"
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    @api.multi
    def _duplicate_view_for_website(self, pattern, xmlid, override_key):
        """
        Duplicate a view pattern and enable it only for current website.

        Workaround to overwrite the ir.model.data with noupdate=False to make possible keep active
        the desired customize views what and avoid they will be deactivated in website_multi_theme module update.

        :param ir.ui.view pattern:
            Original view that will be copied for current website.

        :param str xmlid:
            The XML ID of the generated record.

        :param bool override_key:
            Indicates wether the view key should be overriden. If ``True``,
            it will become the same as :param:`xmlid`. Otherwise, the key will
            be copied from :param:`pattern` as it would happen normally.

        :return ir.ui.view:
            The duplicated view.
        """
        self.ensure_one()
        # Return the pre-existing copy if any or delete if is a copy of custom theme views
        # Do not duplicated custom theme views no duplicated by default
        duplicate = True
        theme = self.multi_theme_id.converted_theme_addon
        try:
            result = self.env.ref(xmlid)
        except ValueError:
            pass
        else:
            # If we develop and want xml reloading, update view arch always
            if "xml" in config.get("dev_mode"):
                result.arch = pattern.arch
            if pattern.key and theme and theme in pattern.key and not pattern.inherit_id:
                _logger.debug("DELETED COPIED VIEW for %s: %s", result.display_name, result.display_name)
                result.unlink()
                return
            else:
                return result
        # Copy patterns only for current website
        _logger.debug("PATTERN.KEY %s: %s", pattern.display_name, pattern.key)
        if pattern.key and theme and theme in pattern.key and not pattern.inherit_id:
            duplicate = False
            _logger.info("NO DUPLICATED CUSTOM VIEW for %s: %s", pattern.display_name, pattern.key)

        if duplicate:
            key = xmlid if override_key else pattern.key
            result = pattern.copy({
                "active": pattern.was_active,
                "arch_fs": False,
                "key": key,
                "name": '%s (Website #%s)' % (pattern.name, self.id),
                "website_id": self.id,
                "origin_view_id": pattern.id,
            })
            # Assign external IDs to new views
            module, name = xmlid.split(".")
            self.env["ir.model.data"].with_context(
                duplicate_view_for_website=True
            ).create({
                "model": result._name,
                "module": module,
                "name": name,
                "noupdate": False,  # This is the only change
                "res_id": result.id,
            })
            _logger.debug(
                "Duplicated %s as %s with xmlid %s for %s with arch:\n%s",
                pattern.display_name,
                result.display_name,
                xmlid,
                self.display_name,
                result.arch,
            )
            return result

    @api.multi
    def _find_duplicated_view_for_website(self, origin_view):
        """
        Workaround to modifies inherit method to find duplicates views but by origin_view.key instead of origin_view.id.
        :param origin_view: Now is a string not an integer
        :return: xmlid
        """
        self.ensure_one()
        xmlid = VIEW_KEY % (self.name[:3].strip().lower(), origin_view)
        return self.env.ref(xmlid, raise_if_not_found=False)

    def _multi_theme_activate(self):
        """
        Modifies inherit method to activate current multi theme for current websites
        but by origin_view.key instead of origin_view.id.
        This is necessary for how know to refer to inherit templates and avoid update problems
        who activate auto generated views and hide customatedes inherit templates.
        """
        main_assets_frontend = (
            self.env.ref("web.assets_frontend") |
            self.env.ref("website.assets_frontend"))
        main_layout = self.env.ref("website.layout")
        main_views = main_assets_frontend | main_layout
        # Patterns that will be duplicated to enable multi themes
        assets_pattern = self.env.ref("website_multi_theme.assets_pattern")
        layout_pattern = self.env.ref("website_multi_theme.layout_pattern")
        for website in self:
            if not website.multi_theme_id:
                default_theme = self.env.ref(
                    'website_multi_theme.theme_default',
                    raise_if_not_found=False,
                )
                if not default_theme:
                    _logger.info("Deleting multi website theme views for %s: %s",
                                 website.display_name,
                                 website.multi_theme_view_ids,
                    )
                    website.multi_theme_view_ids.unlink()
                    continue
                else:
                    website.multi_theme_id = default_theme

            # Duplicate multi theme patterns for this website
            custom_assets = website._duplicate_view_for_website(
                assets_pattern,
                ASSETS_KEY % website.name[0:3].strip().lower(),
                True
            )
            custom_layout = website._duplicate_view_for_website(
                layout_pattern,
                LAYOUT_KEY % website.name[0:3].strip().lower(),
                True
            )
            # Update custom base views arch to latest pattern
            custom_assets.arch = assets_pattern.arch
            custom_layout.arch = layout_pattern.arch.format(
                theme_view=custom_assets.key,
            )
            # These custom base views must be active
            custom_views = custom_assets | custom_layout
            custom_views.update({
                "active": True,
            })

            _logger.debug("ASSETS MAPPED BY VIEW_ID: %s", website.multi_theme_id.get_assets().mapped("view_id"))
            # Duplicate all theme's views for this website
            for origin_view in website.multi_theme_id.get_assets().mapped("view_id"):
                _logger.debug("TRYING COPY VIEW for %s - %s", origin_view.name, origin_view.key, )
                copied_view = website._duplicate_view_for_website(
                    origin_view,
                    VIEW_KEY % (website.name[0:3].strip().lower(), origin_view.key.replace('.', '_')),
                    False
                )
                # Do not duplicated custom theme views no duplicated by default
                if copied_view:
                    _logger.debug("COPIED VIEW for %s - %s", copied_view.name, copied_view.key,)
                    # Applied views must inherit from custom assets or layout
                    new_parent = None
                    if copied_view.inherit_id & main_views:
                        if copied_view.inherit_id & main_assets_frontend:
                            new_parent = custom_assets
                        elif copied_view.inherit_id & main_layout:
                            new_parent = custom_layout
                    else:
                        parent_view = copied_view.inherit_id

                        if parent_view and parent_view.key:
                            parent_view = parent_view.key.replace('.', '_')

                        # check if parent was copied, so we need inherit that
                        # instead of original parent, which is deactivated and not used
                        copied_parent = website._find_duplicated_view_for_website(
                            parent_view
                        )

                        if copied_parent:
                            new_parent = copied_parent

                    if new_parent:
                        copied_view._replace_parent(new_parent)

                    _logger.debug("REPLACE PARENT VIEW for %s with: %s", copied_view.key, copied_view.inherit_id.key,)

                    custom_views |= copied_view
            # Delete any custom view that should exist no more
            views_to_remove = website.multi_theme_view_ids - custom_views
            # Removed views could be a copied parent for others
            # So, replace to original parent first
            views_to_replace_parent = self.env['ir.ui.view'].with_context(active_test=False).search([
                ('inherit_id', 'in', views_to_remove.ids)
            ])
            for view in views_to_replace_parent:
                view._replace_parent(view.inherit_id.origin_view_id)
            views_to_remove.unlink()
            _logger.info("Updated multi website theme views for %s: %s",
                         website.display_name, website.multi_theme_view_ids,)
