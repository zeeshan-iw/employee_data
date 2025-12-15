# models/hr_manager_history.py
from odoo import models, fields, api


class HrManagerHistory(models.Model):
    _name = 'hr.manager.history'
    _description = 'Manager History'
    _order = 'date_from desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    contract_reference = fields.Char(string='Contract/Period Reference')  # Custom reference field
    manager_id = fields.Many2one('hr.employee', string='Manager')
    date_from = fields.Datetime(string='From Date', required=True)
    date_to = fields.Datetime(string='To Date')
    modification_date = fields.Datetime(string='Modification Date', default=fields.Datetime.now)

    @api.model
    def create_manager_history(self, employee_id, old_manager_id, new_manager_id, contract_ref=None):
        """Create manager history record when manager changes"""
        # Close previous record if exists
        last_record = self.search([
            ('employee_id', '=', employee_id),
            ('date_to', '=', False)
        ], limit=1)

        if last_record:
            last_record.date_to = fields.Datetime.now()

        # Create new record
        if new_manager_id:
            self.create({
                'employee_id': employee_id,
                'manager_id': new_manager_id,
                'contract_reference': contract_ref or f"Period-{fields.Date.today()}",
                'date_from': fields.Datetime.now(),
            })