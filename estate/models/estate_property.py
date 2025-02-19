from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty (models.Model):
    _name = "estate.property"
    _description =  "test model in traning"
    _order = "id desc"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Availability From", copy=False, default = lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(string="Expected Price", required=True, default = 0.0)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy= False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)", default=0)
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)", default=0)

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
    ], string="State", required=True, default='new', copy=False, compute = "_compute_state", store = True)

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

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(string = "Total area", compute="_compute_total", store=True)

    best_price = fields.Float(string = "Best offer", compute = "_highest_price", store=True)

    color = fields.Integer(string="Color")

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _highest_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.depends("offer_ids")
    def _compute_state(self):
        for record in self:
            if record.state in ["new", "offer_received"] and record.offer_ids:
                record.state = "offer_received"
            elif not record.offer_ids and record.state not in["sold","cancelled"]:
                record.state = "new"

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = 0

    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("A cancelled property cannot be set as sold.")
            record.state = 'sold'
            record.offer_ids.status = 'accepted'

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be cancelled.")
            record.state = 'cancelled'

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0.0)', "Expected price must be strictly positive."),
        ('check_selling_price', 'CHECK(selling_price >= 0)', "Selling price must be positive.")
    ]

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            min_acceptable_price = record.expected_price * 0.9

            if float_compare(record.selling_price, min_acceptable_price, precision_digits=2) == -1:
                raise ValidationError(
                    "Selling price cannot be lower than 90% of the expected price."
                )


    @api.ondelete(at_uninstall=False)
    def _prevent_delete(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise UserError("Cannot delete a property unless its state is 'new' or 'cancelled'.")



