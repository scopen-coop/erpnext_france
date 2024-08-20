# Copyright (c) 2024, Scopen and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.query_builder.functions import Max


def add_cards():
    add_card("Settings", "ERPNext France")
    update_workspace_link_idx()
    add_card("Accounting", "ERPNext France")
    update_workspace_link_idx()


def add_card(workspace_name, workspace_link_label):
    workspace = frappe.get_doc("Workspace", workspace_name)

    if not workspace:
        return

    workspace_link = frappe.get_last_doc(
        "Workspace Link",
        filters={"label": workspace_link_label, "parent": workspace_name},
    )

    content = json.loads(workspace.content)

    should_add_entry = True
    for element in content:
        if element["id"] == workspace_link.name:
            should_add_entry = False

    if not should_add_entry:
        return

    content.append(
        {
            "id": workspace_link.name,
            "type": "card",
            "data": {"card_name": workspace_link.label, "col": 4},
        }
    )

    workspace.content = json.dumps(content)
    workspace.save()


def update_workspace_link_idx():
    workspace_link_idx = [
        {
            "name": "463658a38e",
        },
        {
            "name": "87e757e3c1",
        },
        {
            "name": "dc2d70f0be",
        },
        {
            "name": "2faa60a916",
        },
        {
            "name": "df2fa6d850",
        },
        {
            "name": "a129c62bb0",
        },
        {
            "name": "fc83fdfd07",
        },
        {
            "name": "24d4382374",
        },
        {
            "name": "df2fa6d847",
        },
    ]
    for workspace_info in workspace_link_idx:
        if not frappe.db.exists("Workspace Link", dict(name=workspace_info["name"])):
            continue

        workspace_link = frappe.get_doc("Workspace Link", workspace_info["name"])
        if workspace_link.parenttype == "Workspace":
            workspace_link.idx = find_next_idx_links(workspace_link.parent)

        if workspace_link.idx != 0:
            workspace_link.save()


def find_next_idx_links(workspace_name):
    workspace_link = frappe.qb.DocType("Workspace Link")
    max_idx = (
        frappe.qb.from_(workspace_link)
        .select(Max(workspace_link.idx).as_("max_idx"))
        .where(workspace_link.parent == workspace_name)
        .run(as_dict=True)
    )
    return max_idx[0].max_idx + 1
