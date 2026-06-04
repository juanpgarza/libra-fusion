from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    excluir_markup = fields.Boolean(string="Excluir del calculo del mark-up (Porcentaje) en los pedidos",
                    compute='_computed_excluir_markup', 
                    readonly=False, 
                    store=True)

    precio_unitario_con_descuento = fields.Float('Precio unitario con descuento', compute="_compute_precio_unitario_con_descuento")
    
    @api.depends('product_id', 'price_unit', 'discount')
    def _compute_precio_unitario_con_descuento(self):
        for line in self:
            line.precio_unitario_con_descuento = line.price_unit * (1 - (line.discount/100))

    @api.depends('product_id','product_id.excluir_calculo_markup')
    def _computed_excluir_markup(self):
        for rec in self:
            if rec.product_id.excluir_calculo_markup == 'siempre':                
                rec.excluir_markup = True
            elif rec.product_id.excluir_calculo_markup == 'componente_pack':
                if rec.pack_parent_line_id:
                    rec.excluir_markup = True
            else:
                rec.excluir_markup = False

    # Hago esto porque no logro que traiga los descuentos que tiene el pack
    # Tambien modifico el action_update_prices de sale.order
    @api.model_create_multi
    def create(self, values):
        res = super(SaleOrderLine,self).create(values)
        for line in res:
            if line.pack_parent_line_id:
                line.discount = line._get_pack_line_discount()
                # import pdb; pdb.set_trace()
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.order_id.sale_order_template_id:
            raise ValidationError("Antes de informar los productos debe informar la plantilla")

    def _get_sale_order_line_multiline_description_sale(self):
        """
        Sobreescribimos el método de sale.order.line para evitar que concatenar
        el nombre/código del producto, mostrando SOLO la descripción de venta.
        """
        self.ensure_one()
        # import pdb;pdb.set_trace()    
        # Si el producto tiene descripción de venta, usamos esa.
        if self.product_id.description_sale:
            return self.product_id.description_sale
        
        # Si no tiene descripción de venta, usamos el comportamiento nativo 
        # (para que no quede la línea completamente en blanco)
        return super(SaleOrderLine, self)._get_sale_order_line_multiline_description_sale()