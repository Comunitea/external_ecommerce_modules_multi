# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_signup_url(self):
        """
            Proxy for function field towards actual implementation.

            Workaround to pass 'website_id' in context for get_param('web.base.url') and retrieve the correct base_url.
            Used in reset_password and portal_wizard.
        """
        for partner in self:
            if not partner.user_ids:
                continue
            result = partner.sudo().with_context(
                website_id=partner.user_ids[0].backend_website_id.id)._get_signup_url_for_action()
            if any(u.has_group('base.group_user') for u in partner.user_ids if u != self.env.user):
                self.env['res.users'].check_access_rights('write')
            partner.signup_url = result.get(partner.id, False)
