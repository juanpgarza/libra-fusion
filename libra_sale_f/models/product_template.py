# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from odoo.exceptions import ValidationError,UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    meses_de_stock = fields.Float("Meses de stock", compute="_compute_meses_de_stock", store=True)

    @api.depends('sales_count', 'virtual_available')
    def _compute_meses_de_stock(self):
        for rec in self:
            rec.meses_de_stock = rec.sales_count and rec.virtual_available / rec.sales_count * 12
