from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_quote_log_ids = fields.One2many(
        'sale.order.quote.log', 
        'sale_order_id', 
        string="Logs del pedido", 
        copy=False
    )

    def write(self, values):     
        # 1. Ejecutar el write original primero y guardar el resultado
        res = super().write(values)
        
        # 2. Iterar por cada registro para evitar errores de singleton
        for order in self:
            if order.state in ('draft', 'sent', 'sale'):
                # Limpiar logs anteriores de validez y precio de este pedido específico
                order.sale_order_quote_log_ids.filtered(
                    lambda x: x.log_type in ('validez', 'precio')
                ).unlink()

                # Controlar si la fecha de validez existe y está vencida
                if order.validity_date:
                    delta = order.validity_date - fields.Date.context_today(order)
                    if delta.days < 0:
                        self.env['sale.order.quote.log'].registrar_log(
                            order, 
                            f"Fecha de validez vencida: {order.validity_date}", 
                            'validez'
                        )

                # Evaluar las líneas del pedido
                for line in order.order_line.filtered(lambda x: not x.display_type):
                    if not line.product_id.registrar_novedad_presupuesto:
                        continue

                    # --- NOVEDAD: Descuento en componente de Pack ---
                    if line.pack_parent_line_id:
                        # Evitar búsquedas en bucle: usamos filter sobre el pack del producto padre
                        pack_line = line.pack_parent_line_id.product_id.pack_line_ids.filtered(
                            lambda x: x.product_id == line.product_id
                        )
                        descuento_predefinido = pack_line.sale_discount if pack_line else 0.0
                        descuento_modificado = line.discount

                        if descuento_modificado > descuento_predefinido:                
                            self.env['sale.order.quote.log'].registrar_log(
                                order,
                                f"Descuento predefinido: {descuento_predefinido} - Descuento modificado: {descuento_modificado}",
                                'descuento_componente_pack', 
                                line, 
                                line.product_id
                            )

                    # Ignorar control de precio si el pack es detallado pero totalizado en precio
                    if (line.pack_parent_line_id and 
                            line.pack_parent_line_id.pack_type == 'detailed' and 
                            line.pack_parent_line_id.pack_component_price == 'totalized'):
                        continue

                    # --- NOVEDAD: Control de Precios (Tarifa / Pricelist) ---
                    if order.pricelist_id and order.partner_id:                        
                        product = line.product_id.with_context(
                            lang=order.partner_id.lang,
                            partner=order.partner_id,
                            quantity=line.product_uom_qty,
                            date=fields.Datetime.now(),
                            pricelist=order.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=self.env.context.get('fiscal_position')
                        )

                        # Simulación de cálculo de precio según el módulo OCA product_pack
                        if line.product_id.pack_ok and line.product_id.pack_component_price == 'totalized':
                            prices = product.price_compute(
                                price_type='non_detailed', 
                                currency=order.pricelist_id.currency_id
                            )
                            precio_unitario_actual = round(prices.get(line.product_id.id, 0.0), 2)
                        else:
                            # Odoo 18 nativo: _get_display_price ya procesa la tarifa.
                            # Para impuestos incluidos/excluidos de forma segura en Odoo 18:
                            precio_base = line._get_display_price()
                            
                            # Ajuste de impuestos según la posición fiscal y la compañía
                            taxes = line.tax_id.compute_all(
                                precio_base, 
                                currency=order.currency_id, 
                                quantity=1.0, 
                                product=line.product_id, 
                                partner=order.partner_id
                            )
                            # Dependiendo de si comparas contra price_unit (que suele ser sin impuestos devueltos),
                            # usamos 'total_excluded'. Si necesitas con impuestos, usa 'total_included'.
                            precio_unitario_actual = round(taxes['total_excluded'], 2)

                        precio_unitario = round(line.price_unit, 2)

                        if precio_unitario != precio_unitario_actual:                
                            self.env['sale.order.quote.log'].registrar_log(
                                order,
                                f"Precio anterior: {precio_unitario} - Precio nuevo: {precio_unitario_actual}",
                                'precio', 
                                line, 
                                product
                            )                    
        
        return res