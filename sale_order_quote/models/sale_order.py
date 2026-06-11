##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_quote_log_ids = fields.One2many('sale.order.quote.log','sale_order_id',string="Logs del pedido", copy=False)

    def write(self, values): 
        super(SaleOrder,self).write(values)

        if self.state in ('draft','sent'):
            self.sale_order_quote_log_ids.filtered(lambda x: x.log_type in ('validez', 'precio')).unlink()

            for line in self.order_line.filtered(lambda x: not x.display_type):
                if line.product_id.registrar_novedad_presupuesto:

                    # copiado desde: product_uom_change (addons/sale)
                    if line.order_id.pricelist_id and line.order_id.partner_id:                        
                        
                        product = line.product_id.with_context(
                            lang=line.order_id.partner_id.lang,
                            partner=line.order_id.partner_id,
                            quantity=line.product_uom_qty,
                            # date=line.order_id.date_order,
                            date=fields.Datetime.now(),
                            pricelist=line.order_id.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=line.env.context.get('fiscal_position')
                        )

                        if line.product_id.pack_ok and line.product_id.pack_component_price == 'totalized':
                            # addons-OCA/product-pack/product_pack/models/product_product.py:33
                            prices = product.price_compute(price_type='non_detailed',currency=line.order_id.pricelist_id.currency_id)
                            precio_unitario_actual = round(prices[line.product_id.id],2)
                            # import pdb; pdb.set_trace()
                        else:              
                            precio_unitario_actual = round(self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(), product.taxes_id, line.tax_id, line.company_id),2)

                        precio_unitario = round(line.price_unit,2)
                        
                        if precio_unitario != precio_unitario_actual:                
                            self.env['sale.order.quote.log'].registrar_log(self,
                                "Precio presupuesto: {} - Precio actualizado: {}".format(
                                    precio_unitario,
                                    precio_unitario_actual),'precio', line, product)                    

                    
        return