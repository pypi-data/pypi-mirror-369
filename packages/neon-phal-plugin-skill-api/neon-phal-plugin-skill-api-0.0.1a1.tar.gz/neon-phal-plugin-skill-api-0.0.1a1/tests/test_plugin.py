# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from unittest.mock import MagicMock, patch
from ovos_bus_client import Message
from neon_phal_plugin_skill_api import NeonPhalPluginSkillAPI


class TestSkillApi(unittest.TestCase):
    def setUp(self):
        self.bus = MagicMock()
        self.plugin = NeonPhalPluginSkillAPI(bus=self.bus)

    def test_00_init(self):
        self.assertIsInstance(self.plugin, NeonPhalPluginSkillAPI)
        self.assertEqual(self.plugin.name, "neon-phal-plugin-skill-api")
        self.assertEqual(self.plugin.bus, self.bus)

        # Check Messagebus event listeners
        self.bus.on.assert_any_call("mycroft.ready", self.plugin._on_ready)
        self.bus.on.assert_any_call(
            "neon.skill_api.update", self.plugin.update_available_apis
        )
        self.bus.on.assert_any_call(
            "neon.skill_api.get", self.plugin.get_available_apis
        )

        self.bus.wait_for_response.assert_called_once_with(
            Message("mycroft.skills.is_ready")
        )

    def test_get_active_skills(self):
        self.bus.reset_mock()
        
        # Test with no response
        self.bus.wait_for_response.return_value = None
        skills = self.plugin._get_enabled_skills()
        self.bus.wait_for_response.assert_called_once_with(
            Message(
                "skillmanager.list",
                context={
                    "source": ["neon-phal-plugin-skill-api"],
                    "destination": ["skills"],
                },
            ),
            "mycroft.skills.list",
        )
        self.assertEqual(skills, [])

        # Test with mock response data
        self.bus.reset_mock()
        mock_response_data = {
            'skill-test1.neongeckocom': {'active': True, 'id': 'skill-test1.neongeckocom'},
            'skill-test2.neongeckocom': {'active': False, 'id': 'skill-test2.neongeckocom'},
            'skill-test3.neongeckocom': {'active': True, 'id': 'skill-test3.neongeckocom'}
        }
        mock_response = Message("mycroft.skills.list", data=mock_response_data)
        self.bus.wait_for_response.return_value = mock_response
        
        skills = self.plugin._get_enabled_skills()
        expected_skills = ['skill-test1.neongeckocom', 'skill-test3.neongeckocom']
        self.assertEqual(sorted(skills), sorted(expected_skills))

    def test_get_skill_api_methods(self):
        self.bus.reset_mock()
        skill_id = "test_skill.neongeckocom"
        
        # Test with no response
        self.bus.wait_for_response.return_value = None
        methods = self.plugin._get_skill_api_methods(skill_id)
        self.bus.wait_for_response.assert_called_once_with(
            Message(
                f"{skill_id}.public_api",
                context={
                    "source": ["neon-phal-plugin-skill-api"],
                    "destination": ["skills"],
                },
            )
        )
        self.assertEqual(methods, {})

        # Test with mock response data
        self.bus.reset_mock()
        mock_api_data = {
            'skill_info_examples': {
                'help': '\n        API Method to build a list of examples as listed in skill metadata.\n        ',
                'type': 'test_skill.neongeckocom.skill_info_examples'
            },
            'get_skill_status': {
                'help': 'Returns the current status of the skill',
                'type': 'test_skill.neongeckocom.get_skill_status'
            }
        }
        mock_response = Message(f"{skill_id}.public_api", data=mock_api_data)
        self.bus.wait_for_response.return_value = mock_response
        
        methods = self.plugin._get_skill_api_methods(skill_id)
        expected_methods = mock_api_data
        self.assertEqual(methods, expected_methods)

    @patch.object(NeonPhalPluginSkillAPI, '_get_skill_api_methods')
    @patch.object(NeonPhalPluginSkillAPI, '_get_enabled_skills')
    def test_update_available_apis(self, mock_get_skills, mock_get_api_methods):
        self.plugin.refresh_timeout_seconds = 0
        # Test with no enabled skills
        mock_get_skills.return_value = []
        self.plugin.update_available_apis()
        self.assertEqual(self.plugin._available_apis, {})
        
        # Test with enabled skills and API methods
        test_skills = ['skill-test1.neongeckocom', 'skill-test2.neongeckocom']
        test_apis = {
            'skill-test1.neongeckocom': {
                'skill_info_examples': {
                    'help': 'API Method to build a list of examples',
                    'type': 'skill-test1.neongeckocom.skill_info_examples'
                }
            },
            'skill-test2.neongeckocom': {
                'get_status': {
                    'help': 'Returns skill status',
                    'type': 'skill-test2.neongeckocom.get_status'
                },
                'restart': {
                    'help': 'Restarts the skill',
                    'type': 'skill-test2.neongeckocom.restart'
                }
            }
        }
        
        def mock_get_api_methods_side_effect(skill_id):
            return test_apis.get(skill_id, {})
        
        mock_get_skills.return_value = test_skills
        mock_get_api_methods.side_effect = mock_get_api_methods_side_effect
        
        self.plugin.update_available_apis()
        self.assertEqual(self.plugin._available_apis, test_apis)

    @patch.object(NeonPhalPluginSkillAPI, 'update_available_apis')
    def test_get_available_apis(self, mock_update):
        # Test when APIs are already available
        test_apis = {
            'skill-test1.neongeckocom': {
                'skill_info_examples': {
                    'help': 'API Method to build a list of examples',
                    'type': 'skill-test1.neongeckocom.skill_info_examples'
                }
            }
        }
        self.plugin._available_apis = test_apis
        
        test_message = Message("neon.skill_api.get", context={"ctx": "test"})
        self.plugin.get_available_apis(test_message)
        
        # Should not call update since APIs are already available
        mock_update.assert_not_called()
        
        # Check that bus.emit was called with correct response
        self.bus.emit.assert_called_once()
        emitted_message = self.bus.emit.call_args[0][0]
        self.assertEqual(emitted_message.msg_type, "neon.skill_api.get.response")
        self.assertEqual(emitted_message.data, test_apis)
        self.assertEqual(emitted_message.context, {"ctx": "test"})
        
        # Test when no APIs are available (should trigger update)
        self.bus.reset_mock()
        mock_update.reset_mock()
        self.plugin._available_apis = {}
        
        self.plugin.get_available_apis(test_message)
        
        # Should call update since no APIs are available
        mock_update.assert_called_once()
        
        # Should still emit response (with empty data)
        self.bus.emit.assert_called_once()
        emitted_message = self.bus.emit.call_args[0][0]
        self.assertEqual(emitted_message.msg_type, "neon.skill_api.get.response")
        self.assertEqual(emitted_message.data, {})
