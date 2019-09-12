# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):

    _inherit = 'res.users'

    backend_website_ids = fields.Many2many(
        'website',
        'website_user_rel',
        'website_id',
        'user_id',
        string=_('Allowed Backend Websites'),
        help=_('Only websites presents let user get portal access'),
        compute=False,
    )

    @api.model
    def create(self, vals):
        """
            Do not want fill this field for all websites. Just current website.
        """
        user = super(ResUsers, self).create(vals)
        if 'website_id' in vals and vals['website_id'] not in user.backend_website_ids:
            user.backend_website_ids = [(4, vals['website_id'].id)]
        return user

    @api.depends('backend_website_ids')
    def _compute_backend_website_ids(self):
        """
            Do not want compute this field. Must be filled in by context or direct user action and have to be editable.
        """
        for user in self:
            user.backend_websites_count = len(user.backend_website_ids)
