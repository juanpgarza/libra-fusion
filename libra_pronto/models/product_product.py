from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):        
        # res = super(ProductProduct,self).get_product_multiline_description_sale()

        if self.description_sale:
            name = self.description_sale
        else:
            name = self.display_name

        return name    