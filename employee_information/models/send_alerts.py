# models/expiration_alert.py
from odoo import models, fields, api
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

ALERT_DAYS = [180, 120, 90, 60, 30, 0]

EXPIRY_FIELDS = {
    'i94_expiry_date': 'I-94 Expiration',
    'visa_stamp_expiry_date': 'Visa Stamp Expiration',
    'passport_expiry_date': 'Passport Expiration',
    'lca_posting_end_date': 'LCA Expiration',
}

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _send_expiry_alert(self, label, expiry_date, days_left):
        subject = (
            f"{label} Expiry Alert – {self.name} ({days_left} days left)"
            if days_left > 0
            else f"{label} Expired – {self.name}"
        )

        body = f"""
        <div style='font-family: Arial; font-size:14px;'>
            <p>Dear {self.name},</p>

            <p>This is an automated notification regarding an upcoming document expiration.</p>

            <table style='border-collapse: collapse;'>
                <tr><td><strong>Employee Name:</strong></td><td>{self.name}</td></tr>
                <tr><td><strong>Document Type:</strong></td><td>{label}</td></tr>
                <tr><td><strong>Expiration Date:</strong></td><td>{expiry_date}</td></tr>
                <tr><td><strong>Days Remaining:</strong></td><td>{'Expired' if days_left == 0 else f'{days_left} days'}</td></tr>
            </table>

            <br/>
            <p><strong>Recommended Next Steps:</strong></p>
            <ul>
                <li>Review the expiration details carefully.</li>
                <li>Initiate renewal or extension immediately.</li>
                <li>Contact HR or Immigration Support if assistance is required.</li>
                <li>Upload updated documents once renewed.</li>
            </ul>

            <p>If you have already taken action, please ignore this message.</p>

            <p>Regards,<br/><strong>HR Compliance System</strong></p>
        </div>
        """

        # Send to employee
        if self.work_email:
            self.env['mail.mail'].create({
                'subject': subject,
                'body_html': body,
                'email_to': self.work_email,
            }).send()

    @api.model
    def cron_check_expiry_alerts(self):
        today = fields.Date.today()
        _logger.warning("TODAY = %s", today)

        for emp in self.search([]):
            _logger.warning("EMPLOYEE = %s", emp.name)

            for field_name, label in EXPIRY_FIELDS.items():
                expiry_date = getattr(emp, field_name)
                _logger.warning(
                    "Field %s → value = %s",
                    field_name, expiry_date
                )

                if not expiry_date:
                    continue

                days_left = (expiry_date - today).days
                _logger.warning(
                    "Document %s | Expiry = %s | Days left = %s",
                    label, expiry_date, days_left
                )

                if days_left in ALERT_DAYS:
                    emp._send_expiry_alert(label, expiry_date, days_left)



