##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class TipoCliente(models.Model):
	_name = 'sale.tipo.cliente'
	_description = 'Tipo de cliente'

	name = fields.Char('Nombre')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipo_cliente_id = fields.Many2one('sale.tipo.cliente',string='Tipo Cliente', ondelete='Restrict')

    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False, store=True,
        help="This pricelist will be used, instead of the default one, for sales to the current partner")

    @api.constrains('mobile', 'email', 'tipo_cliente_id', 'is_customer')
    def _check_required_fields(self):
        for rec in self:
            mensaje_validacion = ""
            
            if not rec.mobile:
                mensaje_validacion += _("- Debe informar el Nro. de móvil.\n")
            
            if not rec.email:
                mensaje_validacion += _("- Debe informar el correo electrónico.\n")

            # Nota: Asegúrate de que 'is_customer' exista en tu modelo, 
            # ya que en Odoo estándar esa variable cambió en versiones recientes.
            if rec.is_customer and not rec.tipo_cliente_id:
                mensaje_validacion += _("- Debe informar el tipo de cliente.\n")

            if mensaje_validacion:
                raise ValidationError(
                    _("Debe completar los siguientes campos:\n\n%s") % mensaje_validacion
                )

    def write(self, values):
        super(ResPartner,self).write(values)

        if 'sale_type' in values:
            if not self.env.user.has_group('pronto.group_ventas_cambiar_tipo_venta_contacto'):
                create_from_website = self._context.get('create_from_website', False)
                if not create_from_website:
                    raise ValidationError("Su usuario no posee permisos para modificar el tipo de venta")
   
