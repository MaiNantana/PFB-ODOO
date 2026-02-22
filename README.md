# PFB-ODOO

Odoo Docker Compose project with custom addons for Purchase Request and Employee/Department extensions.

## Repository Structure

- `docker-compose.yml`: Odoo + PostgreSQL services
- `odoo.conf`: Odoo configuration
- `addons/purchase_request`: Purchase Request module
- `addons/pr_employee_field`: Custom Employee/Department enhancements on PR/PO/Analysis
- `odoo-src/`: Local Odoo source (ignored from Git)

## Features

### purchase_request
- Purchase Request workflow (draft -> approval -> RFQ -> done/reject)
- Create RFQ from Purchase Request lines
- Allocation and traceability between PR lines and PO lines

### pr_employee_field
- Add `Employee` and `Department` on Purchase Request
- Propagate `Employee` to RFQ/PO when created from PR
- Add `Employee` and `Department` on PO form/list
- Lock `Employee` edit on PO state `done` and `cancel` (still open employee record)
- Add `Employee` / `Department` filters and Group By in Purchase Analysis

## Quick Start

1. Start services

```bash
docker compose up -d
```

2. Open Odoo

- URL: `http://localhost:8069`

3. Update apps list and install/upgrade modules

- `purchase_request`
- `pr_employee_field`

## Upgrade Module (CLI example)

```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d <db_name> -u pr_employee_field --stop-after-init
```

## Notes

- This repo excludes `odoo-src/` from Git tracking to keep repository size manageable.
- Python cache files are ignored (`__pycache__`, `*.pyc`).

## Versioning

- First release tag: `v1.0.0`
