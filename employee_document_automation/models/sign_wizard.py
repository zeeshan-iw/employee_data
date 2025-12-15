from odoo import models, fields, api, _
from odoo import Command
from odoo.exceptions import UserError


class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees",
        help="Select one or more employees. A separate sign request will be created for each employee."
    )

    def _create_requests_for_employees(self):
        self.ensure_one()

        if not self.employee_ids:
            return self.env['sign.request']

        requests = self.env['sign.request']

        for employee in self.employee_ids:
            if not employee.work_contact_id:
                raise UserError(
                    _("Employee %s has no Work Contact assigned.") % employee.display_name
                )

            partner = employee.work_contact_id

            signer_vals = {
                'partner_id': partner.id,
                'role_id': self.env.ref('sign.sign_item_role_default').id,
                'mail_sent_order': 1,
            }

            request_vals = {
                'template_id': self.template_id.id,
                'request_item_ids': [Command.create(signer_vals)],
                'reference': f"{self.template_id.name} - {employee.name}",
                'subject': self.subject,
                'message': self.body,
                'message_cc': self.message_cc,
                'attachment_ids': [Command.set(self.attachment_ids.ids)],
                'validity': self.validity,
                'reminder': self.reminder,
                'reminder_enabled': self.reminder_enabled,
                'reference_doc': f"hr.employee,{employee.id}",
                'certificate_reference': self.certificate_reference,
            }

            req = self.env['sign.request'].create(request_vals)

            if self.cc_partner_ids:
                req.message_subscribe(partner_ids=self.cc_partner_ids.ids)

            requests |= req

        return requests

    def send_request(self):
        self.ensure_one()

        # If employees selected: mass sending
        if self.employee_ids:
            requests = self._create_requests_for_employees()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': _("Signature Requests Sent"),
                    'message': _("Successfully created %s signature request(s).") % len(requests),
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
                },
            }

        # Otherwise: default Odoo behavior
        return super().send_request()
