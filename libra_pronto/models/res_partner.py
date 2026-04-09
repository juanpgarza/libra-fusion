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

    @api.model_create_multi
    def create(self, values):

        for val in values:
            mensaje_validacion = ""
            if not val.get('mobile'):
                mensaje_validacion += "- Debe informar el Nro. de móvil  \n"

            if not val.get('email'):
                mensaje_validacion += "- Debe informar el correo electrónico \n"

            if not val.get('tipo_cliente_id') and val.get('is_customer'):
                mensaje_validacion += "- Debe informar el tipo de cliente \n"

            # if not val.get('property_product_pricelist_ids') and val.get('is_customer'):
            #     mensaje_validacion += "- Debe informar la lista de precios \n"

            if mensaje_validacion:
                    raise ValidationError(
                        "Debe completar los siguientes campos: \n\n" + mensaje_validacion
                    )

        res = super(ResPartner, self).create(values)
        return res


    def write(self, values):
        super(ResPartner,self).write(values)

        for rec in self:
            mensaje_validacion = ""
            if not rec.mobile:
                mensaje_validacion += "- Debe informar el Nro. de móvil  \n"
            
            if not rec.email:
                mensaje_validacion += "- Debe informar el correo electrónico  \n"

            if not rec.tipo_cliente_id and rec.is_customer:
                mensaje_validacion += "- Debe informar el tipo de cliente \n"

            # if not rec.property_product_pricelist_ids and rec.is_customer:
            #     mensaje_validacion += "- Debe informar la lista de precios \n"            

            if mensaje_validacion:
                    raise ValidationError(
                        "Debe completar los siguientes campos: \n\n" + mensaje_validacion
                    )

        if 'sale_type' in values:
            if not self.env.user.has_group('pronto.group_ventas_cambiar_tipo_venta_contacto'):
                create_from_website = self._context.get('create_from_website', False)
                if not create_from_website:
                    raise ValidationError("Su usuario no posee permisos para modificar el tipo de venta")
   
