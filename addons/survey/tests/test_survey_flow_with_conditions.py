# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.survey.tests import common
from orj.tests import tagged
from orj.tests.common import HttpCase


@tagged('-at_install', 'post_install', 'functional')
class TestSurveyFlowWithConditions(common.TestSurveyCommon, HttpCase):
    def test_conditional_flow_with_scoring(self):
        with self.with_user('survey_user'):
            survey = self.env['survey.survey'].create({
                'title': 'Survey',
                'access_mode': 'public',
                'questions_layout': 'page_per_section',
                'scoring_type': 'scoring_with_answers',
                'scoring_success_min': 85.0,
            })

            page_0 = self.env['survey.question'].with_user(self.survey_manager).create({
                'title': 'First page',
                'survey_id': survey.id,
                'sequence': 1,
                'is_page': True,
                'question_type': False,
            })

            q01 = self._add_question(
                page_0, 'Question 1', 'simple_choice',
                sequence=1,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2'},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4', 'is_correct': True, 'answer_score': 1.0}
                ])

            q02 = self._add_question(
                page_0, 'Question 2', 'simple_choice',
                sequence=2,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                triggering_answer_ids=q01.suggested_answer_ids.filtered(lambda q: q.is_correct),
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2', 'is_correct': True, 'answer_score': 1.0},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4'}
                ])

            q03 = self._add_question(
                page_0, 'Question 3', 'simple_choice',
                sequence=1,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2'},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4', 'is_correct': True, 'answer_score': 1.0}
                ])

            q03_suggested_answers_triggering_q04 = q03.suggested_answer_ids.filtered(lambda q: q.is_correct)

            self._add_question(  # q04
                page_0, 'Question 4', 'simple_choice',
                sequence=2,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                triggering_answer_ids=q03_suggested_answers_triggering_q04,
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2', 'is_correct': True, 'answer_score': 1.0},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4'}
                ])

            q05 = self._add_question(
                page_0, 'Question 5', 'simple_choice',
                sequence=1,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2'},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4', 'is_correct': True, 'answer_score': 1.0}
                ])

            q06 = self._add_question(
                page_0, 'Question 6', 'simple_choice',
                sequence=2,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                triggering_answer_ids=q05.suggested_answer_ids.filtered(lambda q: q.is_correct),
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2', 'is_correct': True, 'answer_score': 1.0},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4'}
                ])

            q03_suggested_answers_triggering_q07 = q03.suggested_answer_ids - q03_suggested_answers_triggering_q04
            # Make sure to have a case with multiple possible triggers.
            self.assertGreater(len(q03_suggested_answers_triggering_q07), 1)

            q07 = self._add_question(
                page_0, 'Question 7', 'simple_choice',
                sequence=2,
                constr_mandatory=True, constr_error_msg='Please select an answer', survey_id=survey.id,
                triggering_answer_ids=q03_suggested_answers_triggering_q07,
                labels=[
                    {'value': 'Answer 1'},
                    {'value': 'Answer 2', 'is_correct': True, 'answer_score': 1.0},
                    {'value': 'Answer 3'},
                    {'value': 'Answer 4'}
                ])

        # User opens start page
        self._access_start(survey)

        # -> this should have generated a new user_input with a token
        user_inputs = self.env['survey.user_input'].search([('survey_id', '=', survey.id)])
        self.assertEqual(len(user_inputs), 1)
        self.assertEqual(len(user_inputs.predefined_question_ids), 7)
        answer_token = user_inputs.access_token

        # User begins survey with first page
        response = self._access_page(survey, answer_token)
        self.assertResponse(response, 200)
        csrf_token = self._find_csrf_token(response.text)

        r = self._access_begin(survey, answer_token)
        self.assertResponse(r, 200)

        answers = {
            q01: q01.suggested_answer_ids[3],  # Right
            q02: q02.suggested_answer_ids[1],  # Right
            q03: q03.suggested_answer_ids[0],  # Wrong
            q05: q05.suggested_answer_ids[3],  # Right
            q06: q06.suggested_answer_ids[2],  # Wrong
            q07: q07.suggested_answer_ids[1],  # Right
        }

        self._answer_page(page_0, answers, answer_token, csrf_token)
        self.assertEqual(len(user_inputs.predefined_question_ids), 6, "q04 should have been removed as not triggered.")

        user_inputs.invalidate_recordset()
        self.assertEqual(round(user_inputs.scoring_percentage), 67, "Four right answers out of six questions asked.")
        self.assertFalse(user_inputs.scoring_success)
