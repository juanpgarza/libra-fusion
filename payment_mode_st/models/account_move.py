from odoo import api, models, fields
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_mode_st_id = fields.Many2one('payment.mode.st',string="Modo de pago")