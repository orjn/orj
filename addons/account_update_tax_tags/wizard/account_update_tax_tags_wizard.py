from datetime import timedelta
from orj import _, api, fields, models
from orj.exceptions import UserError


class AccountUpdateTaxTagsWizard(models.TransientModel):
    _name = 'account.update.tax.tags.wizard'
    _description = 'Update Tax Tags Wizard'

    company_id = fields.Many2one(comodel_name='res.company', required=True, readonly=True, default=lambda self: self.env.company)
    date_from = fields.Date(
        string='Starting from',
        help='Date from which journal items will be updated.',
        compute='_compute_date_from',
        store=True,
        readonly=False,
        required=True,
    )
    display_lock_date_warning = fields.Boolean(compute='_compute_display_lock_date_warning')

    # ==== Compute methods ====
    @api.depends('company_id')
    def _compute_date_from(self):
        for wizard in self:
            tax_lock_date = self.company_id.tax_lock_date
            wizard.date_from = tax_lock_date + timedelta(days=1) if tax_lock_date else fields.Date.context_today(self)

    @api.depends('date_from')
    def _compute_display_lock_date_warning(self):
        for wizard in self:
            tax_lock_date = self.company_id.tax_lock_date
            wizard.display_lock_date_warning = tax_lock_date and wizard.date_from < tax_lock_date

    # ==== Business methods ====
    def _modify_tag_to_aml_relation(self, company_id, date_from):
        """ Update Journal Items' tax grids to match current taxes' configuration.
        The next query work in 3 steps.
        1) Get a duo: (aml_id, tag_id or NULL) for each aml involved with the tax.
            This first step is achieved in the 3 first table: base line, tax line, fusion.
            a) As the base line and tax line aren't linked to tax in the same way, we need to gather them separately.
            The base line get its repartition line by going through the tax.
            b) The tax lines already have their repartition line linked.
        2) Delete the previous relation aml - tag for each aml appearing in the previous queries.
        3) Insert the new relation aml - tag.
        4) Gather the ids of impacted amls into an array and return it.
        :param: int company_id id of company
        :return: list of impacted account.move.line ids
        """
        self.env.flush_all()
        self.env.cr.execute("""
            -- 1.a) Handle base line: relation aml <-> tag, if no relation, tag is NULL
            WITH base_aml_id_rep_tag_to_insert AS (
                SELECT aml.id AS aml_id, rep_tags.account_account_tag_id AS tag_id
                FROM account_move_line aml
                JOIN account_move move
                ON aml.move_id = move.id AND move.company_id = %(company_id)s AND aml.date >= %(date_from)s
                LEFT JOIN account_move caba_origin_move
                ON move.tax_cash_basis_origin_move_id = caba_origin_move.id
                JOIN account_move_line_account_tax_rel aml_to_tax
                ON aml_to_tax.account_move_line_id = aml.id
                -- Handle possible children_tax_ids
                LEFT JOIN account_tax_filiation_rel taxes_filiation
                ON taxes_filiation.parent_tax = aml_to_tax.account_tax_id
                JOIN account_tax tax
                ON tax.id = COALESCE(taxes_filiation.child_tax, aml_to_tax.account_tax_id)
                JOIN account_tax parent_tax
                ON aml_to_tax.account_tax_id = parent_tax.id
                JOIN account_tax_repartition_line tax_to_rep_line
                -- the repartition line to join depends of the move_type
                -- also, as this is the base line query, we only join for the base repartition type
                ON
                    tax_to_rep_line.repartition_type = 'base'
                    AND (
                        -- invoice type doc
                            (
                                COALESCE(caba_origin_move.move_type, move.move_type) IN ('in_invoice','out_invoice', 'in_receipt', 'out_receipt')
                                AND tax_to_rep_line.document_type = 'invoice'
                                AND tax_to_rep_line.tax_id = tax.id
                            )
                        OR
                        -- refund type doc
                            (
                                COALESCE(caba_origin_move.move_type, move.move_type) IN ('in_refund','out_refund')
                                AND tax_to_rep_line.document_type = 'refund'
                                AND tax_to_rep_line.tax_id = tax.id
                            )
                        OR
                        -- entry type doc: depends on the tax type
                        -- for base line:
                        -- balance < 0 and sale tax --> invoice
                        -- balance > 0 and sale tax --> refund
                        -- balance > 0 and purchase tax --> invoice
                        -- balance < 0 and purchase tax --> refund
                        -- impossible to decide for balance at 0 --> invoice by default
                        (
                            COALESCE(caba_origin_move.move_type, move.move_type) = 'entry'
                            AND (
                                (
                                    COALESCE(parent_tax.type_tax_use, tax.type_tax_use) = 'sale'
                                    AND (
                                        aml.balance <= 0 AND tax_to_rep_line.document_type = 'invoice' AND tax_to_rep_line.tax_id = tax.id
                                        OR aml.balance > 0 AND tax_to_rep_line.document_type = 'refund' AND tax_to_rep_line.tax_id = tax.id
                                    )
                                )
                                OR
                                (
                                    COALESCE(parent_tax.type_tax_use, tax.type_tax_use) = 'purchase'
                                    AND (
                                        aml.balance >= 0 AND tax_to_rep_line.document_type = 'invoice' AND tax_to_rep_line.tax_id = tax.id
                                        OR aml.balance < 0 AND tax_to_rep_line.document_type = 'refund' AND tax_to_rep_line.tax_id = tax.id
                                    )
                                )
                            )
                        )
                    )
                -- LEFT to allow keeping all aml even those without relation. The NULL will symbolize no relation
                LEFT JOIN account_account_tag_account_tax_repartition_line_rel rep_tags
                ON rep_tags.account_tax_repartition_line_id = tax_to_rep_line.id
            ),

            -- 1.b) Handle tax line: relation aml <-> tag, if no relation, tag is NULL
            tax_aml_id_rep_tag_to_insert AS (
                SELECT aml.id AS aml_id, rep_tags.account_account_tag_id AS tag_id
                FROM account_move_line aml
                JOIN account_tax_repartition_line rep_ln ON rep_ln.id = aml.tax_repartition_line_id
                LEFT JOIN account_account_tag_account_tax_repartition_line_rel rep_tags
                ON rep_tags.account_tax_repartition_line_id = aml.tax_repartition_line_id
                WHERE aml.company_id = %(company_id)s AND aml.date >= %(date_from)s
            ),

            base_and_tax_aml_tag_id AS (
                SELECT aml_id, tag_id FROM base_aml_id_rep_tag_to_insert
                UNION
                SELECT aml_id, tag_id FROM tax_aml_id_rep_tag_to_insert
            ),

            -- 2) Delete previous tags from amls
            delete_statement AS (
                DELETE FROM account_account_tag_account_move_line_rel aml_tags
                USING base_and_tax_aml_tag_id btat
                WHERE btat.aml_id = aml_tags.account_move_line_id
                RETURNING account_move_line_id AS aml_id
            ),

            -- 3) Insert new tag on amls
            insert_statement AS (
                INSERT INTO account_account_tag_account_move_line_rel
                SELECT btat.aml_id, btat.tag_id
                FROM base_and_tax_aml_tag_id btat
                WHERE btat.tag_id NOTNULL
                RETURNING account_move_line_id AS aml_id
            ),

            -- 4) Return impacted amls
            impacted_aml as (
                SELECT aml_id
                FROM delete_statement
                UNION
                SELECT aml_id
                FROM insert_statement
            )

            SELECT ARRAY_AGG(impacted_aml.aml_id)
              FROM impacted_aml
        """, params={
            'date_from': date_from,
            'company_id': company_id,
        })
        self.env.invalidate_all()
        return self.env.cr.fetchone()[0]

    def update_amls_tax_tags(self):
        parent_taxes = self.env['account.tax'].search([
            ('company_id', '=', self.company_id.id),
            ('children_tax_ids', '!=', False),
        ])
        children_taxes = []
        for tax in parent_taxes:
            children_taxes += tax.children_tax_ids.ids
        if len(children_taxes) > len(parent_taxes.children_tax_ids.ids):
            raise UserError(_('Update with children taxes that are child of multiple parents is not supported.'))
        self._modify_tag_to_aml_relation(self.company_id.id, self.date_from)
