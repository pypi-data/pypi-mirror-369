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

from mycroft_bus_client.client import MessageBusClient
from neon_mana_utils.constants import Message


def check_ready(bus: MessageBusClient,
                service: str, namespace: str = "mycroft") -> bool:
    """
    Check if a service is reporting ready
    :param bus: Connected MessageBusClient to query
    :param service: Registered service name to query (i.e. skills, audio)
    :param namespace: Namespace service is registered in
    :returns: Service ready state
    """
    resp = bus.wait_for_response(Message(f"{namespace}.{service}.is_ready",
                                         context={"source": ["mana"],
                                                  "destination": [service]}))
    if resp:
        return resp.data.get("status")
    return False


def check_alive(bus: MessageBusClient,
                service: str, namespace: str = "mycroft") -> bool:
    """
    Check if a service is reporting ready
    :param bus: Connected MessageBusClient to query
    :param service: Registered service name to query (i.e. skills, audio)
    :param namespace: Namespace service is registered in
    :returns: Service ready state
    """
    resp = bus.wait_for_response(Message(f"{namespace}.{service}.is_alive",
                                         context={"source": ["mana"],
                                                  "destination": [service]}))
    if resp:
        return resp.data.get("status")
    return False
