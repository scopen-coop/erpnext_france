# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LegalForm(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        code: DF.Data
        label: DF.Data
    # end: auto-generated types
    pass
