from odoo import models, fields, api
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection([
        ('accepted', "Accepted"),
        ('refused', "Refused")
    ], string="Status", copy=False)

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    validity = fields.Integer(string = "Validity (days)", default = 7)
    date_deadline = fields.Date(string = "Deadline", compute = "_compute_deadline", inverse = "_compute_validity")

    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add((record.create_date.date() or fields.Date.today()),days = (record.validity or 0))

    def _compute_validity(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - (record.create_date.date() or fields.Date.today())).days
    

    @api.onchange("date_deadline")
    def _onchange_date_deadline(self):
        for record in self:
            if record.date_deadline and record.date_deadline < fields.Date.today():
                record.date_deadline = record._origin.date_deadline  # Quay về giá trị trước đó
                return {
                    'warning': {
                        'title': "Invalid Date",
                        'message': "The deadline date cannot be in the past. Please select a valid date.",
                    }
                }