# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class FleetRentalContract(models.Model):
    _name = 'fleet.rental.contract'
    _description = 'Fleet Rental Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'
    _check_company_auto = True

    name = fields.Char(
        string='Contract Number',
        readonly=True,
        default=lambda self: _('New'),
        copy=False,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    vehicle_id = fields.Many2one(
        'fleet.rental.vehicle',
        string='Vehicle',
        required=True,
        check_company=True,
        domain=[('state', '=', 'available')],
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today(),
        tracking=True,
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_currency_id',
        store=True,
        readonly=False
    )

    @api.depends('vehicle_id.currency_id')
    def _compute_currency_id(self):
        for contract in self:
            if contract.vehicle_id:
                contract.currency_id = contract.vehicle_id.currency_id
            else:
                contract.currency_id = contract.env.company.currency_id


    rent_cost = fields.Monetary(
        string='Rent Cost',
        compute='_compute_rent_cost',
        store=True, readonly=False,
        currency_field='currency_id',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('invoiced', 'Invoiced'),
            ('done', 'Done'),
        ],
        string='State',
        default='draft',
        copy=False,
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
        copy=False,
        tracking=True,
    )
    payment_state = fields.Selection(
        related='invoice_id.payment_state',
        string='Payment State',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        
    )

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id


    @api.depends('start_date', 'end_date', 'vehicle_id.daily_rent')
    def _compute_rent_cost(self):
        for contract in self:
            if contract.start_date and contract.end_date and contract.vehicle_id.daily_rent:
                delta = contract.end_date - contract.start_date
                days = delta.days + 1 
                contract.rent_cost = days * contract.vehicle_id.daily_rent
            else:
                contract.rent_cost = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.rental.contract') or _('New')
        return super().create(vals)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for contract in self:
            if contract.start_date and contract.end_date:
                if contract.end_date < contract.start_date:
                    raise ValidationError(_('End Date must be after Start Date.'))

    # @api.constrains('vehicle_id', 'state')
    # def _check_vehicle_availability(self):
    #     for contract in self:
    #         if contract.state == 'draft' and contract.vehicle_id:
    #             if contract.vehicle_id.state != 'available':
    #                 raise ValidationError(
    #                     _('Vehicle %s is not available. Current state: %s') %
    #                     (contract.vehicle_id.name, dict(contract.vehicle_id._fields['state'].selection)[contract.vehicle_id.state])
    #                 )

    def action_confirm(self):
        for contract in self:
            if contract.state != 'draft':
                raise UserError(_('Only draft contracts can be confirmed.'))
            if contract.vehicle_id.state != 'available':
                raise UserError(_('Vehicle is not available for rental.'))
            
            contract.write({
                'state': 'confirmed',
            })
            contract.vehicle_id.write({
                'state': 'on_rent',
            })

    def action_create_invoice(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Invoice can only be created for confirmed contracts.'))
        if self.invoice_id:
            raise UserError(_('Invoice already exists for this contract.'))
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': _('Rental Contract: %s - %s to %s') % (
                    self.vehicle_id.name,
                    self.start_date,
                    self.end_date
                ),
                'quantity': 1,
                'price_unit': self.rent_cost,
                'product_id': False,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        
        self.write({
            'invoice_id': invoice.id,
            'state': 'invoiced',
        })

        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_done(self):
        for contract in self:
            if contract.state not in ('confirmed', 'invoiced'):
                raise UserError(_('Only confirmed or invoiced contracts can be marked as done.'))
            
            contract.write({
                'state': 'done',
            })
            contract.vehicle_id.write({
                'state': 'available',
            })

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_('No invoice linked to this contract.'))
        
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

