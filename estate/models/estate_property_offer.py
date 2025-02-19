from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection([
        ('accepted', "Accepted"),
        ('refused', "Refused")
    ], string="Status", copy=False)

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    validity = fields.Integer(string = "Validity (days)", default = 7)
    date_deadline = fields.Date(string = "Deadline", compute = "_compute_deadline", inverse = "_compute_validity")

    property_type_id = fields.Many2one( 'estate.property.type',
                                    string="Property Type",
                                    related="property_id.property_type_id",
                                    store=True)


    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            record.create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = fields.Date.add((record.create_date.date() or fields.Date.today()),days = (record.validity or 0))

    def _compute_validity(self):
        for record in self:
            if record.date_deadline:
                record.create_date = record.create_date.date() if record.create_date else fields.Date.today()
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

    def action_accept(self):
        for record in self:
            if record.property_id.state in ["sold", "cancelled"]:
                raise UserError("Can not chang the state of an offer that was canceled or sold.")

            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'

        other_offers = self.search([
            ('property_id', '=', record.property_id.id),
            ('id', '!=', record.id),
            ('status', '=', 'accepted')
        ])
        other_offers.write({'status': 'refused'})

    def action_refuse(self):
        for record in self:
            if record.property_id.state in ["sold", "cancelled"]:
                raise UserError("Can not chang the state of an offer that was canceled or sold.")

            record.status = 'refused'

            other_offers = self.search([
                ('property_id', '=', record.property_id.id),
                ('id', '!=', record.id),
                ('status', '=', 'accepted')
            ])

            if not other_offers:
                record.property_id.selling_price = 0
                record.property_id.buyer_id = ''
                record.property_id.state = 'offer_received'
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', "Offer price must be strictly positive.")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("property_id") and vals.get("price"):
                prop = self.env["estate.property"].browse(vals["property_id"])

                # Kiểm tra nếu có offer nào đã tồn tại
                if prop.offer_ids:
                    max_offer = max(prop.mapped("offer_ids.price"))
                    if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                        raise UserError("The offer must be higher than %.2f" % max_offer)

                # Cập nhật trạng thái của property
                prop.state = "offer_received"

        return super().create(vals_list)
