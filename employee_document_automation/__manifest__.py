{
    'name': 'Employee Document Automation',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Automatically upload documents based on employee selection field',
    'description': """
        This module adds:
        - A selection field in employee form
        - Automatic document upload based on selection
        - Document template management UI
        - Works with Documents app, hr.document, or as attachments
    """,
    'author': '',
    'depends': ['hr','documents','sign'],
    'data': [
        'security/ir.model.access.csv',
        'views/document_template_views.xml',
        'views/PTO_field.xml',
        'views/sign_wizard.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}