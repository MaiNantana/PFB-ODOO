from odoo import _, api, fields, models

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    @api.model
    def _get_pr_sequence_date(self, vals=None):
        vals = vals or {}
        sequence_date = vals.get("date_start") or self.env.context.get("default_date_start")
        if sequence_date:
            return fields.Date.to_date(sequence_date)
        return fields.Date.context_today(self)

    @api.model
    def _get_default_name(self):
        sequence_date = self._get_pr_sequence_date()
        return self.env["ir.sequence"].next_by_code(
            "purchase.request",
            sequence_date=sequence_date,
        )

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

    purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Purchase Orders",
        compute="_compute_purchase_order_ids",
    )

    purchase_order_count = fields.Integer(
        string="Purchase Order Count",
        compute="_compute_purchase_order_ids",
    )

    def _compute_purchase_order_ids(self):
        for request in self:
            purchase_orders = request.mapped("line_ids.purchase_lines.order_id").filtered(
                lambda order: order.state in ("purchase", "done")
            )
            request.purchase_order_ids = purchase_orders
            request.purchase_order_count = len(purchase_orders)

    def action_view_purchase_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        purchase_orders = self.purchase_order_ids
        action["domain"] = [("id", "in", purchase_orders.ids)]
        if len(purchase_orders) == 1:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchase_orders.id
        return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "purchase.request",
                    sequence_date=self._get_pr_sequence_date(vals),
                )
        return super().create(vals_list)
    
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
