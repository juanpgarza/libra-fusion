from odoo import api, models, fields
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_mode_st_id = fields.Many2one('payment.mode.st',string="Modo de pago")

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for rec in invoices:
            rec.payment_mode_st_id = self.payment_mode_st_id
        return invoices