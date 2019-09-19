# -*- coding: utf-8 -*-

from odoo import api, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def get_related_views(self, key, bundles=False):
        """This method is used to prepare items
           in 'Customize' menu of website Editor"""
        views = super(IrUiView, self).get_related_views(
            key, bundles=bundles
        )

        if bundles is True:
            views = views.filtered(lambda v: v.active is True)

        return views
