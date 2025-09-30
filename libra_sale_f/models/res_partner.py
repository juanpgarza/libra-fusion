##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipo_cliente_id = fields.Many2one('sale.tipo.cliente',string='Tipo Cliente', ondelete='Restrict')

    def write(self, values):
        super(ResPartner,self).write(values)
        if 'sale_type' in values:
            if not self.env.user.has_group('libra_sale_f.group_ventas_cambiar_tipo_venta_contacto'):
                create_from_website = self._context.get('create_from_website', False)
                if not create_from_website:
                    raise ValidationError("Su usuario no posee permisos para modificar el tipo de venta")
   
