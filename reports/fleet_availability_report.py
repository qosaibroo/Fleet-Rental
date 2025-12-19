# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError


class FleetAvailabilitySqlReport(models.Model):
    """SQL view backing the fleet availability list view."""

    _name = 'fleet.availability.report'
    _description = 'Fleet Availability Report'
    _auto = False
    _rec_name = 'vehicle_name'
    _order = 'vehicle_name'

    vehicle_id = fields.Many2one(
        'fleet.rental.vehicle',
        string='Vehicle',
        readonly=True,
    )
    vehicle_name = fields.Char(
        string='Vehicle Name',
        readonly=True,
    )
    brand_model = fields.Char(
        string='Brand/Model',
        readonly=True,
    )
    registration_number = fields.Char(
        string='Registration Number',
        readonly=True,
    )
    state = fields.Selection(
        [
            ('available', 'Available'),
            ('on_rent', 'On Rent'),
            ('maintenance', 'Maintenance'),
        ],
        string='Current Status',
        readonly=True,
    )
    expected_return_date = fields.Date(
        string='Expected Return Date',
        readonly=True,
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    v.id AS id,
                    v.id AS vehicle_id,
                    v.name AS vehicle_name,
                    v.brand_model,
                    v.registration_number,
                    v.state,
                    CASE
                        WHEN v.state = 'on_rent' THEN lc.end_date
                        ELSE NULL
                    END AS expected_return_date
                FROM fleet_rental_vehicle v
                LEFT JOIN LATERAL (
                    SELECT
                        c.end_date
                    FROM fleet_rental_contract c
                    WHERE c.vehicle_id = v.id
                        AND c.state IN ('confirmed', 'invoiced')
                    ORDER BY c.start_date DESC
                    LIMIT 1
                ) AS lc ON TRUE
            )
        """)



