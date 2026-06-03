from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        cost_changed = 'replenishment_base_cost' in vals
        currency_changed = 'replenishment_base_cost_currency_id' in vals
        # import pdb; pdb.set_trace()
        if cost_changed or currency_changed:
            history_vals_list = []

            for record in self:
                old_cost = record.replenishment_base_cost
                old_currency_id = record.replenishment_base_cost_currency_id.id

                new_cost = vals.get(
                    'replenishment_base_cost',
                    old_cost
                )
                new_currency_id = vals.get(
                    'replenishment_base_cost_currency_id',
                    old_currency_id
                )

                # Registrar si cambió el costo o la moneda
                if (
                    old_cost != new_cost or
                    old_currency_id != new_currency_id
                ):
                    history_vals_list.append({
                        'product_tmpl_id': record.id,
                        'old_cost': old_cost,
                        'new_cost': new_cost,
                        'old_currency_id': old_currency_id,
                        'new_currency_id': new_currency_id,
                        'user_id': self.env.uid,
                    })

            res = super(ProductTemplate, self).write(vals)

            if history_vals_list:
                self.env[
                    'product.replenishment.cost.history'
                ].sudo().create(history_vals_list)

            return res

        return super(ProductTemplate, self).write(vals)