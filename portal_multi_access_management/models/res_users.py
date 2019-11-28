# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, SUPERUSER_ID, _

from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError

from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'

    backend_website_ids = fields.Many2many(
        'website',
        'website_user_rel',
        'user_id',
        'website_id',
        string=_('Allowed Backend Websites'),
        help=_('Only websites presents let user get portal access'),
        compute=False,
    )

    @api.model_cr
    def init(self):
        """
            Workaround in login because now is not unique and is allowed same login in a different website.
        """
        super(ResUsers, self).init()
        self._cr.execute("select 1 from information_schema.constraint_column_usage where table_name = 'res_users' "
                         "and constraint_name = 'res_users_login_key'")
        if self._cr.rowcount:
            # DROP CONSTRAINT unconditionally takes an ACCESS EXCLUSIVE lock
            # on the table, even "IF EXISTS" is set and not matching; disabling
            # the relevant trigger instead acquires SHARE ROW EXCLUSIVE, which
            # still conflicts with the ROW EXCLUSIVE needed for an insert
            self._cr.execute("ALTER TABLE res_users DROP CONSTRAINT res_users_login_key")

    @api.constrains('id', 'backend_website_ids')
    def _check_user_website(self):
        """
        Check user must be unique for each website
        """
        if self.search_count([('backend_website_ids', 'in', self.backend_website_id.id), ('id', '=', self.id)]) > 1:
            raise ValidationError(_("Another user is already registered in the same website!"))

    @api.model
    def create(self, vals):
        """
            Workaround to fill backend_website_ids just for current website.
        """
        user = super(ResUsers, self).create(vals)
        if 'backend_website_id' in vals:
            # Add current_website to allowed websites
            user.backend_website_ids = [(4, vals['backend_website_id'])]
        return user

    def write(self, vals):
        """
            Workaround to control allowed websites in backend user menu for multi website system
            because it is possible use the same user with the same login in different websites
            or different users with the same login in diferents websites as well
            but It is not possible to use different users with the same login on the same website.
        """
        res = super().write(vals)
        if 'backend_website_ids' in vals:
            for user in self:
                if user.backend_website_ids:
                    users = self.search([('login', '=', user.login)])
                    website_ids = list()
                    for wid in user.backend_website_ids:
                        website_ids.append(wid.id)
                    websites = self.env['website'].sudo().search([('id', 'in', website_ids)])
                    for web in websites:
                        for uid in users.filtered(lambda v: v.id != user.id):
                            if web in uid.backend_website_ids:
                                _logger.error(
                                    "The user '%s' with the same login '%s' is already allowed this website '%s'!",
                                    uid.name, uid.login, web.name)
                                raise ValidationError(
                                    _("The user '%s' with the same login '%s' is already allowed this website '%s'!. "
                                      "It is not possible to use different users with the same login on the same website.")
                                    % (uid.name, uid.login, web.name))
        return res

    @api.depends('backend_website_ids')
    def _compute_backend_website_ids(self):
        """
            Do not want compute this field. Must be filled in by context or direct user action and have to be editable.
        """
        for user in self:
            user.backend_websites_count = len(user.backend_website_ids)

    @staticmethod
    def _get_user(login=None, password=None, env=None):
        user_id = False
        users = env.search([('login', '=', login)])
        website_id = request.env['website'].get_current_website()
        for user in users:
            if user and (user.has_group('base.group_user')
                         or (website_id and website_id in user.backend_website_ids)):
                user_id = user.id
                if password:
                    user.sudo(user_id).check_credentials(password)
                user.sudo(user_id)._update_last_login()
        return user_id

    @classmethod
    def _login(cls, db, login, password):
        """
        Workaround to always let user login in multi websites system for employees and the rest of the users
        who already have allow current_website in their backend_website_ids.
        Signup is only allowed if there no another user with the same login in the same website.
        """
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                if not request:
                    user_ids = env.search([('login', '=', login)]).filtered(lambda x: x.has_group("base.group_user"))
                    for user in user_ids:
                        try:
                            user_id = user.id
                            user.sudo(user.id).check_credentials(password)
                            user.sudo(user_id)._update_last_login()
                        except AccessDenied:
                            user_id = False
                        if user_id:
                            return user_id
                else:
                    user_id = cls._get_user(login, password, env)
        except AccessDenied:
            user_id = False
        status = "successful" if user_id else "failed"
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        website_id = request.env['website'].get_current_website()
        _logger.info("Login %s for db:%s login: %s from %s in %s", status, db, login, ip, website_id.name)
        return user_id

    @api.model
    def _signup_create_user(self, values):
        """
        Check if user exists in current website.
        :return: super if user NOT exists in current website otherwise SignupError
        """
        uid = self._login(self.env.cr.dbname, values.get('login'), values.get('password'))
        user_sudo = request.env['res.users'].sudo().search([('id', '=', uid)])
        if user_sudo:
            raise SignupError(_("Another user is already registered using this email address."))
        return super(ResUsers, self)._signup_create_user(values)

    def reset_password(self, login):
        """
            Retrieve the user corresponding to login (login or email), and reset their password in current website
        """
        uid = self._get_user(login=login, env=self.env['res.users'])
        user_sudo = request.env['res.users'].sudo().search([('id', '=', uid)])
        if len(user_sudo) != 1:
            raise Exception(_('Reset password: invalid username or email'))
        return user_sudo.action_reset_password()
