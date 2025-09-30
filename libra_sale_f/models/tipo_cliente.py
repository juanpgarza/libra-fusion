from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class TipoCliente(models.Model):
	_name = 'sale.tipo.cliente'
	_description = 'Tipo de cliente'

	name = fields.Char('Nombre')