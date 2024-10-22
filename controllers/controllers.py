# -*- coding: utf-8 -*-
from odoo import http

# class MbfDashboardActivity(http.Controller):
#     @http.route('/mbf_dashboard_activity/mbf_dashboard_activity/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mbf_dashboard_activity/mbf_dashboard_activity/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mbf_dashboard_activity.listing', {
#             'root': '/mbf_dashboard_activity/mbf_dashboard_activity',
#             'objects': http.request.env['mbf_dashboard_activity.mbf_dashboard_activity'].search([]),
#         })

#     @http.route('/mbf_dashboard_activity/mbf_dashboard_activity/objects/<model("mbf_dashboard_activity.mbf_dashboard_activity"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mbf_dashboard_activity.object', {
#             'object': obj
#         })