from odoo import models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        vals = super()._prepare_purchase_order(picking_type, group_id, company, origin)

        # If all selected request lines belong to one employee, carry it to RFQ/PO.
        employees = self.item_ids.mapped("request_id.employee_id").filtered(lambda e: e)
        if len(employees) == 1:
            vals["employee_id"] = employees.id

        return vals
