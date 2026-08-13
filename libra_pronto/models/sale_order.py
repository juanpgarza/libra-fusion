from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['sale.order', 'tier.validation']

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

    def action_cancel(self):        
        # solo para pedidos de venta. NO incluye presupuestos
        for rec in self.filtered(lambda x:x.state in ('done','sale') and x.state != 'cancel'):
            group = "libra_pronto.group_cancel_sale_order"
            if not self.env.user.has_group(group):
                group_id = self.env.ref(group)
                raise ValidationError("Opción habilitada solo para los miembros del grupo: \n\n'{} / {}'".format(group_id.sudo().category_id.name,group_id.name))
        return super(SaleOrder, self).action_cancel()

    def _get_tier_validation_readonly_domain(self):
        # 
        # tengo que sobre-escribir este metodo porque sino, cuando tiene validaciones aprobadas,
        #  no me deja editar los campos por más que el pedido este desbloqueda
        return "False"

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        # import pdb; pdb.set_trace()
        rec['sale_order_template_id'] = False

        return rec

    @api.onchange('partner_id')
    def _compute_user_id(self):
    #     # Tarea #974
    #     # Se anula la funcion que hace que tome el comercial asignado al cliente
    #     # Lo informan a mano         
        res = super(SaleOrder, self)._compute_user_id()
        for rec in self:
            rec.user_id = self.env.user        
        return res
    
    def request_validation(self):
        if not self.payment_mode_st_id:
            raise ValidationError(
                    'Debe informar el modo de pago'
                    )

        if self.env.user.has_group('libra_pronto.group_commitment_date_required'):
            if not self.commitment_date:
                raise ValidationError(
                                'Debe informar la fecha de compromiso'
                                )

        rec = super(SaleOrder, self).request_validation()

    def action_add_from_catalog(self):
            self.ensure_one()
            
            # Validación antes de llamar a super()
            if not self.sale_order_template_id:
                raise ValidationError(_("Antes de informar los productos debe informar la plantilla."))
                
            return super().action_add_from_catalog()