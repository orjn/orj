# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

""" Helper functions for reports testing.

    Please /do not/ import this file by default, but only explicitly call it
    through the code of python tests.
"""

import logging
import os
import tempfile
from lxml import etree
from subprocess import Popen, PIPE

from .. import api
from .safe_eval import safe_eval

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('orj.tests')


def try_report(cr, uid, rname, ids, data=None, context=None, our_module=None, report_type=None):
    """ Try to render a report <rname> with contents of ids

        This function should also check for common pitfalls of reports.
    """
    if context is None:
        context = {}
    _test_logger.info("  - Trying %s.create(%r)", rname, ids)

    env = api.Environment(cr, uid, context)

    res_data, res_format = env['ir.actions.report']._render(rname, ids, data=data)

    if not res_data:
        raise ValueError("Report %s produced an empty result!" % rname)

    _logger.debug("Have a %s report for %s, will examine it", res_format, rname)
    if res_format == 'pdf':
        if res_data[:5] != b'%PDF-':
            raise ValueError("Report %s produced a non-pdf header, %r" % (rname, res_data[:10]))
        res_text = None
        try:
            fd, rfname = tempfile.mkstemp(suffix=res_format)
            os.write(fd, res_data)
            os.close(fd)

            proc = Popen(['pdftotext', '-enc', 'UTF-8', '-nopgbrk', rfname, '-'], shell=False, stdout=PIPE, encoding="utf-8")
            res_text, _stderr = proc.communicate()
            os.unlink(rfname)
        except Exception:
            _logger.debug("Unable to parse PDF report: install pdftotext to perform automated tests.")

        if res_text:
            for line in res_text.splitlines():
                if ('[[' in line) or ('[ [' in line):
                    _logger.error("Report %s may have bad expression near: \"%s\".", rname, line[80:])
            # TODO more checks, what else can be a sign of a faulty report?
    elif res_format == 'html':
        pass
    else:
        _logger.warning("Report %s produced a \"%s\" chunk, cannot examine it", rname, res_format)
        return False

    _test_logger.info("  + Report %s produced correctly.", rname)
    return True

