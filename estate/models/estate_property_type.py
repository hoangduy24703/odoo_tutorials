from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate property model type'

    name = fields.Char(string="Property Type", required=True)

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', "The property type name must be unique.")
    ]
