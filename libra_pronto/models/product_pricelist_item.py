from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError

class Message(models.Model):
    _inherit = 'product.pricelist.item'
    
    @api.constrains('categ_id', 'pricelist_id')
    def _check_unique_categ_id(self):
        for rec in self:
            # Solo evaluamos si tiene asignada una categoría
            if rec.categ_id:
                domain = [
                    ('id', '!=', rec.id),
                    ('categ_id', '=', rec.categ_id.id),
                    ('pricelist_id', '=', rec.pricelist_id.id), # Opcional: si la unicidad es por lista de precios
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(_("Ya existe una regla para la categoría '%s'.") % rec.categ_id.display_name)