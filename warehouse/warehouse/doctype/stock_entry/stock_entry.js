// Copyright (c) 2026, simon muturi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry Detail", {
    quantity(frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
    },

    basic_rate(frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
    }
});

function calculate_amount(cdt, cdn) {
    const row = locals[cdt][cdn];

    frappe.model.set_value(
        cdt,
        cdn,
        "amount",
        flt(row.quantity) * flt(row.basic_rate)
    );
}