# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging
from werkzeug.exceptions import Forbidden, NotFound

from orj import exceptions, http
from orj.http import request
from orj.addons.website_event.controllers.community import EventCommunityController
from orj.osv import expression

_logger = logging.getLogger(__name__)


class WebsiteEventMeetController(EventCommunityController):

    def _get_event_rooms_base_domain(self, event):
        search_domain_base = [('event_id', '=', event.id)]
        if not request.env.user.has_group('event.group_event_registration_desk'):
            search_domain_base = expression.AND([search_domain_base, [('is_published', '=', True)]])
        return search_domain_base

    def _sort_event_rooms(self, room):
        return (room.website_published, room.is_pinned, room.room_last_activity, room.id)

    # ------------------------------------------------------------
    # MAIN PAGE
    # ------------------------------------------------------------

    @http.route()
    def community(self, event, page=1, lang=None, **kwargs):
        """Display the meeting rooms of the event on the frontend side.

        :param event: event for which we display the meeting rooms
        :param lang: lang id used to perform a search
        """
        return request.render(
            "website_event_meet.event_meet",
            self._event_meeting_rooms_get_values(event, lang=lang)
        )

    def _event_meeting_rooms_get_values(self, event, lang=None):
        search_domain = self._get_event_rooms_base_domain(event)
        meeting_rooms_all = request.env['event.meeting.room'].sudo().search(search_domain)
        if lang:
            search_domain = expression.AND([
                search_domain,
                [('room_lang_id', '=', int(lang))]
            ])
        meeting_rooms = request.env['event.meeting.room'].sudo().search(search_domain)
        meeting_rooms = meeting_rooms.sorted(self._sort_event_rooms, reverse=True)

        is_event_user = request.env.user.has_group("event.group_event_registration_desk")
        if not is_event_user:
            meeting_rooms = meeting_rooms.filtered(lambda m: not m.room_is_full)

        visitor = request.env['website.visitor']._get_visitor_from_request()

        return {
            # event information
            "event": event,
            'main_object': event,
            # rooms
            "meeting_rooms": meeting_rooms,
            "current_lang": request.env["res.lang"].browse(int(lang)) if lang else False,
            "available_languages": meeting_rooms_all.mapped("room_lang_id"),
            "default_lang_code": request.context.get('lang', request.env.user.lang),
            "default_username": visitor.display_name if visitor else None,
            # environment
            "is_event_user": is_event_user,
        }

    @http.route("/event/<model('event.event'):event>/meeting_room_create",
                type="http", auth="public", methods=["POST"], website=True)
    def create_meeting_room(self, event, **post):
        if not event or (not event.is_published and not request.env.user._is_internal()) or not event.meeting_room_allow_creation:
            raise Forbidden()

        name = post.get("name")
        summary = post.get("summary")
        target_audience = post.get("audience")
        lang_code = post.get("lang_code")
        max_capacity = post.get("capacity")

        # get the record to be sure they really exist
        lang = request.env["res.lang"].search([("code", "=", lang_code)], limit=1)

        if not lang or max_capacity == "no_limit":
            raise Forbidden()

        meeting_room = request.env["event.meeting.room"].sudo().create({
            "name": name,
            "summary": summary,
            "target_audience": target_audience,
            "is_pinned": False,
            "event_id": event.id,
            "room_lang_id": lang.id,
            "room_max_capacity": max_capacity,
            "is_published": True,
        })
        _logger.info("New meeting room (%s) created by %s (uid %s)" % (name, request.httprequest.remote_addr, request.env.uid))

        return request.redirect(f"/event/{request.env['ir.http']._slug(event)}/meeting_room/{request.env['ir.http']._slug(meeting_room)}")

    @http.route(["/event/active_langs"], type="json", auth="public")
    def active_langs(self):
        return request.env["res.lang"].sudo().get_installed()

    # ------------------------------------------------------------
    # ROOM PAGE VIEW
    # ------------------------------------------------------------

    @http.route('''/event/<model('event.event', "[('community_menu', '=', True)]"):event>/meeting_room/<model("event.meeting.room","[('event_id','=',event.id)]"):meeting_room>''',
                type="http", auth="public", website=True, sitemap=True)
    def event_meeting_room_page(self, event, meeting_room, **post):
        """Display the meeting room frontend view.

        :param event: Event for which we display the meeting rooms
        :param meeting_room: Meeting Room to display
        """
        if meeting_room not in event.sudo().meeting_room_ids:
            raise NotFound()

        if not meeting_room.has_access('read'):
            raise Forbidden()

        meeting_room = meeting_room.sudo()

        return request.render(
            "website_event_meet.event_meet_main",
            self._event_meeting_room_page_get_values(event, meeting_room),
        )

    def _event_meeting_room_page_get_values(self, event, meeting_room):
        # search for meeting room list. Set a limit to 6 because it is better than 5 or 7
        meeting_rooms_other = request.env['event.meeting.room'].sudo().search([
            ('event_id', '=', event.id), ('id', '!=', meeting_room.id), ('is_published', '=', True),
        ], limit=6)

        if not request.env.user.has_group("event.group_event_manager"):
            # only the event manager can see meeting rooms which are full
            meeting_rooms_other = meeting_rooms_other.filtered(lambda m: not m.room_is_full)

        meeting_rooms_other = meeting_rooms_other.sorted(self._sort_event_rooms, reverse=True)

        return {
            # event information
            'event': event,
            'main_object': meeting_room,
            'meeting_room': meeting_room,
            # sidebar
            'meeting_rooms_other': meeting_rooms_other,
            # options
            'option_widescreen': True,
            'is_event_user': request.env.user.has_group('event.group_event_registration_desk'),
        }
