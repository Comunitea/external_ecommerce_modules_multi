=========================
Multi Company Base Module
=========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Production-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Comunitea-lightgray.png?logo=github
    :target: https://github.com/Comunitea/
    :alt: Comunitea
.. |badge4| image:: https://img.shields.io/badge/github-Comunitea%2FMultiWebsite-lightgray.png?logo=github
    :target: https://github.com/Comunitea/external_ecommerce_multi_modules/tree/11.0/multi_company_base
    :alt: Comunitea / Website
.. |badge5| image:: https://img.shields.io/badge/Spanish-Translated-F47D42.png
    :target: https://github.com/Comunitea/external_ecommerce_multi_modules/tree/11.0/multi_company_base/i18n/es.po
    :alt: Spanish Translated

|badge1| |badge2| |badge3| |badge4| |badge5|

This module contains dependencies with the necessary modules to work in a environment with multicompany and with multiwebsite companies.

**Table of contents**

.. contents::
   :local:

Base module for creation of a multi-website company
---------------------------------------------------

This module contains dependencies with the necessary modules to create base multi-company e-commerce page.

It also contains styles and layout elements, bug fixes and module translations.

Web Editor
----------

It include some improves to let use css resources of each website only for web editor of their domain.

Customized Views
----------------

It is overwrite the ir.model.data with noupdate=False to make possible keep active
the desired customize views what and avoid they will be deactivated in website_multi_theme module update.

Now , you may use a views.xml for activate the view what you want like this:

    <record id="website_multi_theme.auto_view_poi_website_layout_logo_show" model="ir.ui.view">
    <field name="active">True</field>
    </record>

Multi themes views
------------------

Change xmlid of duplicated views for the three first characters of website name a make it easy overwrite they
including assets and layouts views

Using this:

    website.name[0:3].strip().lower()

You get:

    website_multi_theme.auto_view_XXX_website_layout_logo_show

Instead of:

    website_multi_theme.auto_view_1643_website_layout_logo_show

Dependencies
------------

For correct use must have **Ecommerce base module** (ecommerce_base) of Comunitea (will be installed automatically).

Repositories to include in the buildout:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* github.com/it-projects-llc/website-addons
* github.com/it-projects-llc/misc-addons
* github.com/it-projects-llc/mail-addons
* github.com/it-projects-llc/access-addons

Author
------

Developer: Comunitea, info@comunitea.com

Contributors
~~~~~~~~~~~~

Pavel Smirnov, pavel@comunitea.com

Rubén Seijas, ruben@comunitea.com

Maintainer
~~~~~~~~~~

This module is maintained by Comunitea.

For support and more information, please visit https://comunitea.com.
