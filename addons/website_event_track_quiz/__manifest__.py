# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


{
    'name': 'Quizzes on Tracks',
    'category': 'Marketing/Events',
    'sequence': 1007,
    'version': '1.0',
    'summary': 'Quizzes on tracks',
    'website': 'https://www.orj.net/app/events',
    'depends': [
        'website_profile',
        'website_event_track',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/event_leaderboard_templates.xml',
        'views/event_quiz_views.xml',
        'views/event_quiz_question_views.xml',
        'views/event_track_views.xml',
        'views/event_track_visitor_views.xml',
        'views/event_menus.xml',
        'views/event_quiz_templates.xml',
        'views/event_track_templates_page.xml',
        'views/event_event_views.xml',
        'views/event_type_views.xml'
    ],
    'demo': [
        'data/quiz_demo.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_frontend': [
            'website_event_track_quiz/static/src/scss/event_quiz.scss',
            'website_event_track_quiz/static/src/js/event_quiz.js',
            'website_event_track_quiz/static/src/js/event_quiz_leaderboard.js',
            'website_event_track_quiz/static/src/xml/quiz_templates.xml',
        ],
    },
    'license': 'LGPL-3',
}
