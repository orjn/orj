# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class MailingSubscriptionReason(models.Model):
    """ Reason for opting out of mailing lists or for blacklisting. """
    _name = 'mailing.subscription.optout'
    _description = 'Mailing Subscription Reason'
    _order = 'sequence ASC, create_date DESC, id DESC'

    name = fields.Char(string='Reason', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_feedback = fields.Boolean(string='Ask For Feedback')
