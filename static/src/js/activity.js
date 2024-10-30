odoo.define('mail.Activity', function (require) {
    "use strict";
    
    var mailUtils = require('mail.utils');
    
    var AbstractField = require('web.AbstractField');
    var BasicModel = require('web.BasicModel');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var time = require('web.time');
    
    var QWeb = core.qweb;
    var _t = core._t;

    var BasicActivity = AbstractField.extend({
        events: {
            // 'click .o_edit_activity': '_onEditActivity',
            // 'click .o_mark_as_done': '_onMarkActivityDone',
            // 'click .o_activity_template_preview': '_onPreviewMailTemplate',
            // 'click .o_schedule_activity': '_onScheduleActivity',
            // 'click .o_activity_template_send': '_onSendMailTemplate',
            'click .o_unlink_activity': '_onUnlinkActivity',
        },
        init: function () {
            this._super.apply(this, arguments);
            this._draftFeedback = {};
        },
        _onUnlinkActivity: function () {
            var self = this;
            this.$('.o_unlink_activity').hide();
        },

    })
    
})