from odoo import models, fields, api

class EstateProperty (models.Model):
    _name = "estate.property"
    _description =  "test model in traning"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Availability From", copy=False, default = lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy= False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        string="Garden Orientation"
    )

    active = fields.Boolean(default=True)

    state = fields.Selection([
    ('new', 'New'),
    ('offer_received', 'Offer Received'),
    ('offer_accepted', 'Offer Accepted'),
    ('sold', 'Sold'),
    ('cancelled', 'Cancelled')
    ], string="State", required=True, default='new', copy=False)

    property_type_id = fields.Many2one('estate.property.type', string="Property Type")

    buyer_id = fields.Many2one(
        "res.partner", 
        string="Buyer", 
        copy=False
    )
    
    salesperson_id = fields.Many2one(
        "res.users", 
        string="Salesperson", 
        default=lambda self: self.env.user
    )

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
