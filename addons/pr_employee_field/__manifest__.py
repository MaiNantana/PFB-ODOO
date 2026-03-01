{
    "name": "Purchase Request - Employee Field",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Add Employee field next to Approver (assigned_to) in Purchase Request",
    "depends": [
        "purchase_request",  # module dependency
        "hr",  # use hr.employee
    ],
    "data": [
        "views/purchase_request_view.xml",
        "views/purchase_order_view.xml",
        "views/purchase_report_view.xml",
    ],
    "installable": True,
    "application": False,
}
