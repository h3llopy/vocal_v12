# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    use_in_marketing_automation = fields.Boolean(
        string='Specific mailing used in marketing campaign', default=False,
        help='Marketing campaigns use mass mailings with some specific behavior; this field is used to indicate its statistics may be suspicious.')

    def convert_links(self):
        """Override convert_links so we can add marketing automation campaign instead of mass mail campaign"""
        res = {}
        done = self.env['mail.mass_mailing']
        for mass_mailing in self:
            if self.env.context.get('default_marketing_activity_id'):
                activity = self.env['marketing.activity'].browse(self.env.context['default_marketing_activity_id'])
                vals = {
                    'mass_mailing_id': self.id,
                    'campaign_id': activity.campaign_id.utm_campaign_id.id,
                    'source_id': activity.utm_source_id.id,
                    'medium_id': self.medium_id.id,
                }
                res[mass_mailing.id] = self.env['link.tracker'].convert_links(
                    self.body_html or '',
                    vals,
                    blacklist=['/unsubscribe_from_list']
                )
                done |= mass_mailing
        res.update(super(MassMailing, self - done).convert_links())
        return res

    def _get_blacklist(self):
        self.ensure_one()
        target = self.env[self.mailing_model_real]
        if not ('email' in target._fields or 'email_from' in target._fields):
            return {}
        return super(MassMailing, self)._get_blacklist()

    def _get_seen_list(self):
        self.ensure_one()
        target = self.env[self.mailing_model_real]
        if not ('email' in target._fields or 'email_from' in target._fields):
            return set()
        return super(MassMailing, self)._get_seen_list()
