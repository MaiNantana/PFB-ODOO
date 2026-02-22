# pr_employee_field/models/purchase_order.py
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    employee_id = fields.Many2one("hr.employee", string="Employee", index=True)
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
        index=True,
    )