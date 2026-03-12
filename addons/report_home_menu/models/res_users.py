from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    reporting_setting_access = fields.Selection(
        selection=[("admin", "Admin")],
        string="Reporting Setting",
        compute="_compute_reporting_setting_access",
        inverse="_inverse_reporting_setting_access",
        readonly=False,
    )

    def _compute_reporting_setting_access(self):
        admin_group = self.env.ref(
            "report_home_menu.group_reporting_setting_admin", raise_if_not_found=False
        )
        for user in self:
            user.reporting_setting_access = (
                "admin" if admin_group and admin_group in user.groups_id else False
            )

    def _inverse_reporting_setting_access(self):
        admin_group = self.env.ref(
            "report_home_menu.group_reporting_setting_admin", raise_if_not_found=False
        )
        if not admin_group:
            return
        for user in self:
            if user.reporting_setting_access == "admin":
                user.groups_id = [(4, admin_group.id)]
            else:
                user.groups_id = [(3, admin_group.id)]
