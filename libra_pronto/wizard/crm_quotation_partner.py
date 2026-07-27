# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError

class CrmQuotationPartner(models.TransientModel):
    _inherit = 'crm.quotation.partner'

    def action_apply(self):

        if self.action == 'create':
                raise ValidationError("Opción no permitida para crear clientes")

        res = super(CrmQuotationPartner, self).action_apply()

        return res 