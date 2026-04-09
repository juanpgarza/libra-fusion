# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PaymentModeST(models.Model):
    _name = 'payment.mode.st'
    _description = 'Modo de pago'

    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    
    active = fields.Boolean(default=True)

    name = fields.Char('Descripción')

