# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    usuario_responsable_reserva_stock_id = fields.Many2one('res.users',string="Resp. reservas de stock")
