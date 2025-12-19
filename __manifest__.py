# -*- coding: utf-8 -*-
{
    'name': 'Fleet Rental Management',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Manage vehicle rentals with contracts, invoicing, and reporting',
    'description': """
Fleet Rental Management
=======================
This module provides comprehensive fleet rental management functionality:

* Vehicle Management
    - Track vehicle information (name, brand/model, registration number)
    - Manage vehicle states (Available, On Rent, Maintenance)
    - Set daily rental rates

* Rental Contracts
    - Create and manage rental agreements
    - Automatic rent cost calculation
    - State workflow (Draft → Confirmed → Invoiced → Done)
    - Integration with Odoo Accounting

* Accounting Integration
    - Generate customer invoices from contracts
    - Track payment status
    - Link invoices to contracts

* Reporting
    - Fleet Availability Analysis
    - Customer Rental History (Analytical Report)
    """,
    'author': 'LTC',
    'website': '',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'data/fleet_rental_data.xml',
        'security/fleet_rental_security.xml',
        'security/ir.model.access.csv',
        'reports/fleet_availability_report.xml',
        'reports/customer_rental_history_report.xml',
        'views/fleet_rental_vehicle_views.xml',
        'views/fleet_rental_contract_views.xml',
        'views/fleet_rental_menus.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

