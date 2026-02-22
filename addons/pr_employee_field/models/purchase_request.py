from odoo import models, fields

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        tracking=True,
    )
    
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    
    def _prepare_purchase_order(self, picking_type_id=False, company_id=False, origin=False):
        vals = super()._prepare_purchase_order(
            picking_type_id=picking_type_id,
            company_id=company_id,
            origin=origin,
        )
        # ✅ ส่งค่าจาก PR ไป PO
        vals.update({
            "employee_id": self.employee_id.id,
            # department_id ใน PO เป็น related แล้ว ไม่จำเป็นต้องส่งก็ได้
        })
        return vals