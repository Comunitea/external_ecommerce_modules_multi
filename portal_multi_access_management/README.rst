==============================
Portal Multi Access Management
==============================

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
    :target: https://github.com/Comunitea/external_ecommerce_multi_modules/tree/11.0/portal_multi_access_management
    :alt: Comunitea / Website
.. |badge5| image:: https://img.shields.io/badge/Spanish-Translated-F47D42.png
    :target: https://github.com/Comunitea/external_ecommerce_multi_modules/blob/11.0/portal_multi_access_management/i18n/es.po
    :alt: Spanish Translated


|badge1| |badge2| |badge3| |badge4| |badge5|

This module let you have control about user portal access of your websites.

It is compatible with the multi-website.

**Table of contents**

.. contents::
   :local:

Access
~~~~~~
You can manage portal access of your users setting their allowed websites.
They only be enabled to get portal access for their allowed websites.

Set this in Settings > Users and companies > Users > Multi websites > Allowed Websites

Users
~~~~~~
Now it is possible for an user that use their same login into different websites

Invitation
~~~~~~~~~~
Improve portal access management wizard

By Domain
~~~~~~~~~~
#. You only can management portal access for your current website domain.
#. Remember you can change it in black task bar by select another one.
#. If you do not have a website selector in black task bar, please ask for permissions of Multi Websites for Backend to your administrator.
#. Please, note this selector is available only if you have more than one allowed website otherwise current website domain will be taken.

Portal checkbox
~~~~~~~~~~~~~~~
#. Please, pay attention to portal checkbox.
#. Remember: You have to check it for users who you want granted access.
#. If an user have already checked it then means this user has already get granted access for some website but not for a website with this domain, therefore will be sent a new email access for this domain.
#. Note that you can always check user access in their settings by allowed websites field.

Portal Account
~~~~~~~~~~~~~~
All documents in multi user system by website are showed only for website user.

Register and Reset pwd form
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add validation script for email field to check correct pattern: your_name@provider.domain

Author
~~~~~~
.. image:: https://comunitea.com/wp-content/uploads/2016/01/logocomunitea3.png
   :alt: Comunitea
   :target: https://comunitea.com

Comunitea Servicios Tecnológicos S.L.

For support and more information, please visit `<https://comunitea.com>`_.

Contributors
------------
Rubén Seijas (ruben@comunitea.com)

Maintainer
----------
.. image:: https://comunitea.com/wp-content/uploads/2016/01/logocomunitea3.png
   :alt: Comunitea
   :target: https://comunitea.com

Comunitea Servicios Tecnológicos S.L.

For support and more information, please visit `<https://comunitea.com>`_.

Known issues / Roadmap
~~~~~~~~~~~~~~~~~~~~~~

This module has the following limitations:

 * It will not work as long as cookies are not accepted.
 * When cookies are already accepted you need to change the page or manually reload it to see the header affix on the top of the page.
 * TODO: Be able to establish the position of the scroll from which you want to affix the header.

Bug Tracker
~~~~~~~~~~~
Bugs are tracked on `Comunitea Issues <https://github.com/Comunitea/external_ecommerce_modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`Feedback <https://github.com/Comunitea/PXGO_00028_2014_SyD/issues/new>`_.

Please, do not contact contributors directly about support or help with technical issues.

Disclaimer of Warranties
~~~~~~~~~~~~~~~~~~~~~~~~

    **Attention!**

    We provide this module as is, and we make no promises or guarantees about this correct working.

    `Comunitea <https://comunitea.com>`_ provides this application without warranty of any kind.

    `Comunitea <https://comunitea.com>`_ does not warrant that the module will meet your requirements;
    that the current application will be uninterrupted, timely, secure, or error-free or that any defects or errors will be corrected.
