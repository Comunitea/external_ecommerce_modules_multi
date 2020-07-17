odoo.define('portal_multi_access_management.auth_signup', function (require) {
    'use strict';

    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function(){
        var default_email_msg = _t('Please, write your email with a right format such: your_name@provider.domain');
        $(".oe_reset_password_form").validate({
            rules: {
                login: {
                    required: true,
                    email: true
                }
            },
            messages: {
                login: {
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
                login: {
                    required: default_email_msg,
                    email: default_email_msg
                }
            }
        });
    });
});