import logging
import os
from configparser import ConfigParser, SectionProxy
from functools import wraps

from basecmd import BaseCmd

from .exceptions import SnipsClarificationError, SnipsError
from .i18n import get_translations
from .intent import IntentPayload
from .log import LoggingMixin
from .snips import SnipsClient, on_intent

__all__ = ("Skill", "intent", "min_confidence", "PARDON", "require_slot")
_, ngettext = get_translations(__file__, "snips_skill")


PARDON = _("Pardon?")


class Skill(BaseCmd, LoggingMixin, SnipsClient):
    "Base class for Snips actions."

    CONFIGURATION_FILE = "config.ini"

    DEFAULT_SECTION = "DEFAULT"
    STANDARD_SECTIONS = (DEFAULT_SECTION, "global", "secret")

    configuration: ConfigParser

    def __init__(
        self,
        client_id: str | None = None,
        clean_session: bool = True,
        userdata=None,
    ):
        # Work around a Paho cleanup bug if called with -h or illegal args
        self._sock = self._sockpairR = self._sockpairW = None
        super(Skill, self).__init__(
            client_id=client_id, clean_session=clean_session, userdata=userdata
        )

        self.configuration = ConfigParser()
        if os.path.isfile(self.options.config):
            self.log.debug("Reading configuration: %s", self.options.config)
            self.configuration.read(self.options.config, encoding="UTF-8")
            self.process_config()
        else:
            self.log.warning("Configuration %s not found", self.options.config)

    def add_arguments(self) -> None:
        super().add_arguments()
        self.parser.add_argument(
            "-c",
            "--config",
            default=self.CONFIGURATION_FILE,
            help="Configuration file (%s)" % self.CONFIGURATION_FILE,
        )

    def process_config(self) -> None:
        "May be overridden"
        pass

    def get_config(self, section: str = DEFAULT_SECTION) -> SectionProxy:
        "Get a configuration section, or DEFAULT values"
        if section in self.configuration:
            return self.configuration[section]
        return self.configuration[self.DEFAULT_SECTION]


def intent(
    intent: str, qos: int = 1, log_level: int = logging.NOTSET, silent: bool = False
):
    """Decorator for intent handlers.
    :param intent: Intent name.
    :param qos: MQTT quality of service.
    :param log_level: Log intents at this level, if set.
    :param silent: Set to `True` for intents that should return `None`
    The wrapped function gets a parsed `IntentPayload` object
    instead of a JSON `msg.payload`.
    If a `SnipsClarificationError` is raised, the session continues with a question.
    Otherwise, the session is ended.
    """

    def wrapper(method):
        @on_intent(intent, qos=qos, payload_converter=None)
        @wraps(method)
        def wrapped(client, userdata, msg):
            msg.payload = IntentPayload.model_validate_json(msg.payload)
            if log_level:
                client.log_intent(msg.payload, level=log_level)
            try:
                result = method(client, userdata, msg)
                if log_level and result:
                    client.log_response(result, level=log_level)
                if result is None and silent:
                    client.end_session(msg.payload.session_id, qos=qos)
                    return
                raise SnipsError(result)
            except SnipsClarificationError as sce:
                if log_level:
                    client.log_response(sce, level=log_level)
                client.continue_session(
                    msg.payload.session_id,
                    str(sce),
                    [sce.intent] if sce.intent else None,
                    slot=sce.slot,
                    custom_data=sce.custom_data,
                )
            except SnipsError as e:
                client.end_session(msg.payload.session_id, str(e), qos=qos)

        return wrapped

    return wrapper


def min_confidence(threshold: float, prompt: str = PARDON):
    """Decorator that requires a minimum intent confidence, or else asks the user.
    :param threshold: Minimum confidence (0.0 - 1.0)
    :param prompt: Question for the user
    """

    def wrapper(method):
        @wraps(method)
        def wrapped(client, userdata, msg):
            if msg.payload.intent.confidence_score >= threshold:
                return method(client, userdata, msg)
            raise SnipsClarificationError(prompt)

        return wrapped

    return wrapper


def require_slot(slot: str, prompt: str, kind: str | None = None):
    """Decorator that checks whether a slot is present, or else asks the user.
    :param slot: Slot name
    :param prompt: Question for the user
    :param kind: Optionally, the slot is expected to be of the given kind.
    """

    def wrapper(method):
        @wraps(method)
        def wrapped(client, userdata, msg):
            if slot in msg.payload.slots and (
                kind is None or msg.payload.slot_values[slot].kind == kind
            ):
                return method(client, userdata, msg)
            raise SnipsClarificationError(prompt, msg.payload.intent.intent_name, slot)

        return wrapped

    return wrapper
