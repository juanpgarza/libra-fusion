from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        res = super(AccountMove,self).button_draft()
        for rec in self:
            if rec.move_type in ('out_invoice','out_refund') and rec.journal_id.l10n_latam_use_documents and not self.env.user.has_group('libra_account_f.group_cancelar_comprobante_fiscal'):                
                raise ValidationError("No es posible cambiar a borrador a un comprobante fiscal validado contra AFIP.")