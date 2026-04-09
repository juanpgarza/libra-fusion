from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_due = fields.Monetary(
        related='partner_id.total_due',
        string = 'Saldo'
    )

    cotizacion = fields.Float(string='Cotización',
                            compute='_compute_cotizacion', 
                            store=True,
                            help='Cotización del dolar en la fecha del presupuesto/pedido.')

    @api.depends('date_order')
    def _compute_cotizacion(self):
        for order in self:
            moneda_origen = self.env.ref('base.USD')
            moneda_destino = self.env.ref('base.ARS')
            compania = self.env.user.company_id
            order.cotizacion = moneda_origen._convert(1,moneda_destino,compania, order.date_order)

    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        super(SaleOrder,self)._compute_margin()
        for order in self:            
            costo_total = 0
            for line in order.order_line.filtered(lambda r: r.state != 'cancel' and not r.excluir_markup):
                costo_total += line.purchase_price * line.product_uom_qty
            order.margin_percent = costo_total and order.margin/costo_total


    def write(self, values):
        for order in self:

            if ('state' in values and order.state != 'done' and values['state'] == 'sale') or 'user_requesting_review' in values:
                if not order.payment_mode_st_id:
                            raise ValidationError(
                                    'Debe informar el modo de pago'
                                    )

            if self.env.user.has_group('libra_pronto.group_commitment_date_required'):
                if ('state' in values and order.state != 'done' and values['state'] == 'sale') or 'user_requesting_review' in values:
                        if not order.commitment_date:
                            raise ValidationError(
                                    'Debe informar la fecha de compromiso'
                                    )

            if self.env.user.has_group('libra_pronto.group_ventas_solo_lectura_pedidos'):
                raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")

        res = super(SaleOrder, self).write(values)

        return res
    
    # hay que hacer esto porque cuando se actualiza el precio
    # se borran los descuentos de los productos del pack
    def action_update_prices(self):
        # import pdb; pdb.set_trace()
        super(SaleOrder, self).action_update_prices()
        for line in self.order_line:
            if line.pack_parent_line_id:
                line.discount = line._get_pack_line_discount()

    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for picking in self.picking_ids:
            self.env['procurement.group'].run_smart_scheduler(picking.id)            