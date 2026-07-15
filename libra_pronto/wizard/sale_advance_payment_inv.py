##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInvWizard(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        # 1. Dejamos que Odoo corra su flujo normal y cree la factura con sus defaults
        res = super(SaleAdvancePaymentInvWizard, self).create_invoices()

        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)
        
        # 2. Interceptamos la acción resultante para modificar la factura creada
        if isinstance(res, dict) and res.get('res_id'):
            invoice_id = res['res_id']
            # Buscamos la factura en la base de datos
            invoice = self.env['account.move'].browse(invoice_id)
            
            if sale_order.es_un_cambio:
                
            # si es un cambio se tiene que usar el diario de cambios                
                # 3. Forzamos el cambio de diario únicamente si está en borrador
                if invoice.state == 'draft':
                    diario_de_cambios = int(self.env['ir.config_parameter'].sudo().search([('key','=','libra_pronto.diario_de_cambios')]).value)
                    invoice.write({'journal_id': diario_de_cambios})
        return res
