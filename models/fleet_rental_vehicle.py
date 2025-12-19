# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FleetRentalVehicle(models.Model):
    _name = 'fleet.rental.vehicle'
    _description = 'Fleet Rental Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _check_company_auto = True

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    brand_model = fields.Char(
        string='Brand/Model',
    )
    registration_number = fields.Char(
        string='Registration Number',
        required=True,
        copy=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default = lambda x: x.env.company.currency_id

    )
    daily_rent = fields.Monetary(
        string='Daily Rent',
        required=True,
        tracking=True,
        currency_field='currency_id',
        help='Daily rental rate for this vehicle',
    )
    state = fields.Selection(
        [
            ('available', 'Available'),
            ('on_rent', 'On Rent'),
            ('maintenance', 'Maintenance'),
        ],
        string='State',
        default='available',
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    active_contract_id = fields.Many2one(
        'fleet.rental.contract',
        string='Active Contract',
        compute='_compute_active_contract',
        help='Currently active rental contract for this vehicle',
    )

    @api.constrains('registration_number', 'company_id')
    def _check_registration_number_unique(self):
        for vehicle in self:
            if vehicle.registration_number:
                domain = [
                    ('registration_number', '=', vehicle.registration_number),
                    ('id', '!=', vehicle.id),
                ]
                if vehicle.company_id:
                    domain.append(('company_id', '=', vehicle.company_id.id))
                duplicate = self.search(domain, limit=1)
                if duplicate:
                    raise ValidationError(
                        _('Registration Number %s already exists for another vehicle in the same company.') %
                        vehicle.registration_number
                    )

    
    def _compute_active_contract(self):
        for vehicle in self:
            active_contract = self.env['fleet.rental.contract'].search([
                ('vehicle_id', '=', vehicle.id),
                ('state', 'in', ('confirmed', 'invoiced')),
            ], limit=1)
            vehicle.active_contract_id = active_contract if active_contract else False



    def action_set_maintenance(self):
        for vehicle in self:
            if vehicle.state == 'on_rent':
                raise ValidationError(
                    _('Cannot set vehicle to Maintenance while it is On Rent. Please complete or cancel the active contract first.')
                )
            vehicle.write({'state': 'maintenance'})

    def action_set_available(self):
        for vehicle in self:
            if vehicle.state == 'maintenance':
                vehicle.write({'state': 'available'}) 
