# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging
import os
import re
import subprocess

try:
    import screeninfo
except ImportError:
    screeninfo = None
    import RPi.GPIO as GPIO
    from vcgencmd import Vcgencmd

from orj.addons.hw_drivers.interface import Interface
from orj.addons.hw_drivers.tools import helpers

_logger = logging.getLogger(__name__)

MIN_IMAGE_VERSION_WAYLAND = 25.03

class DisplayInterface(Interface):
    _loop_delay = 3
    connection_type = 'display'

    def get_devices(self):
        display_devices = {}
        dummy_display = {
            'distant_display': {
                'identifier': 'distant_display',
                'name': 'Distant Display',
            }
        }

        if screeninfo is None:
            # On IoT image < 24.10 we don't have screeninfo installed, so we can't get the connected displays
            # We use old method to get the connected display
            hdmi_ports = {'hdmi_0': 2, 'hdmi_1': 7} if 'Pi 4' in GPIO.RPI_INFO.get('TYPE') else {'hdmi_0': 2}
            try:
                for x_screen, port in enumerate(hdmi_ports):
                    if Vcgencmd().display_power_state(hdmi_ports.get(port)) == 'on':
                        display_devices[port] = self._add_device(port, x_screen)
            except subprocess.CalledProcessError:
                _logger.warning('Vcgencmd "display_power_state" method call failed')

            return display_devices or dummy_display

        if float(helpers.get_version()[1:]) >= MIN_IMAGE_VERSION_WAYLAND:
            randr_result = subprocess.run(['wlr-randr'], capture_output=True, text=True)
            if randr_result.returncode != 0:
                return {}
            displays = re.findall(r"(?<=\()HDMI-A-\d(?=\))", randr_result.stdout)
            return {
                monitor: self._add_device(monitor, x_screen)
                for x_screen, monitor in enumerate(displays)
            }

        try:
            os.environ['DISPLAY'] = ':0'
            for x_screen, monitor in enumerate(screeninfo.get_monitors()):
                display_devices[monitor.name] = self._add_device(monitor.name, x_screen)
            return display_devices or dummy_display
        except screeninfo.common.ScreenInfoError:
            # If no display is connected, screeninfo raises an error, we return the distant display
            return dummy_display

    @classmethod
    def _add_device(cls, display_identifier, x_screen):
        """Creates a display_device dict.

        :param display_identifier: the identifier of the display
        :param x_screen: the x screen number
        :return: the display device dict
        """

        return {
            'identifier': display_identifier,
            'name': 'Display - ' + display_identifier,
            'x_screen': str(x_screen),
        }
