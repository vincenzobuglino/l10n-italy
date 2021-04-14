# Copyright 2019 Francesco Apruzzese <francescoapruzzese@openforce.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SelectManuallyDeclarations(models.TransientModel):

    _name = "l10n_it_declaration_of_intent.select_declarations"
    _description = "Set declaration of intent manually on invoice"

    def _default_declaration(self):
        invoice_id = self._context.get("active_id", False)
        if not invoice_id:
            return []
        invoice = self.env["account.move"].browse(invoice_id)
        type_short = invoice.get_type_short()
        if not type_short:
            return []
        domain = [
            ("partner_id", "=", invoice.partner_id.commercial_partner_id.id),
            ("type", "=", type_short),
            ("date_start", "<=", invoice.invoice_date),
            ("date_end", ">=", invoice.invoice_date),
        ]
        return self.env["l10n_it_declaration_of_intent.declaration"].search(domain)

    declaration_ids = fields.Many2many(
        comodel_name="l10n_it_declaration_of_intent.declaration",
        relation="declaration_select_manually_rel",
        string="Declarations of Intent",
        default=_default_declaration,
    )

    def confirm(self):
        self.ensure_one()
        res = True
        # Link declaration to invoice
        invoice_id = self.env.context.get("active_id", False)
        if not invoice_id:
            return res
        invoice = self.env["account.move"].browse(invoice_id)
        for declaration in self.declaration_ids:
            invoice.declaration_of_intent_ids = [(4, declaration.id)]
        return True
