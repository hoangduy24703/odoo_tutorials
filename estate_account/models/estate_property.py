from odoo import models, fields, api, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty (models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        res = super().action_sold()

        for record in self:
            # Kiểm tra nếu property đã bán thì mới tạo hóa đơn
            if record.state == 'sold':
                # Lấy thông tin cần thiết
                partner_id = record.buyer_id.id
                selling_price = record.selling_price
                journal_id = self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id

                # Tạo các dòng hóa đơn (invoice lines)
                invoice_lines = [
                    # Phí hoa hồng 6% của giá bán
                    Command.create({
                        'name':'Commission Fee (6% of Selling Price)',
                        'quantity': 1,
                        'price_unit': selling_price * 0.06,
                    }),
                    # Phí hành chính cố định 100.00
                    Command.create({
                        'name':'Administrative Fee',
                        'quantity': 1,
                        'price_unit': 100.00,
                    })
                ]

                # Tạo hóa đơn (account.move)
                invoice_vals = {
                    'partner_id': partner_id,
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,
                    'invoice_line_ids': invoice_lines
                }
                self.env['account.move'].create(invoice_vals)

        return res
