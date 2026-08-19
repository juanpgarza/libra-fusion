from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_draft(self):
        if not self.env.user.has_group('libra_pronto.group_payment_to_draft'):
            raise ValidationError("No tiene los permisos suficientes para pasar a borrador ")
        super().action_draft()

    def action_post(self):

        for payment in self:
            # Captura las líneas de deuda en borrador (según el módulo usado: to_pay_move_line_ids o debt_line_ids)
            debt_lines = getattr(payment, 'to_pay_move_line_ids', None) or getattr(payment, 'debt_line_ids', None)
            
            # Si no usa un campo One2many custom, intenta obtener los move_ids asociados al contexto o líneas
            invoices = debt_lines.mapped('move_id').filtered(lambda m: m.is_invoice()) if debt_lines else payment.move_id

            for invoice in invoices:
                if payment.en_clima != invoice.en_clima:
                    raise ValidationError(_(
                        "Incompatibilidad en la marca 'En clima':\n"
                        "- Pago: %s ('En clima': %s)\n"
                        "- Factura %s: ('En clima': %s)\n\n"
                        "No se puede confirmar el pago para facturas con marca distinta."
                    ) % (
                        payment.name or 'Borrador', 
                        "Sí" if payment.en_clima else "No",
                        invoice.name, 
                        "Sí" if invoice.en_clima else "No"
                    ))

        return super().action_post()
