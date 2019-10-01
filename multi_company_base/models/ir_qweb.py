# -*- coding: utf-8 -*-

from odoo import models, tools
from odoo.http import request

from odoo.addons.base.ir.ir_qweb.qweb import QWeb


class IrQWeb(models.AbstractModel, QWeb):
    """ Base QWeb rendering engine
    * to customize ``t-field`` rendering, subclass ``ir.qweb.field`` and
      create new models called :samp:`ir.qweb.field.{widget}`
    Beware that if you need extensions or alterations which could be
    incompatible with other subsystems, you should create a local object
    inheriting from ``ir.qweb`` and customize that.
    """

    _inherit = 'ir.qweb'

    @tools.ormcache_context('xmlid', 'options.get("lang", "en_US")', keys=("website_id",))
    def _get_asset_content(self, xmlid, options):
        """
        Workaround to include hook and only load theme assets for current website.
        """
        files = super(IrQWeb, self)._get_asset_content(xmlid=xmlid, options=options)
        new_files = []
        if 'assets_frontend' in xmlid or 'auto_assets_website' in xmlid:
            for file in files:
                for f in file:
                    if 'theme_' in f['url'] and 'website' in dir(request):
                        theme_id = request.website.multi_theme_id.converted_theme_addon
                        if theme_id and theme_id in f['url']:
                            new_files.append(f)
                    else:
                        new_files.append(f)
            return new_files, []
        return files
