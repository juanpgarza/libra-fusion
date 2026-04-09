from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_draft(self):
        if not self.env.user.has_group('libra_pronto.group_payment_to_draft'):
            raise ValidationError("No tiene los permisos suficientes para pasar a borrador ")
        super().action_draft()