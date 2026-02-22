from odoo import fields, models
from odoo.tools.sql import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    department_id = fields.Many2one("hr.department", string="Department", readonly=True)

    def _select(self):
        return SQL(
            "%s, po.employee_id AS employee_id, po.department_id AS department_id",
            super()._select(),
        )

    def _group_by(self):
        return SQL("%s, po.employee_id, po.department_id", super()._group_by())
