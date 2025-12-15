from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    # job_code = fields.Char(string="Job Code")

    dl_valid_from = fields.Date("Driver License Valid From")
    dl_valid_to = fields.Date("Driver License Valid To")


    document_category = fields.Many2one(
        comodel_name='hr.document.template',
        string='Employee Category'
    )
    employee_typee = fields.Selection(related='document_category.name')

    paid_time_off = fields.Boolean(
        string='Paid Time Off',
        compute='_compute_paid_time_off',
        store=True,
        readonly=False,
    )
    paid_time_off_readonly = fields.Boolean(
        string='Paid Time Off Readonly',
        compute='_compute_paid_time_off_readonly',
    )
    holiday_eligibility = fields.Boolean(
        string='Holiday Eligibility',
        compute='_compute_holiday_eligibility',
        store=True,
        readonly=False,
    )
    holiday_eligibility_readonly = fields.Boolean(
        string='Holiday Eligibility Readonly',
        compute='_compute_holiday_eligibility_readonly',
    )

    # ============================================================
    #   COMPUTE FUNCTIONS (unchanged)
    # ============================================================
    @api.depends('document_category')
    def _compute_holiday_eligibility(self):
        for employee in self:
            if not employee.document_category:
                employee.holiday_eligibility = False
                continue

            if employee.document_category.name == 'us_employee':
                employee.holiday_eligibility = True

    @api.depends('document_category')
    def _compute_holiday_eligibility_readonly(self):
        for employee in self:
            if not employee.document_category:
                employee.holiday_eligibility_readonly = False
                continue

            if employee.document_category.name == 'us_employee':
                employee.holiday_eligibility_readonly = True
            else:
                employee.holiday_eligibility_readonly = False

    @api.depends('document_category')
    def _compute_paid_time_off(self):
        for employee in self:
            if not employee.document_category:
                employee.paid_time_off = False
                continue

            category = employee.document_category.name

            if category == 'us_employee':
                employee.paid_time_off = True
            elif category == 'overseas_contractor':
                employee.paid_time_off = True
            elif category == 'independent_contractor_us':
                employee.paid_time_off = False

    @api.depends('document_category')
    def _compute_paid_time_off_readonly(self):
        for employee in self:
            if not employee.document_category:
                employee.paid_time_off_readonly = False
                continue

            if employee.document_category.name in [
                'us_employee', 'independent_contractor_us', 'overseas_contractor'
            ]:
                employee.paid_time_off_readonly = True
            else:
                employee.paid_time_off_readonly = False


    def write(self, vals):
        if 'document_category' in vals:
            for employee in self:
                if employee.document_category:
                    employee._delete_category_documents()

        result = super(HrEmployee, self).write(vals)

        if 'document_category' in vals and vals.get('document_category'):
            for employee in self:
                employee.action_generate_documents_from_template()

        return result

    @api.model_create_multi
    def create(self, vals_list):
        employees = super(HrEmployee, self).create(vals_list)

        for employee in employees:
            if employee.document_category:
                employee.action_generate_documents_from_template()

        return employees


    def _get_employee_root_folder(self):
        self.ensure_one()
        Documents = self.env['documents.document']

        # Case 1: Root folder already linked by Odoo
        if self.hr_employee_folder_id and self.hr_employee_folder_id.type == 'folder':
            return self.hr_employee_folder_id

        # Case 2: Existing folder linked to employee
        employee_folder = Documents.search([
            ('type', '=', 'folder'),
            ('res_model', '=', 'hr.employee'),
            ('res_id', '=', self.id),
        ], limit=1)

        # Case 3: Folder with employee name
        if not employee_folder:
            employee_folder = Documents.search([
                ('type', '=', 'folder'),
                ('name', '=', self.name),
            ], limit=1)

        # Case 4: Create a new folder
        if not employee_folder:
            employee_folder = Documents.create({
                'name': self.name,
                'type': 'folder',
                'res_model': 'hr.employee',
                'res_id': self.id,
            })

        if not self.hr_employee_folder_id:
            self.hr_employee_folder_id = employee_folder

        return employee_folder


    def _delete_category_documents(self):
        self.ensure_one()
        Documents = self.env['documents.document']

        employee_folder = self._get_employee_root_folder()

        # 1. Delete all documents
        docs = Documents.search([
            ('res_model', '=', 'hr.employee'),
            ('res_id', '=', self.id),
            ('type', '!=', 'folder'),
        ])
        if docs:
            docs.unlink()

        # 2. Delete all subfolders under employee folder
        subfolders = Documents.search([
            ('type', '=', 'folder'),
            ('folder_id', '=', employee_folder.id),
            ('res_model', '=', 'hr.employee'),
            ('res_id', '=', self.id),
        ])
        if subfolders:
            subfolders.unlink()


    def action_generate_documents_from_template(self):
        self.ensure_one()

        if not self.document_category:
            raise ValidationError(_('Please select a Document Category first.'))

        if not self.work_contact_id:
            raise ValidationError(_('Employee must have a linked contact.'))

        template_lines = self.document_category.document_ids
        if not template_lines:
            raise ValidationError(_('The selected template contains no documents.'))

        Documents = self.env['documents.document']
        employee_folder = self._get_employee_root_folder()

        created_documents = Documents.browse()
        subfolder_cache = {}  # avoid duplicate folders

        for line in template_lines:
            if not line.document_file:
                continue

            # --------------------------------------------
            # Determine target folder
            # --------------------------------------------
            folder_label = dict(line._fields['folder_id'].selection).get(line.folder_id)
            folder_name = folder_label.strip() if folder_label else False
            target_folder = employee_folder

            if folder_name:
                if folder_name not in subfolder_cache:
                    subfolder = Documents.search([
                        ('type', '=', 'folder'),
                        ('name', '=', folder_name),
                        ('folder_id', '=', employee_folder.id),
                        ('res_model', '=', 'hr.employee'),
                        ('res_id', '=', self.id),
                    ], limit=1)

                    if not subfolder:
                        subfolder = Documents.create({
                            'name': folder_name,
                            'type': 'folder',
                            'folder_id': employee_folder.id,
                            'res_model': 'hr.employee',
                            'res_id': self.id,
                        })

                    subfolder_cache[folder_name] = subfolder

                target_folder = subfolder_cache[folder_name]

            # --------------------------------------------
            # Create document inside folder
            # --------------------------------------------
            doc_vals = {
                'name': line.name or line.file_name or 'Untitled Document',
                'datas': line.document_file,
                'partner_id': self.work_contact_id.id,
                'res_model': 'hr.employee',
                'res_id': self.id,
                'folder_id': target_folder.id,
            }

            # Tags
            if line.tags:
                tag_names = [t.strip() for t in line.tags.split(',') if t.strip()]
                tags = self.env['documents.tag'].search([('name', 'in', tag_names)])
                if tags:
                    doc_vals['tag_ids'] = [(6, 0, tags.ids)]

            document = Documents.create(doc_vals)
            created_documents |= document

        # --------------------------------------------
        # Show notification
        # --------------------------------------------
        if created_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('%s document(s) created successfully.') % len(created_documents),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('No documents were created.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