def try_report_action(cr, uid, action_id, active_model=None, active_ids=None,
                wiz_data=None, wiz_buttons=None,
                context=None, our_module=None):
    """Take an ir.actions.act_window and follow it until a report is produced

        :param cr:
        :param uid:
        :param action_id: the integer id of an action, or a reference to xml id
                of the act_window (can search [our_module.]+xml_id
        :param active_model:
        :param active_ids: call the action as if it had been launched
                from that model+ids (tree/form view action)
        :param wiz_data: a dictionary of values to use in the wizard, if needed.
                They will override (or complete) the default values of the
                wizard form.
        :param wiz_buttons: a list of button names, or button icon strings, which
                should be preferred to press during the wizard.
                Eg. 'OK' or 'fa-print'
        :param context:
        :param our_module: the name of the calling module (string), like 'account'
    """
    if not our_module and isinstance(action_id, str):
        if '.' in action_id:
            our_module = action_id.split('.', 1)[0]

    context = dict(context or {})
    # TODO context fill-up

    env = api.Environment(cr, uid, context)

    def log_test(msg, *args):
        _test_logger.info("  - " + msg, *args)

    datas = {}
    if active_model:
        datas['model'] = active_model
    if active_ids:
        datas['ids'] = active_ids

    if not wiz_buttons:
        wiz_buttons = []

    if isinstance(action_id, str):
        if '.' in action_id:
            _, act_xmlid = action_id.split('.', 1)
        else:
            if not our_module:
                raise ValueError('You cannot only specify action_id "%s" without a module name' % action_id)
            act_xmlid = action_id
            action_id = '%s.%s' % (our_module, action_id)
        action = env.ref(action_id)
        act_model, act_id = action._name, action.id
    else:
        assert isinstance(action_id, int)
        act_model = 'ir.actions.act_window'     # assume that
        act_id = action_id
        act_xmlid = '<%s>' % act_id

    def _exec_action(action, datas, env):
        # taken from client/modules/action/main.py:84 _exec_action()
        if isinstance(action, bool) or 'type' not in action:
            return
        # Updating the context : Adding the context of action in order to use it on Views called from buttons
        context = dict(env.context)
        if datas.get('id',False):
            context.update( {'active_id': datas.get('id',False), 'active_ids': datas.get('ids',[]), 'active_model': datas.get('model',False)})
        context1 = action.get('context', {})
        if isinstance(context1, str):
            context1 = safe_eval(context1, dict(context))
        context.update(context1)
        env = env(context=context)
        if action['type'] in ['ir.actions.act_window', 'ir.actions.submenu']:
            for key in ('res_id', 'res_model', 'view_mode',
                        'limit', 'search_view_id'):
                datas[key] = action.get(key, datas.get(key, None))

            view_id = False
            view_type = None
            if action.get('views', []):
                if isinstance(action['views'],list):
                    view_id, view_type = action['views'][0]
                    datas['view_mode']= view_type
                else:
                    if action.get('view_id', False):
                        view_id = action['view_id'][0]
            elif action.get('view_id', False):
                view_id = action['view_id'][0]

            if view_type is None:
                if view_id:
                    view_type = env['ir.ui.view'].browse(view_id).type
                else:
                    view_type = action['view_mode'].split(',')[0]

            assert datas['res_model'], "Cannot use the view without a model"
            # Here, we have a view that we need to emulate
            log_test("will emulate a %s view: %s#%s",
                        view_type, datas['res_model'], view_id or '?')

            model = env[datas['res_model']]
            view_res = model.get_view(view_id, view_type)
            assert view_res and view_res.get('arch'), "Did not return any arch for the view"
            view_data = {}
            arch = etree.fromstring(view_res['arch'])
            fields = [el.get('name') for el in arch.xpath('//field[not(ancestor::field)]')]
            if fields:
                view_data = model.default_get(fields)
            if datas.get('form'):
                view_data.update(datas.get('form'))
            if wiz_data:
                view_data.update(wiz_data)
            _logger.debug("View data is: %r", view_data)

            for fk in fields:
                # Default fields returns list of int, while at create()
                # we need to send a [(6,0,[int,..])]
                if model._fields[fk].type in ('one2many', 'many2many') \
                        and view_data.get(fk, False) \
                        and isinstance(view_data[fk], list) \
                        and not isinstance(view_data[fk][0], tuple) :
                    view_data[fk] = [(6, 0, view_data[fk])]

            action_name = action.get('name')
            try:
                from xml.dom import minidom
                cancel_found = False
                buttons = []
                dom_doc = minidom.parseString(view_res['arch'])
                if not action_name:
                    action_name = dom_doc.documentElement.getAttribute('name')

                for button in dom_doc.getElementsByTagName('button'):
                    button_weight = 0
                    if button.getAttribute('special') == 'cancel':
                        cancel_found = True
                        continue
                    if button.getAttribute('icon') == 'fa-times-circle':
                        cancel_found = True
                        continue
                    if button.getAttribute('default_focus') == '1':
                        button_weight += 20
                    if button.getAttribute('string') in wiz_buttons:
                        button_weight += 30
                    elif button.getAttribute('icon') in wiz_buttons:
                        button_weight += 10
                    string = button.getAttribute('string') or '?%s' % len(buttons)

                    buttons.append({
                        'name': button.getAttribute('name'),
                        'string': string,
                        'type': button.getAttribute('type'),
                        'weight': button_weight,
                    })
            except Exception as e:
                _logger.warning("Cannot resolve the view arch and locate the buttons!", exc_info=True)
                raise AssertionError(e.args[0])

            if not datas['res_id']:
                # it is probably an orm_memory object, we need to create
                # an instance
                datas['res_id'] = env[datas['res_model']].create(view_data).id

            if not buttons:
                raise AssertionError("view form doesn't have any buttons to press!")

            buttons.sort(key=lambda b: b['weight'])
            _logger.debug('Buttons are: %s', ', '.join([ '%s: %d' % (b['string'], b['weight']) for b in buttons]))

            res = None
            while buttons and not res:
                b = buttons.pop()
                log_test("in the \"%s\" form, I will press the \"%s\" button.", action_name, b['string'])
                if not b['type']:
                    log_test("the \"%s\" button has no type, cannot use it", b['string'])
                    continue
                if b['type'] == 'object':
                    #there we are! press the button!
                    rec = env[datas['res_model']].browse(datas['res_id'])
                    func = getattr(rec, b['name'], None)
                    if not func:
                        _logger.error("The %s model doesn't have a %s attribute!", datas['res_model'], b['name'])
                        continue
                    res = func()
                    break
                else:
                    _logger.warning("in the \"%s\" form, the \"%s\" button has unknown type %s",
                        action_name, b['string'], b['type'])
            return res

        elif action['type']=='ir.actions.report':
            if 'window' in datas:
                del datas['window']
            if not datas:
                datas = action.get('datas')
                if not datas:
                    datas = action.get('data')
            datas = datas.copy()
            ids = datas.get('ids')
            if 'ids' in datas:
                del datas['ids']
            res = try_report(cr, uid, action['report_name'], ids, datas, context, our_module=our_module)
            return res
        else:
            raise Exception("Cannot handle action of type %s" % act_model)

    log_test("will be using %s action %s #%d", act_model, act_xmlid, act_id)
    action = env[act_model].browse(act_id).read()[0]
    assert action, "Could not read action %s[%s]" % (act_model, act_id)
    loop = 0
    while action:
        loop += 1
        # This part tries to emulate the loop of the Gtk client
        if loop > 100:
            _logger.info("Passed %d loops, giving up", loop)
            raise Exception("Too many loops at action")
        log_test("it is an %s action at loop #%d", action.get('type', 'unknown'), loop)
        result = _exec_action(action, datas, env)
        if not isinstance(result, dict):
            break
        datas = result.get('datas', {})
        if datas:
            del result['datas']
        action = result

    return True
