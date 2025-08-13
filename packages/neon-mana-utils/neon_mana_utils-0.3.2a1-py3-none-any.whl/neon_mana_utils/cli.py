# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# BSD-3
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

import click
import json

from pprint import pformat
from click_default_group import DefaultGroup
from mycroft_bus_client.client import MessageBusClient

from neon_mana_utils.config import get_messagebus_config
from neon_mana_utils.version import __version__


@click.group("mana", cls=DefaultGroup,
             no_args_is_help=True, invoke_without_command=True,
             help="Mana: Message Application for Neon AI.\n\n"
                  "See also: mana COMMAND --help")
@click.option("--version", "-v", is_flag=True, required=False,
              help="Print the current version")
def neon_mana_cli(version: bool = False):
    if version:
        click.echo(f"Mana version {__version__}")


@neon_mana_cli.command(help="Set Messagebus Config")
@click.option('--host', '-h', default="0.0.0.0",
              help="Default Host (IP or hostname)")
@click.option('--port', '-p', default=8181,
              help="Default Port")
@click.option('--ssl', default=False,
              help="Use SSL")
@click.option('--route', '-r', default="/core",
              help="Default Route")
def configure_messagebus(host, port, route, ssl):
    from neon_mana_utils.config import set_messagebus_config
    set_messagebus_config(host, port, route, ssl)


@neon_mana_cli.command(help="Show configurations")
def print_config():
    from neon_mana_utils.config import print_config, get_config_dir
    conf = print_config()
    click.echo(f"Config Path: {get_config_dir()}\n")
    click.echo(conf)


@neon_mana_cli.command(help="Monitor messages sent over the messagebus")
@click.option('--include', '-i', multiple=True,
              help="Optional msg_type prefix to include in output")
@click.option('--exclude', '-e', multiple=True,
              help="Optional msg_type prefix to exclude from output")
@click.option('--format', '-f', is_flag=True, default=False,
              help="Format printed message outputs")
@click.option('--host', '-h', default=None,
              help="host to connect to (IP or hostname)")
@click.option('--port', '-p', default=None,
              help="port to connect to")
@click.option('--ssl', default=False,
              help="Connect using secured websocket")
@click.option('--route', '-r', default=None,
              help="websocket route to connect to")
@click.option('--include-session', '-s', is_flag=True,
              help="Include session context in output")
def tail_messagebus(host, port, route, ssl, format, include, exclude,
                    include_session):
    from neon_mana_utils.messagebus import tail_messagebus
    default = get_messagebus_config()
    config = {"host": host or default["host"],
              "port": port or default["port"],
              "route": route or default["route"],
              "ssl": ssl or default["ssl"]}
    client = MessageBusClient(**config)
    client.run_in_thread()
    tail_messagebus(include, exclude, format, True, client, include_session)
    click.echo("Exiting")


@neon_mana_cli.command(help="Start listening immediately")
def listen():
    from neon_mana_utils.core_commands import start_listening
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    start_listening(client)


@neon_mana_cli.command(help="Emit a stop message")
def stop():
    from neon_mana_utils.core_commands import stop
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    stop(client)


@neon_mana_cli.command(help="Emit a minimal user input message")
@click.option('--lang', '-l', default="en-us",
              help="Language of the input text")
@click.argument('utterance')
def say_to(utterance, lang):
    from neon_mana_utils.core_commands import say_to
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    say_to(client, utterance, lang)


@neon_mana_cli.command(help="Emit a minimal speak message")
@click.argument('utterance')
def speak(utterance):
    from neon_mana_utils.core_commands import speak
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    speak(client, utterance)


@neon_mana_cli.command(help="Get an STT response")
@click.option('--file', '-f', default=None,
              help="File to transcribe")
@click.option('--lang', '-l', default="en-us",
              help="Language of audio in file")
@click.option('--include-session', '-s', is_flag=True,
              help="Include session context in output")
def get_stt(file, lang, include_session):
    from neon_mana_utils.bus_api import get_stt

    if not file:
        click.echo("No audio file specified")
        return

    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_stt(client, audio_path=file, lang=lang)
    if message:
        if not include_session:
            message.context.pop("session", None)
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Get a TTS response")
@click.option('--text', '-t', default=None,
              help="Text to synthesize")
def get_tts(text):
    from neon_mana_utils.bus_api import get_tts

    if not text:
        click.echo("No text specified")

    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_tts(client, text)
    if message:
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Send an audio file for processing")
@click.option('--lang', '-l', default="en-us",
              help="Language of audio in file")
@click.argument("file")
def send_audio(lang, file):
    from neon_mana_utils.bus_api import audio_input
    if not file:
        click.echo("No file specified")
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    try:
        message = audio_input(client, file, lang=lang)
    except FileNotFoundError as e:
        click.echo(e)
        message = None
    if message:
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Get a skill response")
@click.option('--utterance', '-u',
              help="Input utterance to send to skills")
@click.option('--lang', '-l', default="en-us",
              help="Language of the input utterance")
@click.option('--include-session', '-s', is_flag=True,
              help="Include session context in output")
def get_response(utterance, lang, include_session):
    from neon_mana_utils.bus_api import get_response
    # TODO: Handle message loading DM
    if not utterance:
        click.echo("Empty utterance received")
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_response(client, utterance, lang)
    if message:
        if not include_session:
            message.context.pop("session", None)
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Send a json or yaml serialized message")
@click.option('--response', '-r', default=None,
              help="Optional response message type to listen to")
