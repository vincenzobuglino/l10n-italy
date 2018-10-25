# -*- coding: utf-8 -*-
# Copyright 2018 Sergio Corato (https://efatto.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    is_pec = fields.Boolean("PEC server")
