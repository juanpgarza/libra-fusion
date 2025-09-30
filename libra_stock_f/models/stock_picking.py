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
            group = "libra_stock_f.group_cancel_picking"
            if not self.env.user.has_group(group):
                group_id = self.env.ref(group)
                raise ValidationError("Opción habilitada solo para los miembros del grupo: \n\n'{} / {}'".format(group_id.sudo().category_id.name,group_id.name))
        return super(StockPicking, self).action_cancel()

    def button_validate(self):
        # solo en los movimientos de salida
        if (self.picking_type_id.code == 'outgoing'):
            # Control de productos agregados al pedido pero que no se facturaron
            if not self.env.user.has_group('libra_stock_f.group_stock_omitir_bloqueo_pendiente_facturar'):
                if self.sale_id.order_line.filtered(lambda x: x.qty_invoiced < (x.product_uom_qty - x.quantity_returned)):
                    raise ValidationError("El pedido asociado al movimiento tiene productos pendientes de facturar.")
        
        result = super(StockPicking,self).button_validate()
        
        # solo en los movimientos de salida
        if (self.picking_type_id.code == 'outgoing'):
            # solo si tienen facturas asociadas.
            # osea que para tipo de venta 'sin factura' no aplica porque no se le asocia factura al movimiento
            # tampoco para las transferencia internas porque las operaciones son del tipo 'internal'
            for inv in self.sale_invoice_ids:
                
                if (inv.move_type == 'out_invoice'):
                    # solo para las facturas (sin NC)
                    if (inv.state == 'draft'):
                        raise ValidationError("Este movimiento tiene al menos una factura asociada en estado borrador.")

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