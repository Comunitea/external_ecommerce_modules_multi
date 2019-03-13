
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    _inherit = 'ir.rule'

    """BORRAR CUANDO SE ACTUALICE EL ORIOGINAL"""

    @api.model
    @tools.ormcache_context('self._uid', 'model_name', 'mode', keys=["website_id"])
    def _compute_domain(self, model_name, mode="read"):

        if mode not in self._MODES:
            raise ValueError('Invalid mode: %r' % (mode,))

        if self._uid == SUPERUSER_ID:
            return None

        query = """ SELECT r.id FROM ir_rule r JOIN ir_model m ON (r.model_id=m.id)
                    WHERE m.model=%s AND r.active AND r.perm_{mode}
                    AND (r.id IN (SELECT rule_group_id FROM rule_group_rel rg
                                  JOIN res_groups_users_rel gu ON (rg.group_id=gu.gid)
                                  WHERE gu.uid=%s)
                         OR r.global)
                """.format(mode=mode)
        self._cr.execute(query, (model_name, self._uid))
        rule_ids = [row[0] for row in self._cr.fetchall()]
        if not rule_ids:
            return []
        # browse user and rules as SUPERUSER_ID to avoid access errors!
        eval_context = self._eval_context()
        user_groups = self.env.user.groups_id
        global_domains = []                     # list of domains
        group_domains = []                      # list of domains
        for rule in self.browse(rule_ids).sudo():
            # BEGIN redefined part of original _compute_domain of odoo/base/addons/ir/ir_rule.
            # have to redefine all method to take in account new ir.rule ``backend_behaviour`` setting
            dom = []
            if not eval_context.get('website_id') and rule.backend_behaviour:
                dom = [(1, '=', 1)] if rule.backend_behaviour == 'true' else [(0, '=', 1)]
            else:
                # evaluate the domain for the current user
                dom = safe_eval(rule.domain_force, eval_context) if rule.domain_force else []
                dom = expression.normalize_domain(dom)
            # END redefined part of original _compute_domain
            if not rule.groups:
                global_domains.append(dom)
            elif rule.groups & user_groups:
                group_domains.append(dom)

        # combine global domains and group domains
        if not group_domains:
            return expression.AND(global_domains)
        return expression.AND(global_domains + [expression.OR(group_domains)])
