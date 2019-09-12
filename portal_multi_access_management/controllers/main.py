# -*- coding: utf-8 -*-

from odoo import http, _

from odoo.http import request
from odoo.exceptions import UserError

from odoo.addons.website.controllers.main import Website

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class WebsiteCustom(Website):

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        """
        The portal users only have access granted for allowed websites in settings
        otherwise an error message is showed on login view.
        """
        login = request.params.get('login', False)
        user = request.env['res.users'].sudo().search([('login', '=', login)])
        if login and user:
            current_website = request.env['website'].get_current_website()
            if current_website not in user.backend_website_ids:
                values = request.params.copy()
                if user.has_group('base.group_user'):
                    values['error'] = _("Your user do not have access granted for this website. "
                                        "Please, contact with administrator.")
                else:
                    values['error'] = _("Your user do not have access granted for this website. "
                                        "Please, contact us to get granted access.")
                return request.render('web.login', values)

        return super(Website, self).web_login(redirect=redirect, *args, **kw)


class AuthSignupHomeCustom(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password.
            Include website_id for signup only on this website.
        """
        qcontext = request.params.copy()
        current_website = request.env['website'].get_current_website()
        qcontext.update({
            'website_id': current_website
        })
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token.
            Include website_id for signup only on this website.
         """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'website_id')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
