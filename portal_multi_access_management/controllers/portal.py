# -*- coding: utf-8 -*-

from odoo import http, _

from odoo.http import request

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalAccount(PortalAccount):

    def _get_account_invoice_domain(self):
        """
         Workaround to get invoices in multi user system by website and show only website user invoices in portal.
        """
        partner = request.env.user.partner_id
        website = request.env['website'].get_current_website()
        domain = [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancel']),
            ('team_id', '=', website.salesteam_id.id),
        ]
        return domain


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        """
            Workaround to get sales_user in multi user system by website and show only website user documents in portal.
            Same partner can be different users for each website, not just one.
        """
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        website = request.env['website'].get_current_website()

        SaleOrder = request.env['sale.order']
        quotation_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel']),
            ('partner_id', '=', partner.id),
            ('website_id', '=', website.id),
        ])
        order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('partner_id', '=', partner.id),
            ('website_id', '=', website.id),
        ])
        sales_user = values['sales_user']
        if partner.user_ids[0] and not partner.user_ids[0]._is_public():
            sales_user = partner.user_ids[0]
        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
            'portal_website': website,
            'sales_user': sales_user,
        })
        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        website = request.env['website'].get_current_website()
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel']),
            ('partner_id', '=', partner.id),
            ('website_id', '=', website.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotes_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'portal_website': website,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        website = request.env['website'].get_current_website()
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('partner_id', '=', partner.id),
            ('website_id', '=', website.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'portal_website': website,
        })
        return request.render("sale.portal_my_orders", values)
