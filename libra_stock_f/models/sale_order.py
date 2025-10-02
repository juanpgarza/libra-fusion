from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for picking in self.picking_ids:
            self.env['procurement.group'].run_smart_scheduler(picking.id)
