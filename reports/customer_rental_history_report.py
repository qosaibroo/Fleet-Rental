# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class CustomerRentalHistoryReport(models.AbstractModel):
    _name = 'report.fleet_rental.customer_rental_history_report'
    _description = 'Customer Rental History Report'

    def _get_report_values(self, docids, data=None):
        contracts = self.env['fleet.rental.contract'].search([
            ('state', 'in', ['confirmed', 'done'])
        ])
        
        customer_data = {}
        for contract in contracts:
            customer_id = contract.customer_id.id
            if customer_id not in customer_data:
                customer_data[customer_id] = {
                    'customer_name': contract.customer_id.name,
                    'contracts': [],
                    'first_rental_date': False,
                    'last_rental_date': False,
                    'total_contract_value': 0.0,
                    'contract_count': 0,
                }
            
            customer_data[customer_id]['contracts'].append({
                'start_date': contract.start_date,
                'rent_cost': contract.rent_cost,
            })
            customer_data[customer_id]['total_contract_value'] += contract.rent_cost
            customer_data[customer_id]['contract_count'] += 1
        
        report_data = []
        for customer_id, data in customer_data.items():
            if data['contracts']:
                sorted_contracts = sorted(data['contracts'], key=lambda x: x['start_date'])
                
                first_rental_date = sorted_contracts[0]['start_date']
                last_rental_date = sorted_contracts[-1]['start_date']
                avg_contract_value = data['total_contract_value'] / data['contract_count']
                
                customer = self.env['res.partner'].browse(customer_id)
                current_balance = customer.credit - customer.debit
                
                report_data.append({
                    'customer_name': data['customer_name'],
                    'first_rental_date': first_rental_date,
                    'last_rental_date': last_rental_date,
                    'avg_contract_value': avg_contract_value,
                    'current_balance': current_balance,
                })
        
        report_data.sort(key=lambda x: x['customer_name'])
        
        return {
            'doc_ids': list(customer_data.keys()),
            'doc_model': 'res.partner',
            'report_data': report_data,
            'date': fields.Date.today(),
        }

