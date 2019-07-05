# -*- coding: utf-8 -*-

from odoo import http, tools

from odoo.addons.web_editor.controllers.main import Web_Editor


class WebEditor(Web_Editor):

    @http.route("/web_editor/save_less", type="json", auth="user", website=True)
    def save_less(self, url, bundle_xmlid, content):
        """
        The save_less route is in charge of saving a given modification of a LESS file.
        This part only include a hook to pass website in context to work with website_multi_theme.
        It is necessary to assign website in views because if there not website in context then broken execution
        when try save any css with web editor.

        :param url: the original url of the LESS file which has to be modified
        :param bundle_xmlid: the xmlid of the bundle in which the LESS file addition can be found
        :param content: the new content of the LESS file
        :return: super call with website a True in context for multi theme
        """

        return super(WebEditor, self).save_less(url, bundle_xmlid, content)
