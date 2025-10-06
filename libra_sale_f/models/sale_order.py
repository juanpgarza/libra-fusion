from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_compromiso_vencida = fields.Boolean(string = 'Fecha de Compromiso Vencida', compute = '_compute_vencida', search = '_search_vencida')

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

    def write(self, values):        
        for order in self:
            if self.env.user.has_group('libra_sale_f.group_commitment_date_required'):                
                if ('state' in values and order.state != 'done' and values['state'] == 'sale'):
                        if not order.commitment_date:
                            raise ValidationError(
                                    'Debe informar la fecha de compromiso'
                                    )

            if self.env.user.has_group('libra_sale_f.group_ventas_solo_lectura_pedidos'):
                raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")

        res = super(SaleOrder, self).write(values)

    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        super(SaleOrder,self)._compute_margin()
        for order in self:            
            costo_total = 0
            for line in order.order_line.filtered(lambda r: r.state != 'cancel'):
                costo_total += line.purchase_price * line.product_uom_qty
            order.margin_percent = costo_total and order.margin/costo_total

    def _get_tier_validation_readonly_domain(self):
        # 
        # tengo que sobre-escribir este metodo porque sino, cuando tiene validaciones aprobadas,
        #  no me deja editar los campos por más que el pedido este desbloqueda
        return "False"