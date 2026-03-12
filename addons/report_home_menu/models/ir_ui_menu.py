from odoo import api, fields, models
from odoo.fields import Command


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    reporting_setting_mirror = fields.Boolean(copy=False, index=True)
    source_reporting_menu_id = fields.Many2one(
        "ir.ui.menu", copy=False, index=True, ondelete="cascade"
    )

    @api.model
    def _reporting_source_menu(self):
        return self.env.ref("base.reporting_menuitem", raise_if_not_found=False)

    @api.model
    def _reporting_target_menu(self):
        return self.env.ref("report_home_menu.menu_report_home_root", raise_if_not_found=False)

    @api.model
    def _legacy_reporting_target_menu(self):
        return self.env.ref(
            "report_home_menu.menu_report_home_reporting", raise_if_not_found=False
        )

    @api.model
    def _reporting_system_group(self):
        return self.env.ref(
            "report_home_menu.group_reporting_setting_admin",
            raise_if_not_found=False,
        )

    @api.model
    def _reporting_source_children(self, source_parent):
        self.env.cr.execute(
            """
            SELECT id
            FROM ir_ui_menu
            WHERE parent_id = %s
            ORDER BY sequence, id
            """,
            [source_parent.id],
        )
        ids = [row[0] for row in self.env.cr.fetchall()]
        return self.browse(ids)

    @api.model
    def _mirror_values(self, source_menu, parent_menu):
        system_group = self._reporting_system_group()
        values = {
            "name": source_menu.name,
            "parent_id": parent_menu.id,
            "sequence": source_menu.sequence,
            "action": (
                f"{source_menu.action._name},{source_menu.action.id}"
                if source_menu.action
                else False
            ),
            "active": source_menu.active,
            "reporting_setting_mirror": True,
            "source_reporting_menu_id": source_menu.id,
        }
        if system_group:
            values["groups_id"] = [Command.set([system_group.id])]
        return values

    @api.model
    def _mirror_domain(self):
        target_root = self._reporting_target_menu()
        domain = [("reporting_setting_mirror", "=", True)]
        if target_root:
            domain.append(("id", "child_of", target_root.id))
        return domain

    @api.model
    def _matching_target_mirrors(self, source_menu, target_root):
        action_name = (
            f"{source_menu.action._name},{source_menu.action.id}" if source_menu.action else False
        )
        domain = [("id", "child_of", target_root.id)]
        if action_name:
            domain.append(("action", "=", action_name))
        else:
            domain.extend([("name", "=", source_menu.name), ("action", "=", False)])
        return self.with_context(skip_reporting_setting_sync=True).search(domain, order="id")

    @api.model
    def _dedupe_reporting_mirrors(self, source_parent, target_parent):
        mirror_model = self.with_context(skip_reporting_setting_sync=True)
        for source_menu in self._reporting_source_children(source_parent):
            mirrors = mirror_model.search(
                [
                    ("reporting_setting_mirror", "=", True),
                    ("source_reporting_menu_id", "=", source_menu.id),
                ],
                order="id",
            )
            target_root = self._reporting_target_menu()
            legacy_matches = self.browse()
            if target_root:
                legacy_matches = self._matching_target_mirrors(source_menu, target_root).filtered(
                    lambda menu: menu.id not in mirrors.ids
                )
                if legacy_matches:
                    legacy_matches.write(
                        {
                            "reporting_setting_mirror": True,
                            "source_reporting_menu_id": source_menu.id,
                        }
                    )
                    mirrors |= legacy_matches
            if not mirrors:
                continue
            keeper = mirrors[:1]
            keeper.write(self._mirror_values(source_menu, target_parent))
            duplicates = mirrors - keeper
            if duplicates:
                duplicates.unlink()
            self._dedupe_reporting_mirrors(source_menu, keeper)

    @api.model
    def _sync_reporting_subtree(self, source_parent, target_parent, seen_source_ids):
        mirror_model = self.with_context(skip_reporting_setting_sync=True)
        for source_menu in self._reporting_source_children(source_parent):
            seen_source_ids.add(source_menu.id)
            mirror = mirror_model.search(
                [
                    ("reporting_setting_mirror", "=", True),
                    ("source_reporting_menu_id", "=", source_menu.id),
                ],
                limit=1,
            )
            values = self._mirror_values(source_menu, target_parent)
            if mirror:
                mirror.write(values)
            else:
                mirror = mirror_model.create(values)
            self._sync_reporting_subtree(source_menu, mirror, seen_source_ids)

    @api.model
    def sync_reporting_setting_menus(self):
        source_root = self._reporting_source_menu()
        target_root = self._reporting_target_menu()
        if not source_root or not target_root:
            return True

        self._dedupe_reporting_mirrors(source_root, target_root)

        seen_source_ids = set()
        self._sync_reporting_subtree(source_root, target_root, seen_source_ids)

        stale_mirrors = self.search(
            self._mirror_domain()
            + [
                ("source_reporting_menu_id", "!=", False),
                ("source_reporting_menu_id", "not in", list(seen_source_ids) or [0]),
            ]
        )
        if stale_mirrors:
            stale_mirrors.with_context(skip_reporting_setting_sync=True).unlink()

        legacy_target = self._legacy_reporting_target_menu()
        if legacy_target:
            legacy_children = self.search(
                [
                    ("reporting_setting_mirror", "=", True),
                    ("parent_id", "=", legacy_target.id),
                    (
                        "source_reporting_menu_id",
                        "in",
                        self._reporting_source_children(source_root).ids,
                    ),
                ]
            )
            if legacy_children:
                legacy_children.with_context(skip_reporting_setting_sync=True).write(
                    {"parent_id": target_root.id}
                )
            legacy_target.with_context(skip_reporting_setting_sync=True).write(
                {"active": False}
            )
        return True
