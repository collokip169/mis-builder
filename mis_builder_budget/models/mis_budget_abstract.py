from odoo import _, api, fields, models
from datetime import datetime

class MisBudgetAbstract(models.AbstractModel):
    _name = "mis.budget.abstract"
    _description = "MIS Budget (Abstract Base Class)"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Char(tracking=True)
    date_range_id = fields.Many2one(comodel_name="date.range", string="Date range")
    date_from = fields.Date(required=True, string="From", tracking=True)
    date_to = fields.Date(required=True, string="To", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    quarter = fields.Selection(
        [
            ("q1", "Q1 (January - March)"),
            ("q2", "Q2 (April - June)"),
            ("q3", "Q3 (July - September)"),
            ("q4", "Q4 (October - December)"),
        ],
        string="Quarter",
        compute="_compute_quarter",
        store=True,
        readonly=True,
    )

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "name" not in default:
            default["name"] = _("%s (copy)") % self.name
        return super().copy(default=default)

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        for rec in self:
            if rec.date_range_id:
                rec.date_from = rec.date_range_id.date_start
                rec.date_to = rec.date_range_id.date_end

    @api.onchange("date_from", "date_to")
    def _onchange_dates(self):
        for rec in self:
            if rec.date_range_id:
                if (
                    rec.date_from != rec.date_range_id.date_start
                    or rec.date_to != rec.date_range_id.date_end
                ):
                    rec.date_range_id = False

    @api.depends("date_from")
    def _compute_quarter(self):
        for rec in self:
            if rec.date_from:
                month = rec.date_from.month
                if 1 <= month <= 3:
                    rec.quarter = "q1"
                elif 4 <= month <= 6:
                    rec.quarter = "q2"
                elif 7 <= month <= 9:
                    rec.quarter = "q3"
                else:
                    rec.quarter = "q4"
            else:
                rec.quarter = False

    def action_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_confirm(self):
        self.write({"state": "confirmed"})
