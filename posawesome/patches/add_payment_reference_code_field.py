# Copyright (c) 2026, POS Awesome contributors
# Adds posa_reference_code (optional reconciliation reference) to Sales Invoice Payment child table.

import frappe


def execute():
    doctype = "Sales Invoice Payment"
    fieldname = "posa_reference_code"

    if frappe.db.has_column(doctype, fieldname):
        return

    custom_field = {
        "dt": doctype,
        "fieldname": fieldname,
        "fieldtype": "Data",
        "label": "Reference Code",
        "insert_after": "amount",
        "description": (
            "Optional reference code (e.g. M-PESA transaction code, cheque number) "
            "for later reconciliation."
        ),
        "allow_on_submit": 1,
        "in_list_view": 1,
        "print_hide_if_no_value": 1,
        "length": 140,
    }

    frappe.get_doc(
        {
            "doctype": "Custom Field",
            **custom_field,
            "name": f"{doctype}-{fieldname}",
        }
    ).insert(ignore_permissions=True)

    frappe.db.commit()
