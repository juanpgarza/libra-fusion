##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    excluir_calculo_markup = fields.Selection([
                        ('nunca', 'Nunca'),
                        ('componente_pack', 'Cuando es componente de pack'),
                        ('siempre', 'Siempre')],
                        default='nunca',
                        string='Excluir del cálculo del markup')

    @api.model
    def default_get(self, fields):
        rec = super(ProductTemplate, self).default_get(fields)
        rec['excluir_calculo_markup'] = False
        rec['uom_id'] = False
        rec['uom_po_id'] = False
        rec['categ_id'] = False
        rec["route_ids"] = False
        return rec

    @api.model_create_multi
    def create(self, values):

        for val in values:

            if not val.get('default_code'):
                raise UserError("Debe informar la referencia interna")

            # Validate 'type' and 'pack_ok' fields
            if 'type' in val and 'pack_ok' in val:
                if val['pack_ok'] and val['type'] != 'service':
                    raise UserError("El Tipo de producto de los packs debe ser 'Servicio'")
            
            # import pdb; pdb.set_trace()
            if not val.get('tracking'):
                # este campo es obligatorio a nivel de base de datos
                # hay que informarlo aunque no se marque el producto como vendible
                if val.get('type') == 'consu':
                    raise ValidationError("Debe informar 'Rastrear inventario' y el campo Seguimiento (Inventario/Trazabilidad)")
                else:
                    values['tracking'] = 'none'

            # Perform validation for saleable products
            if not self.env.user.has_group('libra_pronto.group_no_exigir_campos_producto_vendible'):
                mensaje_validacion = ""
                if val.get('sale_ok') and val.get('type') == 'consu':
                    if not val.get('barcode'):
                        mensaje_validacion += "- codigo de barras \n"
                    if not val.get('excluir_calculo_markup'):
                        mensaje_validacion += "- Excluir del cálculo del markup \n"
                    if not val.get('taxes_id'):
                        mensaje_validacion += "- Impuestos cliente \n"
                    if not val.get('supplier_taxes_id'):
                        mensaje_validacion += "- Impuestos de proveedor \n"
                    if not val.get('sale_additional_description'):
                        mensaje_validacion += "- Descripción adicional - ecommerce \n"
                    if val.get('weight') == 0:
                        mensaje_validacion += "- Peso \n"
                    if val.get('volume') == 0:
                        mensaje_validacion += "- Volumen \n"
                    if not val.get('image_1920'):
                        mensaje_validacion += "- imagen del producto \n"
                    if not val.get('seller_ids'):
                        mensaje_validacion += "- Proveedor \n"
                    if not val.get('route_ids'):
                        mensaje_validacion += "- Rutas \n"

                if mensaje_validacion:
                    raise ValidationError(
                        "Debe completar los siguientes campos para que el producto pueda ser vendido: \n\n" + mensaje_validacion
                    )

        # Call the super method to create records
        res = super(ProductTemplate, self).create(values)
        return res


    def write(self, values):
        super(ProductTemplate,self).write(values)

        if 'type' in values or 'pack_ok' in values:
            if self.pack_ok and self.type !='service':
                raise UserError("El Tipo de producto de los pack´s debe ser 'Servicio'")
        
        controlar_requeridos = self.env.context.get('controlar_requeridos', True)

        if controlar_requeridos:
            if not self.env.user.has_group('libra_pronto.group_no_exigir_campos_producto_vendible'):
                for rec in self:
                    mensaje_validacion = ""
                    if rec.sale_ok and rec.type == 'consu':
                        if not rec.default_code:
                            raise UserError("Debe informar el campo referencia")
                        if not rec.barcode:
                            mensaje_validacion += "- codigo de barras \n"
                        if not rec.excluir_calculo_markup:
                            mensaje_validacion += "- Excluir del cálculo del markup \n"
                        if not rec.taxes_id:
                            mensaje_validacion += "- Impuestos de cliente \n"
                        if not rec.supplier_taxes_id:
                            mensaje_validacion += "- Impuestos de proveedor \n"
                        if not rec.sale_additional_description:
                            mensaje_validacion += "- Descripción adicional - ecommerce \n"
                        if rec.weight == 0:
                            mensaje_validacion += "- Peso \n"
                        if rec.volume == 0:
                            mensaje_validacion += "- Volumen \n"
                        if not rec.image_1920:
                            mensaje_validacion += "- imagen del producto \n"

                        proveedores = rec.seller_ids
                        if not proveedores:
                            mensaje_validacion += "- Proveedor \n"
                        else:
                            proveedor = proveedores[0]
                            if proveedor.price == 0:
                                mensaje_validacion += "- el precio en el proveedor \n"

                        if not rec.route_ids:
                            mensaje_validacion += "- Rutas \n"

                        if mensaje_validacion:
                            detalle_mensaje = mensaje_validacion
                            mensaje_validacion = ""
                            raise ValidationError("Ref. Interna: {} \n\n Debe completar los siguientes campos para que el producto pueda ser vendido: \n\n {}".format(
                                                        rec.default_code,
                                                        detalle_mensaje
                                                ))


        return True