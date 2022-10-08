
from datetime import date, datetime, timedelta
import email
from email.policy import default
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class SalonAlconsoft(models.Model):
    _inherit = 'salon.order'

    # alconor: 23/sep/2022
    # user_id = fields.Many2one('res.users', string="Chair User")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="E-Mail")

    def salon_saleorder_create(self):
        if self.partner_id:
            supplier = self.partner_id
        else:
            supplier = self.partner_id.search([("name", "=", "Salon Default Customer")])
        lines = []
        product_id = self.env['product.product'].search([("name", "=", "Salon Service")])
        for records in self.order_line:
            if product_id.property_account_income_id.id:
                income_account = product_id.property_account_income_id.id
            elif product_id.categ_id.property_account_income_categ_id.id:
                income_account = product_id.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                                     product_id.id))

            value = (0, 0, {
                        'name': records.service_id.name,
                        'price_unit': records.price,
                        'product_uom_qty': 1,
                        'product_id': product_id.id,
                    })
            lines.append(value)

        invoice_line = {
            'state': 'draft',
            'partner_id': supplier.id,
            'user_id': self.env.user.id,
            'origin': self.name,
            'client_order_ref': self.chair_id.name,
            'reference': "ref_pago_interna_salon",
            'note': self.chair_user.name,
            'chair_user_id': self.chair_user.id,
            'chair_id': self.chair_id.id,
            'order_line': lines,
        }
        inv = self.env['sale.order'].create(invoice_line)


        imd = self.env['ir.model.data']

        action = imd.xmlid_to_object('account.action_move_out_invoice_type')
        result = {
            'name': action.name,
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id':inv.id,
            'res_model': 'sale.order',
        }

        self.inv_stage_identifier = True
        self.stage_id = 3
        invoiced_records = self.env['salon.order'].search([('stage_id', 'in', [3, 4]),
                                                           ('chair_id', '=', self.chair_id.id)])
        total = 0
        for rows in invoiced_records:
            invoiced_date = str(rows.date)
            invoiced_date = invoiced_date[0:10]
            if invoiced_date == str(date.today()):
                total = total + rows.price_subtotal
        self.chair_id.collection_today = total
        self.chair_id.number_of_orders = len(self.env['salon.order'].search([("chair_id", "=", self.chair_id.id),
                                                                             ("stage_id", "in", [2, 3])]))

        return result
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.phone = self.partner_id.mobile
        self.email = self.partner_id.email
        self.customer_name = self.partner_id.name
        return

    @api.onchange('chair_id')
    def _onchange_chair_id(self):
        self.chair_user = self.chair_id.user_of_chair
        self.color = self.chair_id.color
        return

class BoookingAlconsoft(models.Model):
    _inherit = 'salon.booking'

    partner_id = fields.Many2one('res.partner', string="Customer", required=False,
                                 help="If the customer is a regular customer, "
                                      "then you can add the customer in your database")
    user_id = fields.Many2one('res.users', string="Chair User")
    color = fields.Integer('Color Index')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.phone = self.partner_id.mobile
        self.email = self.partner_id.email
        self.name = self.partner_id.name
        return

    @api.onchange('chair_id')
    def _onchange_chair_id(self):
        self.user_id = self.chair_id.user_of_chair
        self.color = self.chair_id.color
        return

    
    def booking_approve(self):
        
        salon_order_obj = self.env['salon.order']
        salon_service_obj = self.env['salon.order.lines']
        order_data = {
            'customer_name': self.name,
            'chair_id': self.chair_id.id,
            'start_time': self.time,
            'date': date.today(),
            'stage_id': 1,
            'booking_identifier': True,
            'color': self.color,
            'partner_id': self.partner_id.id,
            'chair_user': self.user_id.id,
        }
        order = salon_order_obj.create(order_data)
        for records in self.services:
            service_data = {
                'service_id': records.id,
                'time_taken': records.time_taken,
                'price': records.price,
                'price_subtotal': records.price,
                'salon_order': order.id,
            }
            salon_service_obj.create(service_data)
        template = self.env.ref('salon_management.salon_email_template_approved')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.state = "approved"

class SalonChair(models.Model):
    _inherit = 'salon.chair'

    user_id = fields.Many2one('res.users', string="Chair User")
    chair_id = fields.Many2one('salon.chair', string="Chair", required=True)
    color = fields.Integer('Color Index')

class SaleOrderSalon(models.Model):
    _inherit = 'sale.order'

    chair_user_id = fields.Many2one('res.users', string="Chair User")
    chair_id = fields.Many2one('salon.chair', string="Chair", required=True)

class SalonAlconsoftPartner(models.Model):
	_inherit = 'res.partner'

	def action_view_sale_order(self):
	    return
    
class SanlonAlconsoftPartner2(models.Model):
    _inherit = 'res.partner'

    partner_salon = fields.Boolean(string="Es Cliente Salon", default=True, required=True)

class SalonContacts(models.Model):
    _name = 'calendar.chairs'
    _description = 'Calendar Chairs'

    user_id = fields.Many2one('res.users', 'Me', required=True, default=lambda self: self.env.user)
    #partner_id = fields.Many2one('res.partner', 'Employee', required=True)
    chair_id = fields.Many2one('salon.chair', string="Chair", required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('user_id_chair_id_unique', 'UNIQUE(user_id, chair_id)', 'A user cannot have the same chair twice.')
    ]

    @api.model
    def unlink_from_chair_id(self, chair_id):
        return self.search([('chair_id', '=', chair_id)]).unlink()