@click.option('--include-session', '-s', is_flag=True,
              help="Include session context in output")
@click.argument('file')
def send_message_file(response, include_session, file):
    from neon_mana_utils.messagebus import send_message_file
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    try:
        response = send_message_file(file, client, response)
        if response:
            if not include_session:
                response.context.pop('session', None)
            click.echo(pformat(json.loads(response.serialize())))
        elif response:
            click.echo("No Response")
        else:
            click.echo("Message Sent")
    except Exception as e:
        click.echo(e)


@neon_mana_cli.command(help="Send a simple message with no data or context")
@click.option('--response', '-r', is_flag=True,
              help="Listen for `.response` message")
@click.option('--include-session', '-s', is_flag=True,
              help="Include session context in output")
@click.argument('message')
def send_message(response, include_session, message):
    from neon_mana_utils.messagebus import send_message_simple
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    resp = send_message_simple(message, client, response)
    if response:
        if not resp:
            click.echo("No Response")
            return
        if not include_session:
            resp.context.pop('session', None)
        click.echo(pformat(json.loads(resp.serialize())))
    else:
        click.echo(f"Sent: {message}")


@neon_mana_cli.command(help="Check if a core service is alive")
@click.option('--namespace', '-n', default="mycroft",
              help="Namespace of service to query")
@click.argument("service")
def check_service_alive(namespace, service):
    from neon_mana_utils.status import check_alive
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    ready = check_alive(client, service, namespace)
    if ready:
        click.echo(f"{namespace}.{service} is alive")
    else:
        click.echo(f"{namespace}.{service} is NOT alive")


@neon_mana_cli.command(help="Check if a core service is ready")
@click.option('--namespace', '-n', default="mycroft",
              help="Namespace of service to query")
@click.argument("service")
def check_service_ready(namespace, service):
    from neon_mana_utils.status import check_ready
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    ready = check_ready(client, service, namespace)
    if ready:
        click.echo(f"{namespace}.{service} is ready")
    else:
        click.echo(f"{namespace}.{service} is NOT ready")


@neon_mana_cli.command(help="Get a list of available skills")
def get_skills_list():
    from neon_mana_utils.skills import get_skills_list
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    skills = get_skills_list(client)
    click.echo(pformat(skills))


@neon_mana_cli.command(help="Get the API for a particular skill")
@click.argument("skill_id")
def get_skill_api(skill_id):
    from neon_mana_utils.skills import get_skill_api
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    api = get_skill_api(client, skill_id)
    click.echo(pformat(api))


@neon_mana_cli.command(help="Get a list of available skill APIs")
def get_all_skills_api():
    from neon_mana_utils.skills import get_all_skills_api
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    skills = get_all_skills_api(client)
    click.echo(pformat(skills))


@neon_mana_cli.command(help="Get a list of active skills")
def get_active_skills():
    from neon_mana_utils.skills import get_active_skills
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    skills = get_active_skills(client)
    click.echo(pformat(skills))


@neon_mana_cli.command(help="Get a list of Adapt intents")
@click.option("--lang", "-l", default="en-us")
def get_adapt_manifest(lang):
    from neon_mana_utils.skills import get_adapt_manifest
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    intents = get_adapt_manifest(client, lang)
    click.echo(pformat(intents))


@neon_mana_cli.command(help="Get a list of Padatious intents")
@click.option("--lang", "-l", default="en-us")
def get_padatious_manifest(lang):
    from neon_mana_utils.skills import get_padatious_manifest
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    intents = get_padatious_manifest(client, lang)
    click.echo(pformat(intents))


@neon_mana_cli.command(help="Deactivate a skill for converse handling")
@click.argument("skill")
def deactivate_skill(skill):
    from neon_mana_utils.skills import deactivate_skill
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    deactivate_skill(client, skill)
    click.echo(f"Requested deactivation of: {skill}")


@neon_mana_cli.command(help="Activate a skill for converse handling")
@click.argument("skill")
def activate_skill(skill):
    from neon_mana_utils.skills import activate_skill
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    activate_skill(client, skill)
    click.echo(f"Requested activation of: {skill}")


@neon_mana_cli.command(help="Unload a skill from the Skill Manager")
@click.argument("skill")
def unload_skill(skill):
    from neon_mana_utils.skills import unload_skill
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    unload_skill(client, skill)
    click.echo(f"Requested unload of: {skill}")


@neon_mana_cli.command(help="Load a skill in the Skill Manager")
@click.argument("skill")
def load_skill(skill):
    from neon_mana_utils.skills import load_skill
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    load_skill(client, skill)
    click.echo(f"Requested load of: {skill}")


@neon_mana_cli.command(help="Unload all except one skill Skill Manager")
@click.argument("skill")
def unload_except(skill):
    from neon_mana_utils.skills import unload_skills_except
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    unload_skills_except(client, skill)
    click.echo(f"Requested load of: {skill}")


@neon_mana_cli.command(help="Determine Adapt Intent")
@click.option("--lang", "-l", default="en-us")
@click.argument("utterance")
def get_adapt_response(lang, utterance):
    from neon_mana_utils.skills import get_adapt_intent
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    intent = get_adapt_intent(client, lang, utterance)
    click.echo(pformat(intent))


@neon_mana_cli.command(help="Determine Padatious Intent")
@click.option("--lang", "-l", default="en-us")
@click.argument("utterance")
def get_padatious_response(lang, utterance):
    from neon_mana_utils.skills import get_padatious_intent
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    intent = get_padatious_intent(client, lang, utterance)
    click.echo(pformat(intent))
