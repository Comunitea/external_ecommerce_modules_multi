odoo.define('portal_multi_access_management.auth_signup', function (require) {
    'use strict';

    $(document).ready(function(){
        var core = require('web.core');
        var _t = core._t;
        var default_email_msg = _t('Por favor, introduce una dirección de correo electrónico válida');
        $(".oe_reset_password_form").validate({
          rules: {
            login: {
              required: true,
              email: true
            }
          },
          messages: {
            email_from: {
                required: default_email_msg,
                email: default_email_msg
            }
          }
        });
        $(".oe_signup_form").validate({
          rules: {
            login: {
              required: true,
              email: true
            }
          },
          messages: {
            email_from: {
                required: default_email_msg,
                email: default_email_msg
            }
          }
        });
    });
});