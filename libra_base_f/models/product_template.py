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

    @api.model
    def _get_default_uom_id(self):
        return 0
  
    entregar_al_confirmar_prespuesto = fields.Boolean(string="Entregar al confirmar el pedido",
                    default=True, 
                    help="Si está tildado, el servicio se pone como entregado al confirmar el presupuesto")

    @api.model
    def default_get(self, fields):
        rec = super(ProductTemplate, self).default_get(fields)
        rec['route_ids'] = False        
        rec['tracking'] = False
        rec['taxes_id'] = False
        rec['supplier_taxes_id'] = False

        return rec

    @api.model_create_multi
    def create(self, values):

        for val in values:

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
            if not self.env.user.has_group('libra_base_f.group_no_exigir_campos_producto_vendible'):
                mensaje_validacion = ""
                if val.get('sale_ok') and val.get('type') == 'consu':
                    if val.get('weight', 0) == 0:
                        mensaje_validacion += "- peso \n"
                    if val.get('volume', 0) == 0:
                        mensaje_validacion += "- volumen \n"
                    if not val.get('image_1920'):
                        mensaje_validacion += "- imagen del producto \n"
                    if not val.get('barcode'):
                        mensaje_validacion += "- codigo de barras \n"
                    if not val.get('seller_ids'):
                        mensaje_validacion += "- Proveedor \n"
                    if not val.get('route_ids'):
                        mensaje_validacion += "- Rutas \n"
                    if not val.get('taxes_id'):
                        mensaje_validacion += "- Impuestos cliente \n"
                    if not val.get('supplier_taxes_id'):
                        mensaje_validacion += "- Impuestos de proveedor \n"

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
            if not self.env.user.has_group('libra_base_f.group_no_exigir_campos_producto_vendible'):
                for rec in self:
                    mensaje_validacion = ""
                    if rec.sale_ok and rec.type == 'consu':
                        if rec.weight == 0:
                            mensaje_validacion += "- peso \n"

                        if rec.volume == 0:
                            mensaje_validacion += "- volumen \n"

                        if  not rec.image_1920:
                            mensaje_validacion += "- imagen del producto \n"

                        if  not rec.barcode:
                            mensaje_validacion += "- codigo de barras \n"

                        # en v15 no está mas la tree de precios en el form. Ahora se accede a la misma información
                        # desde el smartbutton "Precio Extra"
                        # if rec.type == 'product' and rec.sale_ok:
                        #     item_lista_precio = rec.item_ids.filtered(lambda x: x.pricelist_id.id == 2)
                        #     if not item_lista_precio:
                        #         mensaje_validacion += "- el precio en la tarifa Costo \n"
                        #     else:
                        #         if item_lista_precio.compute_price == 'fixed' and item_lista_precio.fixed_price == 0:
                        #             mensaje_validacion += "- el precio (distinto de 0) en la tarifa Costo \n"

                        if not rec.taxes_id:
                            mensaje_validacion += "- Impuestos cliente \n"
                        if not rec.supplier_taxes_id:
                            mensaje_validacion += "- Impuestos de proveedor \n"
                        if not rec.route_ids:
                            mensaje_validacion += "- Rutas \n"

                        proveedores = rec.seller_ids
                        if not proveedores:
                            mensaje_validacion += "- Proveedor \n"
                        else:
                            proveedor = proveedores[0]
                            if proveedor.price == 0:
                                mensaje_validacion += "- el precio en el proveedor \n"

                        if mensaje_validacion:
                            detalle_mensaje = mensaje_validacion
                            mensaje_validacion = ""
                            raise ValidationError("Ref. Interna: {} \n\n Debe completar los siguientes campos para que el producto pueda ser vendido: \n\n {}".format(
                                                        rec.default_code,
                                                        detalle_mensaje
                                                ))

        return True