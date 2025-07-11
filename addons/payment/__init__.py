# Part of Orj. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from . import utils
from . import wizards


def setup_provider(env, code):
    env['payment.provider']._setup_provider(code)


def reset_payment_provider(env, code, **kwargs):
    env['payment.provider']._remove_provider(code, **kwargs)
