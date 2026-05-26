# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_invoice_ids = fields.Many2many(
                comodel_name="account.move", 
                string="Facturas del pedido", 
                compute='_compute_sale_invoice_ids',
    )

    sale_order_type_id = fields.Many2one(related="sale_id.type_id", string= 'Tipo de venta')

    def _compute_sale_invoice_ids(self):
        for rec in self:
            # facturas asociadas con el pedido relacionado con la entrega
            rec.sale_invoice_ids = rec.sale_id.mapped('order_line.invoice_lines.move_id').filtered(lambda x: x.move_type == 'out_invoice')

    def action_cancel(self):        
        for rec in self.filtered(lambda x: x.state != 'cancel'):
            group = "libra_pronto.group_cancel_picking"
            if not self.env.user.has_group(group):
                group_id = self.env.ref(group)
                raise ValidationError("Opción habilitada solo para los miembros del grupo: \n\n'{} / {}'".format(group_id.sudo().category_id.name,group_id.name))
        return super(StockPicking, self).action_cancel()

    @api.model
    def _schedule_activity(self,activity_type_id):

        model_stock_picking = self.env.ref('stock.model_stock_picking')
        if self.location_id.usuario_responsable_reserva_stock_id:
            asignada_a = self.location_id.usuario_responsable_reserva_stock_id 
        else:
            asignada_a = self.env.user.company_id.usuario_responsable_reserva_stock_id

        vals = {
            'activity_type_id': activity_type_id.id,
            'date_deadline': fields.Date.today(),
            'summary': activity_type_id.summary,
            'user_id': asignada_a.id,
            'res_id': self.id,
            'res_model_id': model_stock_picking.id,
            'res_model':  model_stock_picking.model
        }
        # mail_activity_quick_update=True para que no le muestre un aviso al usuario. t-70
        return self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(vals)

    # def button_validate(self):
    #     # solo en los movimientos de salida
    #     if (self.picking_type_id.code == 'outgoing'):
    #         # Control de productos agregados al pedido pero que no se facturaron
    #         if not self.env.user.has_group('libra_pronto.group_stock_omitir_bloqueo_pendiente_facturar'):
    #             if self.sale_id.order_line.filtered(lambda x: x.qty_invoiced < (x.product_uom_qty - x.quantity_returned)):
    #                 raise ValidationError("El pedido asociado al movimiento tiene productos pendientes de facturar.")
        
    #     result = super(StockPicking,self).button_validate()
        
    #     # solo en los movimientos de salida
    #     if (self.picking_type_id.code == 'outgoing'):
    #         # solo si tienen facturas asociadas.
    #         # osea que para tipo de venta 'sin factura' no aplica porque no se le asocia factura al movimiento
    #         # tampoco para las transferencia internas porque las operaciones son del tipo 'internal'
    #         for inv in self.sale_invoice_ids:
                
    #             if (inv.move_type == 'out_invoice'):
    #                 # solo para las facturas (sin NC)
    #                 if (inv.state == 'draft'):
    #                     raise ValidationError("Este movimiento tiene al menos una factura asociada en estado borrador.")

    #     return result

    # sobre-escribo el metodo de stock_voucher (adhoc) para calculo de valor declarado
    # cambio: price_reduce_taxexcl por purchase_price
    # CUIDADO! siempre verificar que funcione bien con pedidos en pesos y en dolares
    # si el costo lo saco de order_line.product_id.standard_price NO FUNCIONA cuando la lista es en Dolares
    # porque esta en pesos y despues lo pasa a dolares
    @api.depends(
        "automatic_declare_value",
        "move_ids.state",
        "move_ids.quantity",
    )
    def _compute_declared_value(self):
        for rec in self.filtered(lambda p: p.automatic_declare_value and p.state not in ["done", "cancel"]):
            done_value = 0.0
            picking_value = 0.0
            inmediate_transfer = True
            pricelist = False
            stock_bom_lines = self.env["stock.move"]            
            for move_line in rec.move_ids.filtered(lambda x: x.state != "cancel"):
                order_line = move_line.sale_line_id
                if move_line.quantity:
                    inmediate_transfer = False
                if order_line:
                    pricelist = rec.sale_id.pricelist_id
                    # this should happends only if on SO it's a bom kit
                    if not order_line.product_id == move_line.product_id:
                        stock_bom_lines |= move_line
                        continue
                    so_product_qty = move_line.product_uom_qty
                    so_qty_done = move_line.quantity
                    # convert quantities if move line uom and sale line uom
                    # are different
                    if move_line.product_uom != order_line.product_uom:
                        so_product_qty = move_line.product_uom._compute_quantity(
                            move_line.product_uom_qty, order_line.product_uom
                        )
                        so_qty_done = move_line.product_uom._compute_quantity(
                            move_line.quantity, order_line.product_uom
                        )
                    # import pdb; pdb.set_trace()
                    picking_value += order_line.purchase_price * so_product_qty
                    done_value += order_line.purchase_price * so_qty_done
                elif rec.picking_type_id.pricelist_id:
                    pricelist = rec.picking_type_id.pricelist_id
                    price = rec.picking_type_id.pricelist_id.with_context(uom=move_line.product_uom.id)._price_get(
                        move_line.product_id, move_line.quantity or 1.0, partner=rec.partner_id.id
                    )[rec.picking_type_id.pricelist_id.id]
                    picking_value += price * move_line.product_uom_qty
                    done_value += price * move_line.quantity

            # This is for product in a kit (should only happen if sale_mrp ins
            # installed). If it is bom we only compute amount if all bom
            # components are deliverd (same as in bom _get_delivered_qty)
            bom_enable = "bom_ids" in self.env["product.template"]._fields
            if bom_enable:
                for so_bom_line in stock_bom_lines.mapped("sale_line_id"):
                    bom = self.env["mrp.bom"]._bom_find(products=so_bom_line.product_id)[so_bom_line.product_id]
                    if bom and bom.type == "phantom":
                        bom_moves = so_bom_line.move_ids & stock_bom_lines
                        done_avg = []
                        picking_avg = []
                        boms, lines = bom.sudo().explode(
                            so_bom_line.product_id, so_bom_line.product_uom_qty, picking_type=bom.picking_type_id
                        )
                        for move in bom_moves:
                            bom_quantity = 0.0
                            for bom_line, line_data in lines:
                                if bom_line.product_id == move.product_id:
                                    bom_quantity += line_data["qty"]
                            if not bom_quantity:
                                continue
                            picking_avg.append(move.product_uom_qty / bom_quantity)
                            done_avg.append(move.quantity / bom_quantity)
                        if len(picking_avg) > 0:
                            picking_value += so_bom_line.purchase_price * (sum(picking_avg) / len(picking_avg))
                        if len(done_avg) > 0:
                            done_value += so_bom_line.purchase_price * (sum(done_avg) / len(done_avg))

            declared_value = picking_value if inmediate_transfer else done_value
            if pricelist:
                # we convert the declared_value to the currency of the company
                rec.declared_value = pricelist.currency_id._convert(
                    declared_value,
                    rec.company_id.currency_id,
                    rec.company_id,
                    rec.sale_id.date_order or fields.Date.today(),
                )
            else:
                rec.declared_value = declared_value