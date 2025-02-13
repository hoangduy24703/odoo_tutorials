from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate property model type'

    name = fields.Char(string="Property Type", required=True)