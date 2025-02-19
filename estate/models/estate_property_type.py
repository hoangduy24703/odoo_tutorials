from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate property model type'
    _order = "sequence, name"

    name = fields.Char(string="Property Type", required=True)

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', "The property type name must be unique.")
    ]

    property_ids = fields.One2many('estate.property', 'property_type_id', string='Property')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    offer_ids = fields.One2many('estate.property.offer',
                                'property_type_id',
                                string="Offers")

    offer_count = fields.Integer( string="Offer Count",
                                compute="_compute_offer_count",
                                store=True)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])


