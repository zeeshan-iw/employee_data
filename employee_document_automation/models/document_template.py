from odoo import models, fields, api


class DocumentTemplate(models.Model):
    _name = 'hr.document.template'
    _description = 'Employee Document Template'
    _rec_name = 'display_name'

    name = fields.Selection([
        ('W2_employee', 'W2 Employee'),
        ('independent_contractor_us', 'Independent Contractor – US (1099)'),
        ('overseas_contractor', 'Overseas Independent Contractor'),
        ('staffing_employee', 'Staffing Employee'),
        ('intern', 'Intern'),
        ('temp_to_hire', 'Temp-to-Hire'),
        ('H1B','H1B')
    ], string='Policy Group Name', required=True)

    display_name = fields.Char(
        string="Label",
        compute="_compute_display_name",
        store=True
    )

    @api.depends('name')
    def _compute_display_name(self):
        selection_dict = dict(self._fields['name'].selection)
        for rec in self:
            rec.display_name = selection_dict.get(rec.name, rec.name)



    document_ids = fields.One2many(
        'hr.document.template.line',
        'template_id',
        string='Documents'
    )
    employee_count = fields.Integer(
        string="Employees",
        compute="_compute_employee_count",
    )

    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = self.env['hr.employee'].search_count([
                ('document_category', '=', rec.id)
            ])

    def action_view_employees(self):
        """Open employees linked to this document template."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f"Employees • {self.name}",
            'res_model': 'hr.employee',
            'view_mode': 'list,form',
            'domain': [('document_category', '=', self.id)],
            'context': {'default_document_category': self.id},
        }





class DocumentTemplateLine(models.Model):
    _name = 'hr.document.template.line'
    _description = 'Document Template Line'

    template_id = fields.Many2one(
        'hr.document.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(string='Document', required=True)

    document_file = fields.Binary(
        string='Upload File',
        required=False,
        attachment=True,
        help='Upload the document file (PDF, DOC, etc.)'
    )

    file_name = fields.Char(string='File Name')

    folder_id = fields.Selection([
        ('hr_docs','HR Docs'),
        ('employee_docs','Employee Docs'),
    ],
        string='Folder Name',
        required=True
    )

    folder_display = fields.Char(
        string="Folder Label",
        compute="_compute_folder_display",
        store=True
    )

    @api.depends('folder_id')
    def _compute_folder_display(self):
        selection_dict = dict(self._fields['folder_id'].selection)
        for rec in self:
            rec.folder_display = selection_dict.get(rec.folder_id, rec.folder_id)

    tags = fields.Char(
        string='Tags',
        help='Comma-separated tags to apply (if Documents app is installed)'
    )
