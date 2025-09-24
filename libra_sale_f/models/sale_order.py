from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_compromiso_vencida = fields.Boolean(string = 'Fecha de Compromiso Vencida', compute = '_compute_vencida', search = '_search_vencida')

    def _compute_vencida(self):
        now = fields.Datetime.now()
        # import pdb; pdb.set_trace()
        for rec in self:
            if rec.state in ('sale','done') and rec.delivery_status == 'to deliver' and rec.commitment_date:
                rec.fecha_compromiso_vencida = now > rec.commitment_date
            else:
                rec.fecha_compromiso_vencida = False
            
    def _search_vencida(self, operator, value):
        now = fields.Datetime.now()
        # import pdb; pdb.set_trace()
        facturas = self.env['sale.order'].search([])        
        ids = facturas.filtered(lambda x: x.state in ('sale','done') and x.delivery_status == 'to deliver' and x.commitment_date and now > x.commitment_date).mapped('id')
        return [('id', 'in', ids)]

    @api.model
    def pedidos_fecha_compromiso_vencida(self):
        res = self.search([('fecha_compromiso_vencida','=',True)])
        # import pdb; pdb.set_trace()
        # len(self.env['sale.order'].pedidos_fecha_compromiso_vencida())
        return res
    
    def action_cancel(self):        
        # solo para pedidos de venta. NO incluye presupuestos
        for rec in self.filtered(lambda x:x.state in ('done','sale') and x.state != 'cancel'):
            group = "libra_sale_f.group_cancel_sale_order"
            if not self.env.user.has_group(group):
                group_id = self.env.ref(group)
                raise ValidationError("Opción habilitada solo para los miembros del grupo: \n\n'{} / {}'".format(group_id.sudo().category_id.name,group_id.name))
        return super(SaleOrder, self).action_cancel()

    @api.onchange('partner_id')
    def _compute_user_id(self):
    #     # Tarea #974
    #     # Se anula la funcion que hace que tome el comercial asignado al cliente
    #     # Lo informan a mano         
        res = super(SaleOrder, self)._compute_user_id()
        for rec in self:
            rec.user_id = self.env.user        
        return res

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        # import pdb; pdb.set_trace()
        rec['sale_order_template_id'] = False

        return rec

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Asegurar que sale_order_template_id quede vacío al cambiar partner_id o al crear"""
        if not self.id:  # Solo al crear un nuevo presupuesto
            self.sale_order_template_id = False
