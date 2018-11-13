# Copyright 2016 Davide Corio
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# Copyright 2017 Marco Calcagni - Dinamiche Aziendali srl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('invoice_line_tax_ids')
    def onchange_invoice_line_tax_id(self):
        fposition = self.invoice_id.fiscal_position_id
        self.rc = True if fposition.rc_type_id else False

    rc = fields.Boolean("RC")


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    rc_self_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='RC Self Invoice',
        copy=False, readonly=True)
    rc_purchase_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='RC Purchase Invoice', copy=False, readonly=True)
    rc_self_purchase_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='RC Self Purchase Invoice', copy=False, readonly=True)

    rc_partner_supplier_id = fields.Many2one(
        'res.partner', string='Partner RC', change_default=True,
        required=False, readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='always')

    rc_debit_credit_transfer_id = fields.Many2one(
        'account.move', required=False, readonly=True)
    company_partner = fields.Boolean(compute='_compute_company_partner')

    rc_payment_move_id = fields.Many2one(
        string="Reconciliation move", comodel_name='account.move',
        required=False, readonly=True,
        help="Move that reconciles the purchase and sale invoice")

    @api.depends('partner_id')
    def _compute_company_partner(self):
        for el in self:
            if el.partner_id == el.company_id.partner_id:
                el.company_partner = True

    def rc_inv_line_vals(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'uom_id': line.product_id.uom_id.id,
            'price_unit': line.price_unit,
            'quantity': line.quantity,
        }

    def rc_inv_vals(self, partner, account, rc_type, lines):
        if self.type == 'in_invoice':
            type = 'out_invoice'
        else:
            type = 'out_refund'

        vals = {
            'partner_id': partner.id,
            'type': type,
            'account_id': account.id,
            'journal_id': rc_type.journal_id.id,
            'invoice_line_ids': lines,
            'date_invoice': self.date,
            'date': self.date,
            'origin': self.number,
            'rc_purchase_invoice_id': self.id,
            'name': rc_type.self_invoice_text,
            'fiscal_position_id': None,
            'rc_partner_supplier_id': None
            }

        # controllare se rc_type è other e se partner è la company
        # setto rc_partner_supplier con il partner di partenza
        if (rc_type.partner_type == 'other' and
                partner == self.company_id.partner_id):
            # CREAZIONE DI UN'AUTOFATTURA
            vals['rc_partner_supplier_id'] = (
                self.rc_partner_supplier_id.id or
                self.partner_id.id
            )

        return vals

    def get_inv_line_to_reconcile(self):
        for inv_line in self.move_id.line_ids:
            if (self.type == 'in_invoice') and inv_line.credit:
                return inv_line
            elif (self.type == 'in_refund') and inv_line.debit:
                return inv_line
        return False

    def get_rc_inv_line_to_reconcile(self, invoice):
        for inv_line in invoice.move_id.line_ids:
            if (invoice.type == 'out_invoice') and inv_line.debit:
                return inv_line
            elif (invoice.type == 'out_refund') and inv_line.credit:
                return inv_line
        return False

    def rc_payment_vals(self, rc_type):
        return {
            'journal_id': rc_type.payment_journal_id.id,
            # 'period_id': self.period_id.id,
            'date': self.date,
        }

    def rc_credit_line_vals(self, journal):
        credit = debit = 0.0
        if self.type == 'in_invoice':
            credit = self.amount_tax
        else:
            debit = self.amount_tax

        return {
            'name': self.number,
            'credit': credit,
            'debit': debit,
            'account_id': journal.default_credit_account_id.id,
            'company_id': self.company_id.id,
        }

    def rc_debit_line_vals(self, amount=None):
        credit = debit = 0.0
        if self.type == 'in_invoice':
            if amount:
                debit = amount
            else:
                debit = self.amount_tax
        else:
            if amount:
                credit = amount
            else:
                credit = self.amount_tax
        return {
            'name': self.number,
            'debit': debit,
            'credit': credit,
            'account_id': self.get_inv_line_to_reconcile().account_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id
        }

    def rc_invoice_payment_vals(self, rc_type):
        return {
            'journal_id': rc_type.payment_journal_id.id,
            # 'period_id': self.period_id.id,
            'date': self.date,
        }

    def rc_payment_credit_line_vals(self, invoice):
        credit = debit = 0.0
        if invoice.type == 'out_invoice':
            credit = self.get_rc_inv_line_to_reconcile(invoice).debit
        else:
            debit = self.get_rc_inv_line_to_reconcile(invoice).credit
        return {
            'name': invoice.number,
            'credit': credit,
            'debit': debit,
            'account_id': self.get_rc_inv_line_to_reconcile(
                invoice).account_id.id,
            'partner_id': invoice.partner_id.id,
            'company_id': self.company_id.id
        }

    def rc_payment_debit_line_vals(self, invoice, journal):
        credit = debit = 0.0
        if invoice.type == 'out_invoice':
            debit = self.get_rc_inv_line_to_reconcile(invoice).debit
        else:
            credit = self.get_rc_inv_line_to_reconcile(invoice).credit
        return {
            'name': invoice.number,
            'debit': debit,
            'credit': credit,
            'account_id': journal.default_credit_account_id.id,
            'company_id': self.company_id.id
        }

    def reconcile_supplier_invoice(self):
        rc_type = self.fiscal_position_id.rc_type_id

        move_model = self.env['account.move']
        move_line_model = self.env['account.move.line']

        rc_payment_data = self.rc_payment_vals(rc_type)
        rc_payment = move_model.create(rc_payment_data)
        rc_invoice = self.rc_self_invoice_id

        payment_credit_line_data = self.rc_payment_credit_line_vals(
            rc_invoice)
        payment_debit_line_data = self.rc_debit_line_vals(
            self.amount_total)
        rc_payment.line_ids = [
            (0, 0, payment_debit_line_data),
            (0, 0, payment_credit_line_data),
        ]
        for move_line in rc_payment.line_ids:
            if move_line.debit:
                payment_debit_line = move_line
            elif move_line.credit:
                payment_credit_line = move_line
        rc_payment.post()

        lines_to_rec = move_line_model.browse([
            self.get_inv_line_to_reconcile().id,
            payment_debit_line.id
        ])
        lines_to_rec.reconcile()

        rc_lines_to_rec = move_line_model.browse([
            self.get_rc_inv_line_to_reconcile(rc_invoice).id,
            payment_credit_line.id
        ])
        rc_lines_to_rec.reconcile()

    def prepare_reconcile_supplier_invoice(self):
        rc_type = self.fiscal_position_id.rc_type_id
        move_model = self.env['account.move']
        rc_payment_data = self.rc_payment_vals(rc_type)
        rc_payment = move_model.create(rc_payment_data)

        payment_credit_line_data = self.rc_credit_line_vals(
            rc_type.payment_journal_id)

        payment_debit_line_data = self.rc_debit_line_vals()
        # Avoid payment lines without amounts
        if (payment_credit_line_data['debit'] or
                payment_credit_line_data['credit']):
            rc_payment.line_ids = [
                (0, 0, payment_debit_line_data),
                (0, 0, payment_credit_line_data),
            ]
        return rc_payment

    def partially_reconcile_supplier_invoice(self, rc_payment):
        move_line_model = self.env['account.move.line']
        inv_line_to_reconcile = self.get_inv_line_to_reconcile()
        payment_debit_line = False
        for move_line in rc_payment.line_ids:
            if (inv_line_to_reconcile.account_id.id !=
                    move_line.account_id.id):
                continue
            # testa se nota credito o debito
            if self.type == 'in_invoice' and move_line.debit:
                payment_debit_line = move_line
            elif self.type == 'in_refund' and move_line.credit:
                payment_debit_line = move_line
        if payment_debit_line:
            inv_lines_to_rec = move_line_model.browse(
                [inv_line_to_reconcile.id, payment_debit_line.id])
            inv_lines_to_rec.reconcile()

    def reconcile_rc_invoice(self, rc_payment):
        rc_type = self.fiscal_position_id.rc_type_id
        move_line_model = self.env['account.move.line']
        rc_invoice = self.rc_self_invoice_id
        rc_payment_credit_line_data = self.rc_payment_credit_line_vals(
            rc_invoice)

        rc_payment_debit_line_data = self.rc_payment_debit_line_vals(
            rc_invoice, rc_type.payment_journal_id)

        rc_payment.line_ids = [
            (0, 0, rc_payment_debit_line_data),
            (0, 0, rc_payment_credit_line_data),
        ]
        rc_payment.post()
        inv_line_to_reconcile = self.get_rc_inv_line_to_reconcile(rc_invoice)
        for move_line in rc_payment.line_ids:
            if move_line.account_id.id == inv_line_to_reconcile.account_id.id:
                rc_payment_line_to_reconcile = move_line

        rc_lines_to_rec = move_line_model.browse(
            [inv_line_to_reconcile.id,
                rc_payment_line_to_reconcile.id])
        rc_lines_to_rec.reconcile()

    def generate_self_invoice(self):
        rc_type = self.fiscal_position_id.rc_type_id
        if not rc_type.payment_journal_id.default_credit_account_id:
            raise UserError(
                _('There is no default credit account defined \n'
                  'on journal "%s".') % rc_type.payment_journal_id.name)
        if rc_type.partner_type == 'other':
            rc_partner = rc_type.partner_id
        else:
            rc_partner = self.partner_id
        rc_account = rc_partner.property_account_receivable_id

        rc_invoice_lines = []
        for line in self.invoice_line_ids:
            if line.rc:
                rc_invoice_line = self.rc_inv_line_vals(line)
                line_tax = line.invoice_line_tax_ids
                if not line_tax:
                    raise UserError(_(
                        "Invoice line\n%s\nis RC but has not tax") % line.name)
                tax_id = None
                for tax_mapping in rc_type.tax_ids:
                    if tax_mapping.purchase_tax_id == line_tax[0]:
                        tax_id = tax_mapping.sale_tax_id.id
                if not tax_id:
                    raise UserError(_("Tax code used is not a RC tax.\nCan't "
                                      "find tax mapping"))
                if line_tax:
                    rc_invoice_line['invoice_line_tax_ids'] = [
                        (6, False, [tax_id])]
                rc_invoice_line[
                    'account_id'] = rc_type.transitory_account_id.id
                rc_invoice_lines.append([0, False, rc_invoice_line])
        if rc_invoice_lines:
            inv_vals = self.rc_inv_vals(
                rc_partner, rc_account, rc_type, rc_invoice_lines)

            inv_vals['comment'] = self.fiscal_position_id.note
            # create or write the self invoice
            if self.rc_self_invoice_id:
                # this is needed when user takes back to draft supplier
                # invoice, edit and validate again
                rc_invoice = self.rc_self_invoice_id
                rc_invoice.invoice_line_ids.unlink()
                rc_invoice.period_id = False
                rc_invoice.write(inv_vals)
                rc_invoice.compute_taxes()
            else:
                rc_invoice = self.create(inv_vals)
                self.rc_self_invoice_id = rc_invoice.id
            rc_invoice.action_invoice_open()

            if rc_type.with_supplier_self_invoice:
                self.reconcile_supplier_invoice()
            else:
                rc_payment = self.prepare_reconcile_supplier_invoice()
                self.write({'rc_payment_move_id': rc_payment.id})
                self.reconcile_rc_invoice(rc_payment)
                self.partially_reconcile_supplier_invoice(rc_payment)

    def generate_supplier_self_invoice(self):
        rc_type = self.fiscal_position_id.rc_type_id
        if not len(rc_type.tax_ids) == 1:
            raise UserError(_(
                "Can't find 1 tax mapping for %s" % rc_type.name))
        if not self.rc_self_purchase_invoice_id:
            supplier_invoice = self.copy()
        else:
            supplier_invoice_vals = self.copy_data()
            supplier_invoice = self.rc_self_purchase_invoice_id
            supplier_invoice.invoice_line_ids.unlink()
            supplier_invoice.write(supplier_invoice_vals[0])

        # because this field has copy=False
        supplier_invoice.date = self.date
        supplier_invoice.date_invoice = self.date
        supplier_invoice.date_due = self.date
        supplier_invoice.partner_id = rc_type.partner_id.id
        supplier_invoice.journal_id = rc_type.supplier_journal_id.id
        for inv_line in supplier_invoice.invoice_line_ids:
            inv_line.invoice_line_tax_ids = [
                (6, 0, [rc_type.tax_ids[0].purchase_tax_id.id])]
            inv_line.account_id = rc_type.transitory_account_id.id
        self.rc_self_purchase_invoice_id = supplier_invoice.id

        # temporary disabling self invoice automations
        supplier_invoice.fiscal_position_id = None
        supplier_invoice.compute_taxes()
        supplier_invoice.check_total = supplier_invoice.amount_total
        supplier_invoice.action_invoice_open()
        supplier_invoice.fiscal_position_id = self.fiscal_position_id.id

        self._set_rc_partner_supplier_id(rc_type, supplier_invoice)

    def _set_rc_partner_supplier_id(self, rc_type, supplier_invoice):
        if (rc_type.partner_type == 'other' and
                rc_type.partner_id == self.company_id.partner_id):
            partner_ref = self.rc_partner_supplier_id or self.partner_id
            # ref del partner da cui si stanno generando le autofatture
            supplier_invoice.rc_partner_supplier_id = partner_ref

    @api.multi
    def invoice_validate(self):
        self.ensure_one()
        res = super(AccountInvoice, self).invoice_validate()

        fp = self.fiscal_position_id
        rc_type = fp and fp.rc_type_id
        if rc_type and rc_type.method == 'selfinvoice'\
                and self.amount_total:
            if not rc_type.with_supplier_self_invoice:
                self.generate_self_invoice()
            else:
                # See with_supplier_self_invoice field help
                self.generate_supplier_self_invoice()
                self.rc_self_purchase_invoice_id.generate_self_invoice()

        if (rc_type and
                rc_type.method == 'selfinvoice' and
                self.amount_total and
                self.type in ('in_invoice', 'in_refund') and
                self.company_partner is True):

            self.transfer_debit_partner_supplier()
        return res

    def transfer_debit_partner_supplier(self):
        """
        Se il partner della fattura di partenza (no RC) è la company ed
        è una fattura di acquisto, deve essere aperto un debito vs il
        parnter di partenza e chiuso quello del partner
        """
        # Credit/debit logic refund
        ml_company = False
        for ml in self.move_id.line_ids:
            if ml.account_id.user_type_id.type in ['receivable', 'payable']:
                ml_company = ml
                break

        if ml_company:
            move_lines = []
            # Refund my company
            if ml_company.debit:
                desc = _('Credit transfer for reverse charge')
            else:
                desc = _('Debit transfer for reverse charge')
            company_line = {
                'partner_id': self.partner_id.id,
                'account_id': ml_company.account_id.id,
                'credit': (ml_company and
                           ml_company.debit and
                           self.residual or 0),
                'debit': (ml_company and
                          ml_company.credit and
                          self.residual or 0),
                'name': desc,
            }
            move_lines.append((0, 0, company_line))
            # Add debit/credit to RC partner
            partner_rc_line = {
                'partner_id': self.rc_partner_supplier_id.id,
                'account_id': ml_company.account_id.id,
                'credit': (ml_company and
                           ml_company.credit and
                           self.residual or 0),
                'debit': (ml_company and
                          ml_company.debit and
                          self.residual or 0),
                'name': desc,
            }
            move_lines.append((0, 0, partner_rc_line))

            move_val = {
                'date': self.move_id.date,
                'company_id': self.move_id.company_id.id,
                'journal_id':
                    self.fiscal_position_id.rc_type_id.payment_journal_id.id,
                'line_ids': move_lines
            }
            move_transfer = self.env['account.move'].create(move_val)
            self.write({'rc_debit_credit_transfer_id': move_transfer.id})

            # Reconcile supplier invoice with transfer
            lines_to_reconcile = []
            domain = [('move_id', '=', move_transfer.id),
                      ('partner_id', '=', self.partner_id.id)]
            ml_transfer_company = self.env['account.move.line']\
                .search(domain, order='id', limit=1)
            if ml_transfer_company:
                lines_to_reconcile = ml_transfer_company + ml_company
                lines_to_reconcile.reconcile()

        return move_transfer

    def remove_rc_payment(self):
        inv = self
        if inv.payment_move_line_ids:
            if len(inv.payment_move_line_ids) > 1:
                raise UserError(
                    _('There are more than one payment line.\n'
                      'In that case account entries cannot be canceled'
                      'automatically. Please proceed manually'))
            payment_move = inv.payment_move_line_ids[0].move_id

            # remove move reconcile related to the supplier invoice
            move = inv.move_id
            rec_partial = move.mapped('line_ids').filtered(
                'matched_debit_ids').mapped('matched_debit_ids')
            rec_partial_lines = (
                rec_partial.mapped('credit_move_id') |
                rec_partial.mapped('debit_move_id')
            )
            rec_partial_lines.remove_move_reconcile()

            # also remove full reconcile, in case of with_supplier_self_invoice
            rec_partial_lines = move.mapped('line_ids').filtered(
                'full_reconcile_id'
            ).mapped('full_reconcile_id.reconciled_line_ids')
            rec_partial_lines.remove_move_reconcile()
            # remove move reconcile related to the self invoice
            move = inv.rc_self_invoice_id.move_id
            rec_lines = move.mapped('line_ids').filtered(
                'full_reconcile_id'
            ).mapped('full_reconcile_id.reconciled_line_ids')
            rec_lines.remove_move_reconcile()
            # cancel self invoice
            self_invoice = self.browse(
                inv.rc_self_invoice_id.id)
            self_invoice.action_invoice_cancel()
            # invalidate and delete the payment move generated
            # by the self invoice creation
            payment_move.button_cancel()
            payment_move.unlink()

    @api.multi
    def action_cancel(self):
        for inv in self:
            rc_type = inv.fiscal_position_id.rc_type_id
            if (
                rc_type and
                rc_type.method == 'selfinvoice' and
                inv.rc_self_invoice_id
            ):
                inv.remove_rc_payment()
            elif (
                rc_type and
                rc_type.method == 'selfinvoice' and
                inv.rc_self_purchase_invoice_id
            ):
                inv.rc_self_purchase_invoice_id.remove_rc_payment()
                inv.rc_self_purchase_invoice_id.action_invoice_cancel()
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def action_invoice_draft(self):
        super(AccountInvoice, self).action_invoice_draft()
        invoice_model = self.env['account.invoice']
        for inv in self:
            if inv.rc_self_invoice_id:
                self_invoice = invoice_model.browse(
                    inv.rc_self_invoice_id.id)
                self_invoice.action_invoice_draft()
            if inv.rc_self_purchase_invoice_id:
                self_purchase_invoice = invoice_model.browse(
                    inv.rc_self_purchase_invoice_id.id)
                self_purchase_invoice.action_invoice_draft()
        return True
