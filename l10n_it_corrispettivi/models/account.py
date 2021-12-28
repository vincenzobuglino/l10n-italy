# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2021 Kevin Poli - AIR s.r.l.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    corrispettivi = fields.Boolean(string='Receipts')

    @api.model
    def get_corr_journal(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        corr_journal_id = self.search(
            [('type', '=', 'sale'),
             ('corrispettivi', '=', True),
             ('company_id', '=', company_id.id)], limit=1)

        if not corr_journal_id:
            raise UserError(_('No journal found for receipts'))

        return corr_journal_id


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_partner_id(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return False
        else:
            try:
                return self.env.ref('base.public_user').partner_id.id
            except:
                return False

    @api.model
    def _get_default_journal(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return super(AccountMove, self)._get_default_journal()
        company_id = self._context.get(
            'company_id', self.env.user.company_id)
        return self.env['account.journal'] \
            .get_corr_journal(company_id)

    partner_id = fields.Many2one(default=_default_partner_id)
    journal_id = fields.Many2one(default=_get_default_journal)


    # set default option on inherited field
    corrispettivo = fields.Boolean(
        string='Receipt', related="journal_id.corrispettivi",store=True)

    @api.onchange('company_id')
    def onchange_company_id_corrispettivi(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return

        self.set_corr_journal()

    @api.onchange('partner_id', 'fiscal_position_id')
    def onchange_partner_id_corrispettivi(self):
        if (
            self.partner_id.use_corrispettivi or
            self.fiscal_position_id.corrispettivi
        ):
            self.set_corr_journal()
        else:
            self.journal_id = self._get_default_journal()

    def set_corr_journal(self):
        for invoice in self:
            invoice.journal_id = self.env['account.journal'] \
                .get_corr_journal(invoice.company_id)

    def corrispettivo_print(self):
        """ Print the receipt """
        self.ensure_one()
        return self.env.ref('l10n_it_corrispettivi.account_corrispettivi') \
            .report_action(self)





class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    corrispettivi = fields.Boolean(string='Receipts')

    @api.model
    def get_corr_fiscal_pos(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        corr_fiscal_pos = self.search(
            [
                ('company_id', '=', company_id.id),
                ('corrispettivi', '=', True),
            ],
            limit=1
        )
        if not corr_fiscal_pos:
            # Fall back to fiscal positions without company
            corr_fiscal_pos = self.search(
                [
                    ('company_id', '=', False),
                    ('corrispettivi', '=', True),
                ],
                limit=1
            )

        return corr_fiscal_pos



class ResPartner(models.Model):
    _inherit = 'res.partner'

    use_corrispettivi = fields.Boolean(string='Use Receipts')

    @api.onchange('use_corrispettivi')
    def onchange_use_corrispettivi(self):
        if self.use_corrispettivi:
            # Partner is receipts, assign a receipts (corrispettivi)
            # fiscal position only if there is none
            import pdb;pdb.set_trace()
            if not self.property_account_position_id:
                company = self.company_id or self.env.user.company_id
                self.property_account_position_id = \
                    self.env['account.fiscal.position'] \
                        .get_corr_fiscal_pos(company)
        else:
            # Unset the fiscal position only if it was receipts (corrispettivi)
            if self.property_account_position_id.corrispettivi:
                self.property_account_position_id = False
