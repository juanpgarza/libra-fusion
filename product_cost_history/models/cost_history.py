from odoo import models, fields

class ProductReplenishmentCostHistory(models.Model):
    _name = 'product.replenishment.cost.history'
    _description = 'Historial de Costos de Reposición'
    _order = 'create_date desc'

    product_tmpl_id = fields.Many2one(
        'product.template', 
        string='Producto', 
        required=True, 
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Modificado por', 
        default=lambda self: self.env.user, 
        required=True
    )
    old_cost = fields.Monetary(string='Costo Anterior', currency_field='old_currency_id')
    new_cost = fields.Monetary(string='Costo Nuevo', currency_field='new_currency_id')
    old_currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda anterior',         
        store=True
    )
    new_currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda nueva',
        store=True
    )
    date = fields.Datetime(
        string='Fecha de Modificación', 
        default=fields.Datetime.now, 
        required=True
    )