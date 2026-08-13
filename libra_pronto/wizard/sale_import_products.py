# Copyright 2016 Cédric Pigeon, ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleImportProducts(models.TransientModel):
    _inherit = "sale.import.products"

    def create_items(self):        
        res = super(SaleImportProducts, self).create_items()
        so_obj = self.env["sale.order"]
        sale = so_obj.browse(self.env.context.get("active_id", False))
        
        if not sale.sale_order_template_id:
            raise ValidationError("Antes de informar los productos debe informar la plantilla.")
        return res