{
    "name": "Thai Tax Report Custom Layout",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Custom Thai TAX Report layout without modifying the base localization addon",
    "license": "LGPL-3",
    "depends": ["l10n_th_account_tax_report"],
    "data": [
        "data/report_data.xml",
        "reports/tax_report_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "thai_tax_report/static/src/scss/style_report.scss",
        ],
        "web.report_assets_common": [
            "thai_tax_report/static/src/scss/style_report.scss",
        ],
    },
    "installable": True,
}
