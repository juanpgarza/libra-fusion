##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import datetime
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if not self.partner_id:
            # para que borre el "Entregar a" por defecto
            self.picking_type_id = False

    def write(self, values):
        # import pdb; pdb.set_trace()
        if self.env.user.has_group('libra_purchase_f.group_compras_solo_lectura_ordenes_compra'):
            raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")
        super(PurchaseOrder,self).write(values)