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

from threading import Event, RLock
from time import time
from typing import Optional, List, Dict
from ovos_utils.log import LOG
from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin


class NeonPhalPluginSkillAPI(PHALPlugin):
    def __init__(
        self, bus=None, name="neon-phal-plugin-skill-api", config=None
    ):
        PHALPlugin.__init__(self, bus, name, config)
        self.refresh_timeout_seconds = 60
        self._available_apis: Dict[str, dict] = dict()
        self._waiter = Event()
        self._update_lock = RLock()
        self._register_listeners()

        # Check if skills service already started
        skills_status = self.bus.wait_for_response(Message("mycroft.skills.is_ready"))
        if isinstance(skills_status, Message) and skills_status.data.get("status"):
            LOG.info("Skills service already started")
            self.update_available_apis()

    def _register_listeners(self):
        """
        Registers Messagebus listeners.
        """
        self.bus.on("mycroft.ready", self._on_ready)
        self.bus.on("neon.skill_api.update", self.update_available_apis)
        self.bus.on("neon.skill_api.get", self.get_available_apis)

    def _on_ready(self, _: Optional[Message] = None):
        """
        Query available Skill APIs when core services are ready
        @param message: "mycroft.ready" Message
        """
        self._waiter.wait(15)  # Pad to resolve race conditions
        self.update_available_apis()

    def _get_enabled_skills(self) -> List[str]:
        """
        Get a list of active skill IDs to query for available API methods.
        """
        response = self.bus.wait_for_response(
            Message(
                "skillmanager.list",
                context={"source": [self.name], "destination": ["skills"]},
            ),
            "mycroft.skills.list",
        )
        if not isinstance(response, Message):
            LOG.warning("No active skills reported")
            return []
        skill_ids = [
            skill["id"]
            for skill in response.data.values()
            if skill.get("active")
        ]
        if not skill_ids:
            LOG.warning("No active skills found")
        return skill_ids

    def _get_skill_api_methods(self, skill_id: str) -> Dict[str, dict]:
        """
        Get a dictionary of available API methods for a given skill
        """
        response = self.bus.wait_for_response(
            Message(
                f"{skill_id}.public_api",
                context={"source": [self.name], "destination": ["skills"]},
            ),
        )
        if not isinstance(response, Message):
            LOG.warning(f"No API method response for skill {skill_id}")
            return {}
        return response.data

    def update_available_apis(self, _: Optional[Message] = None):
        """
        Get an updated dictionary of available APIs for all active skills.
        """
        timeout = time() + self.refresh_timeout_seconds
        with self._update_lock:
            enabled_skills = self._get_enabled_skills()
            while not enabled_skills and time() < timeout:
                self._waiter.wait(5)
                enabled_skills = self._get_enabled_skills()
            for skill_id in enabled_skills:
                methods = self._get_skill_api_methods(skill_id)
                LOG.info(
                    f"Found {len(methods)} API methods for skill {skill_id}"
                )
                self._available_apis[skill_id] = methods
        LOG.info(f"Updated Skill APIs for {len(enabled_skills)} skills")

    def get_available_apis(self, message: Message):
        """
        Handle an request and respond with available APIs.
        @param message: `neon.skill_api.get` Message
        """
        if not self._available_apis:
            LOG.warning("No available APIs found, updating...")
            self.update_available_apis()
        LOG.debug("Handling request for available APIs")
        self.bus.emit(message.response(data=self._available_apis))

