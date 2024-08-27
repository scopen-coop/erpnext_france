# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CodeNaf(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        code: DF.Data
        label: DF.Data
        title: DF.Data | None
    # end: auto-generated types

    def validate(self):
        self.set_title()

    def after_rename(self, old_name, new_name, merge=False):
        self.set_title()
        frappe.db.set_value("Code Naf", new_name, "title", self.title)

    def set_title(self):
        self.title = " - ".join(filter(None, [self.code, self.label]))
