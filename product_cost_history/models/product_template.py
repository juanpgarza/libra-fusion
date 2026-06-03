from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        # 1. Verificar si el costo de reposición viene en el diccionario de valores a actualizar
        if 'replenishment_base_cost' in vals:
            history_vals_list = []
            
            # 2. Iterar sobre los registros actuales ANTES de que se aplique el write
            for record in self:
                old_cost = record.replenishment_base_cost
                new_cost = vals.get('replenishment_base_cost')
                
                # Solo registramos si hubo un cambio real en el valor
                if old_cost != new_cost:
                    history_vals_list.append({
                        'product_tmpl_id': record.id,
                        'old_cost': old_cost,
                        'new_cost': new_cost,
                        'user_id': self.env.uid,
                    })
            
            # 3. Ejecutar el write original para guardar los datos en el producto
            res = super(ProductTemplate, self).write(vals)
            
            # 4. Crear los registros del historial en bloque (optimizado para carga masiva)
            if history_vals_list:
                self.env['product.replenishment.cost.history'].sudo().create(history_vals_list)
                
            return res

        # Si no se tocó el costo, el write funciona con normalidad
        return super(ProductTemplate, self).write(vals)