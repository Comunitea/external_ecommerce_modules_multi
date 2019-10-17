# -*- coding: utf-8 -*-

import logging
import werkzeug

from odoo import http, _

from odoo.http import request
from odoo.exceptions import UserError

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class AuthSignupHomeCustom(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        """
        Workaround to receive uid on signup and search a user by that uid
        because in multi website system we can find more than one same user login used in others website.
        """
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                uid = self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    # Before
                    # user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    # Now
                    user_sudo = request.env['res.users'].sudo().search([('id', '=', uid)])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                _logger.error("%s", e)
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def get_auth_signup_qcontext(self):
        """
            Shared helper returning the rendering context for signup and reset password.
            Workaround to include backend_website_id in context
        """
        qcontext = request.params.copy()
        qcontext.update({
            'backend_website_id': request.env['website'].get_current_website().id
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
        """
            Shared helper that creates a res.partner out of a token.
            Include website_id for signup only on this website.

            Workaround to include backend_website_id in context and return a user id.
         """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'backend_website_id')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        uid = self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
        return uid

    def _signup_with_values(self, token, values):
        """
        Workaround to include backend_website_id in backend_website_ids by context and return a user id.
        """
        values.update({
            'backend_website_ids': [(4, values['backend_website_id'])],
        })
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        # as authenticate will use its own cursor we need to commit the current transaction
        request.env.cr.commit()
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))
        return uid

