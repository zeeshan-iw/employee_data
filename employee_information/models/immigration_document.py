from odoo import models, fields, api
import base64
import mimetypes

class ImmigrationDocument(models.Model):
    _name = "immigration.document"
    _description = "Immigration Document Repository"
    _order = "upload_datetime desc"

    employee_id = fields.Many2one("hr.employee", string="Employee", ondelete="cascade")
    document_type = fields.Selection([
        ('passport', 'Copy of Passport'),
        ('visa_stamp', 'Visa Stamps'),
        ('i94', 'Most Recent I-94'),
        ('i129', 'H-1B Petition (I-129)'),
        ('i797', 'Approval Notice (I-797)'),
        ('lca', 'Certified LCA'),
        ('pwd', 'Prevailing Wage Determination'),
        ('support_letter', 'Employer Support Letter'),
        ('rfe_letter', 'RFE Letter'),
        ('rfe_response', 'RFE Response'),
        ('attorney_emails', 'Attorney Email Threads'),
        ('other', 'Other Document'),
    ], required=True)

    file = fields.Binary("File", attachment=True)
    file_name = fields.Char("File Name")
    file_size = fields.Integer(string="File Size", compute='_compute_file_info', store=True)
    file_type = fields.Char(string="File Type", compute='_compute_file_info', store=True)

    @api.depends('file', 'file_name')
    def _compute_file_info(self):
        for record in self:
            if record.file:
                record.file_size = len(base64.b64decode(record.file))
                if record.file_name:
                    mime_type, _ = mimetypes.guess_type(record.file_name)
                    record.file_type = mime_type or 'application/octet-stream'
                else:
                    record.file_type = 'application/octet-stream'
            else:
                record.file_size = 0
                record.file_type = False

    def action_preview_document(self):
        self.ensure_one()

        # For PDFs and images, open in a new tab/modal
        if self.file_type and (self.file_type.startswith('image/') or self.file_type == 'application/pdf'):
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%s/file/%s?download=false' % (
                    self._name, self.id, self.file_name
                ),
                'target': 'new',
            }
        else:
            # For other file types, fallback to download
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%s/file/%s?download=true' % (
                    self._name, self.id, self.file_name
                ),
                'target': 'self',
            }
    version = fields.Integer(string="Version", default=1)
    notes = fields.Text(string="Notes")
    uploaded_by = fields.Many2one("res.users", string="Uploaded By", default=lambda self: self.env.user)
    upload_datetime = fields.Datetime(string="Uploaded On", default=lambda self: fields.Datetime.now())

    @api.model
    def create(self, vals):
        # Support batch creation
        if isinstance(vals, list):
            records = []
            for v in vals:
                existing = self.search([
                    ('employee_id', '=', v.get('employee_id')),
                    ('document_type', '=', v.get('document_type'))
                ], order='version desc', limit=1)
                if existing:
                    v['version'] = existing.version + 1
                records.append(super().create(v))
            return records
        else:
            existing = self.search([
                ('employee_id', '=', vals.get('employee_id')),
                ('document_type', '=', vals.get('document_type'))
            ], order='version desc', limit=1)
            if existing:
                vals['version'] = existing.version + 1
            return super().create(vals)

