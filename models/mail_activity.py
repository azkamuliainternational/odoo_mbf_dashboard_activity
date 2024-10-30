# Copyright 2018 David Juaneda - <djuaneda@sdi.es>
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, SUPERUSER_ID
from collections import defaultdict

class MailActivity(models.Model):
    _inherit = "mail.activity"

    res_model_id_name = fields.Char(
        related='res_model_id.name', string="Origin",
        readonly=True)
    duration = fields.Float(
        related='calendar_event_id.duration', readonly=True)
    calendar_event_id_start = fields.Datetime(
        related='calendar_event_id.start', readonly=True)
    calendar_event_id_partner_ids = fields.Many2many(
        related='calendar_event_id.partner_ids',
        readonly=True)
    status = fields.Selection([
        ('op', 'On Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], 'Status',
        default='op')
    ket = fields.Char(compute="_ket")


    @api.depends('res_model', 'res_id')
    def _ket(self):
        for activity in self:
            if (activity.res_model=='account.invoice') or (activity.res_model=='crm.lead'):
                activity.ket = self.env[activity.res_model].browse(activity.res_id).partner_id[0].name
        

    # @api.depends("res_id")
    # def _ket(self):
    #     for record in self:
    #         if record.res_model=='account.invoice':
    #             no_invoice = self.env['account.invoice'].search([('id','=',record.res_id)])
    #             record.ket = no_invoice.name
            
            
    @api.multi
    def open_origin(self):
        self.ensure_one()
        vid = self.env[self.res_model].browse(self.res_id).get_formview_id()
        response = {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'form',
            'res_id': self.res_id,
            'target': 'current',
            'flags': {
                'form': {
                    'action_buttons': False
                }
            },
            'views': [
                (vid, "form")
            ]
        }
        return response

    @api.model
    def action_activities_board(self):
        action = self.env.ref(
            'mail_activity_board.open_boards_activities').read()[0]
        return action

    @api.model
    def _find_allowed_model_wise(self, doc_model, doc_dict):
        doc_ids = list(doc_dict)
        allowed_doc_ids = self.env[doc_model].with_context(
            active_test=False).search([('id', 'in', doc_ids)]).ids
        return set([message_id for allowed_doc_id in allowed_doc_ids
                    for message_id in doc_dict[allowed_doc_id]])

    @api.model
    def _find_allowed_doc_ids(self, model_ids):
        ir_model_access_model = self.env['ir.model.access']
        allowed_ids = set()
        for doc_model, doc_dict in model_ids.items():
            if not ir_model_access_model.check(doc_model, 'read', False):
                continue
            allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
        return allowed_ids

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        # Rules do not apply to administrator
        if self._uid == SUPERUSER_ID:
            return super(MailActivity, self)._search(
                args, offset=offset, limit=limit, order=order,
                count=count, access_rights_uid=access_rights_uid)

        ids = super(MailActivity, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=False, access_rights_uid=access_rights_uid)
        if not ids and count:
            return 0
        elif not ids:
            return ids

        # check read access rights before checking the actual rules
        super(MailActivity, self.sudo(access_rights_uid or self._uid)).\
            check_access_rights('read')

        model_ids = {}

        self._cr.execute("""
            SELECT DISTINCT a.id, im.id, im.model, a.res_id
            FROM "%s" a
            LEFT JOIN ir_model im ON im.id = a.res_model_id
            WHERE a.id = ANY (%%(ids)s)""" % self._table, dict(ids=ids))
        for a_id, ir_model_id, model, model_id in self._cr.fetchall():
            model_ids.setdefault(model, {}).setdefault(
                model_id, set()).add(a_id)

        allowed_ids = self._find_allowed_doc_ids(model_ids)

        final_ids = allowed_ids

        if count:
            return len(final_ids)
        else:
            # re-construct a list based on ids, because set didn't keep order
            id_list = [a_id for a_id in ids if a_id in final_ids]
            return id_list
    # @api.multi
    def unlink(self):
        # for activity in self:
        #      self.status='cancel'
        """ Override unlink to delete records activities through (res_model, res_id). """
        if (self._name=='mail.activity'):
            for activity in self:
                self.status='cancel'
                result=''
        else :
            record_ids = self.ids
            result = super(MailActivityMixin, self).unlink()
            self.env['mail.activity'].sudo().search(
                [('res_model', '=', self._name), ('res_id', 'in', record_ids)]
            ).unlink()
        return result    
        
    def onprogress(self):
        # for activity in self:
        #      self.status='cancel'
        """ Override unlink to delete records activities through (res_model, res_id). """
        if (self._name=='mail.activity'):
            for activity in self:
                self.status='op'
               
            
        
    def action_feedback(self, feedback=False):
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            activity.status='done'
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
            )

            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            message |= activity_message

        return message.ids and message.ids[0] or False