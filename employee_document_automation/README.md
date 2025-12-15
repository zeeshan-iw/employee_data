# Employee Document Automation Module for Odoo 19

## Overview
This module automatically uploads predefined documents to an employee's document section when a specific category is selected in the employee form.

## Features
- Adds a selection field "Employee Category" to the employee form with 5 options
- Separate model for managing document templates through UI
- Automatic document upload based on selected category
- Support for multiple documents per category
- Configurable document folders and tags
- No hardcoded documents - all managed through UI

## Installation

1. Copy the `employee_document_automation` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Employee Document Automation" module

## Configuration

### 1. Set Up Document Templates

Navigate to: **Employees → Configuration → Document Templates**

For each category:
1. Click "Create"
2. Enter a template name (e.g., "Category 1 Documents")
3. Select the employee category
4. In the "Documents" tab, add documents:
   - Document Name: Name that will appear in the employee's documents
   - File: Upload the document file
   - Folder: (Optional) Select the folder where the document should be stored
   - Tags: (Optional) Select tags to apply to the document

### 2. Using the Feature

1. Open an employee record
2. Select a value from the "Employee Category" field
3. Save the employee record
4. Documents will be automatically uploaded to the employee's document section

## Module Structure

```
employee_document_automation/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── document_template.py      # Document template model
│   └── hr_employee.py             # Employee model extension
├── security/
│   └── ir.model.access.csv        # Access rights
└── views/
    ├── document_template_views.xml # Template management UI
    └── hr_employee_views.xml       # Employee form customization
```

## Customization

### Changing Category Names
Edit the selection field in both files:
- `models/document_template.py` (DocumentTemplate model)
- `models/hr_employee.py` (HrEmployee model)

Change the values:
```python
employee_category = fields.Selection([
    ('your_key_1', 'Your Label 1'),
    ('your_key_2', 'Your Label 2'),
    # ... add more options
], string='Employee Category')
```

### Adding More Categories
Simply add more tuples to the selection field definition in both model files.

## Technical Details

### Models
- **hr.document.template**: Stores document templates for each category
- **hr.document.template.line**: Stores individual documents within a template
- **hr.employee**: Extended with employee_category field and document upload logic

### Workflow
1. User selects an employee category in the employee form
2. On save, the `write()` method is triggered
3. System searches for active document templates matching the selected category
4. For each document in the templates, a new document record is created
5. Documents are linked to the employee and appear in the Documents app

## Dependencies
- hr (Employees module)
- documents (Documents module)

## Version
- Odoo Version: 19.0
- Module Version: 1.0.0

## Support
For issues or customizations, contact your Odoo developer.
