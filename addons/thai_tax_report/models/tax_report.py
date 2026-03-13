from odoo import models


class ThaiTaxReport(models.AbstractModel):
    _inherit = "report.l10n_th_account_tax_report.report_thai_tax"

    def _get_report_values(self, docids, data):
        report_values = super()._get_report_values(docids, data)
        data = report_values["docs"]._prepare_report_tax()
        company = self.env["res.company"].browse(data["company_id"])
        report_values["company_address"] = company.partner_id._display_address(
            without_company=True
        )
        return report_values
