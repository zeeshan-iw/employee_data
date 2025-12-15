from odoo import models, fields

class HrEmployeeDepartmentHistory(models.Model):
    _name = "hr.employee.department.history"
    _description = "Employee Department History"
    _order = "start_date desc"

    employee_id = fields.Many2one("hr.employee", required=True)
    department_id = fields.Many2one("hr.department", required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    notes = fields.Char()
