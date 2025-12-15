from odoo import api, fields, models


class HrVersion(models.Model):
    """Extends the 'hr.version' model to add onchange methods to record
    changes in contract-related fields (wage, name, date_start, date_end) and
    stores the historical data in the 'salary.history' and 'contract.history'
    models for HR contracts."""
    _inherit = 'hr.version'

    parent_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        related='employee_id.parent_id',
        store=True
    )

    contract_reference = fields.Char(
        string='Contract/Period Reference',
        help='Reference to identify the contract or period'
    )

    job_description = fields.Text(
        string='Job Description',
        related='employee_id.job_description',
    )
