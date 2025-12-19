# Fleet Rental Management Module

## Overview
This Odoo 18 Enterprise module provides comprehensive fleet rental management functionality, including vehicle tracking, rental contracts, accounting integration, and analytical reporting.

## Features

### 1. Vehicle Management (`fleet.rental.vehicle`)
- Track vehicle information (name, brand/model, registration number)
- Manage vehicle states: Available, On Rent, Maintenance
- Set daily rental rates
- View rental contract history

### 2. Rental Contracts (`fleet.rental.contract`)
- Create and manage rental agreements
- Automatic rent cost calculation based on rental days
- State workflow: Draft → Confirmed → Invoiced → Done
- Integration with Odoo Accounting for invoice generation
- Track payment status

### 3. Business Logic
- **State Management:**
  - Draft → Confirmed: Automatically sets vehicle state to "On Rent"
  - Any → Done: Automatically sets vehicle state back to "Available"
  
- **Invoice Integration:**
  - Create invoice button (visible only to Managers)
  - Generates customer invoice in Draft state
  - Automatically links invoice to contract
  - Updates contract state to "Invoiced"

### 4. Reporting
- **Fleet Availability Analysis:**
  - Lists all vehicles in the system
  - Shows current status
  - Displays expected return date for vehicles on rent
  
- **Customer Rental History (BONUS):**
  - Lists customers with rental history
  - Shows first and last rental dates
  - Calculates average contract value
  - Displays current balance (receivable)

### 5. Security
- **Groups:**
  - Rental / User: Can read, create, and update contracts (no delete)
  - Rental / Manager: Full access including invoice creation
  
- **Access Rights:**
  - Users cannot delete contracts
  - Users cannot see "Create Invoice" button
  - Managers have full access

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Fleet Rental Management" module

## Dependencies
- `base`
- `account`
- `fleet` (optional, for enhanced fleet management)

## Module Structure

```
ltc_fleet_rental_management/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   └── fleet_rental_data.xml          # Sequences
├── models/
│   ├── __init__.py
│   ├── fleet_rental_vehicle.py       # Vehicle model
│   └── fleet_rental_contract.py      # Contract model
├── reports/
│   ├── __init__.py
│   ├── fleet_availability_report.py  # Fleet availability report
│   ├── fleet_availability_report.xml
│   ├── customer_rental_history_report.py  # Customer history report
│   └── customer_rental_history_report.xml
├── security/
│   ├── ir.model.access.csv           # Access rights
│   └── fleet_rental_security.xml     # Groups and record rules
└── views/
    ├── fleet_rental_vehicle_views.xml # Vehicle views
    ├── fleet_rental_contract_views.xml # Contract views
    └── fleet_rental_menus.xml        # Menu structure
```

## Usage

### Creating a Vehicle
1. Navigate to **Fleet Rental > Vehicles**
2. Click **Create**
3. Fill in vehicle details:
   - Name
   - Brand/Model
   - Registration Number (must be unique)
   - Daily Rent
   - State (default: Available)

### Creating a Rental Contract
1. Navigate to **Fleet Rental > Contracts**
2. Click **Create**
3. Select Customer and Vehicle
4. Set Start Date and End Date
5. Rent cost is automatically calculated
6. Click **Confirm** to activate the contract
7. (Manager only) Click **Create Invoice** to generate invoice
8. Click **Mark as Done** when rental is completed

### Generating Reports
1. **Fleet Availability Analysis:**
   - Navigate to **Fleet Rental > Reporting > Fleet Availability Analysis**
   - Click **Print** to generate PDF report

2. **Customer Rental History:**
   - Navigate to **Fleet Rental > Reporting > Customer Rental History**
   - Click **Print** to generate PDF report

## Technical Details

### Models

#### `fleet.rental.vehicle`
- Inherits: `mail.thread`, `mail.activity.mixin`
- Multi-company support enabled
- Key fields: name, brand_model, registration_number, daily_rent, state

#### `fleet.rental.contract`
- Inherits: `mail.thread`, `mail.activity.mixin`
- Multi-company support enabled
- Automatic contract number generation via sequence
- Computed fields: rent_cost, rental_days
- Related field: payment_state (from invoice)

### State Workflow
- **Draft**: Initial state, contract can be edited
- **Confirmed**: Contract is active, vehicle is on rent
- **Invoiced**: Invoice has been created
- **Done**: Contract completed, vehicle available again

### Invoice Integration
- Invoice is created in Draft state
- Invoice line includes rental period details
- Payment state is automatically tracked via related field
- Invoice can be viewed directly from contract

## Version
- **Odoo Version:** 18.0 Enterprise
- **Module Version:** 0.1

## Author
LTC

