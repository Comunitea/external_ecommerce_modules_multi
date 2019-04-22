# Copyright 2019 Javier Colmenero <javier@comunitea.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import models, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.constrains('company_id', 'website_id')
    def _check_websites_in_company(self):
        for record in self:
            if record.website_id:
                website_company = record.website_id.company_id
                if record.company_id and website_company != record.company_id:
                    raise ValidationError(_("Error! Only the company's websites are allowed. \
                        Leave the Company field empty or select corresponding company"))
