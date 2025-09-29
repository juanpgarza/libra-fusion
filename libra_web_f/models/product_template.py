# Copyright 2021 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_additional_description = fields.Html(
        "Descripción adicional (ecommerce)",
        sanitize_attributes=False,
        copy=False)
