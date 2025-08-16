import logging
from functools import partial, wraps
from pprint import pformat
from signal import SIGUSR1, signal
from typing import Any, Callable

from paho.mqtt.client import MQTTMessageInfo

from .expr import Parser
from .mqtt import decode_json, topic

__all__ = ("StateAwareMixin", "conditional", "when")


class StateAwareMixin:
    """Mixin for stateful MQTT clients.
    Status updates are recorded in-memory from MQTT topics,
    e.g. `status/#`.
    The message payload for status updates is JSON-converted if possible.
    The last known state is available in `self.current_state`.
    Subclasses may define handler methods using the @when decorator`.
    """

    log: logging.Logger
    conditions: dict[Parser.Expr, Callable] = {}
    expr_parser = Parser()
    update_log_level = logging.DEBUG

    def __init__(self, **kw):
        "Register topics and the state callcack."

        super(StateAwareMixin, self).__init__(**kw)
        self.current_state = {}

        status_topic: str = self.get_config().get("status_topic")  # pyright: ignore[reportAttributeAccessIssue]
        assert status_topic, "status_topic not found in configuration"

        # Subscribe to status updates
        register = topic(status_topic, payload_converter=decode_json)
        register(self.update_status)

        # Dump curent state on USR1 signal
        signal(SIGUSR1, self.dump_state)

    def update_status(self, _userdata, msg) -> None:
        """Track the global state,
        and invoke handler methods defined by subclasses
        with the message payload.
        """
        if self.on_status_update(msg.topic, msg.payload):
            self.invoke_handlers(msg.topic, msg.payload)

    def on_status_update(self, topic: str, payload: Any) -> str | None:
        """Keep the global state in-memory.
        Returns a path to the updated attribute in `self.current_state`
        when the state has changed, or `None` otherwise.
        """
        # Update only if the value has changed
        if self.current_state.get(topic) != payload:
            self.current_state[topic] = payload
            self.log.log(self.update_log_level, "Updated: %s = %s", topic, payload)
            return topic

    def invoke_handlers(self, topic: str, payload: Any) -> None:
        "Run through conditions and invoke appropriate handlers"
        for expr, method in self.conditions.items():
            if topic in expr.keys and expr.keys <= self.current_state.keys():
                method(self)

    def publish(
        self,
        topic: str,
        payload=None,
        qos: int = 0,
        retain: bool = False,
        log_level: int = logging.NOTSET,
    ) -> MQTTMessageInfo | None:
        "Avoid redundant updates"
        old_state = self.current_state.get(topic)
        if old_state is not None:
            if old_state == payload:
                return

            cast = type(old_state)
            try:
                if cast(payload) == old_state:
                    return
            except Exception:
                pass
        return super().publish(topic, payload, qos, retain, log_level)  # pyright: ignore[reportAttributeAccessIssue]

    def dump_state(self, _signal, _frame):
        "Print status information"
        print("Current state: " + pformat(self.current_state))


def conditional(expression: str):
    """Decorated a status handler method which is invoked
    with the value of the expression
    whenever the expression depends on an updated topic.
    For the expression grammar, see the docstrings in `expr.py`.
    """

    predicate = StateAwareMixin.expr_parser.parse(expression)

    def wrapper(method):
        id = method.func.__name__ if type(method) is partial else method.__name__

        @wraps(method)
        def wrapped(self):
            last_state = predicate.last_state
            condition = predicate(self.current_state)
            if condition != last_state:
                self.log.info("Invoking: %s(%s)", id, condition)
                method(self, condition)

        StateAwareMixin.conditions[predicate] = wrapped
        return method

    return wrapper


def when(expression: str):
    """Decorate a status handler method which is invoked
    when the expression depends on an updated topic
    and when it evaluates to `True`.
    For the expression grammar, see the docstrings in `expr.py`.
    """

    predicate = StateAwareMixin.expr_parser.parse(expression)

    def wrapper(method):
        id = method.func.__name__ if type(method) is partial else method.__name__

        @wraps(method)
        def wrapped(self):
            last_state = predicate.last_state
            condition = predicate(self.current_state)
            if condition != last_state:
                if condition:
                    self.log.info("Invoking: %s", id)
                    method(self)
                else:
                    self.log.debug("Skipping: %s", id)

        StateAwareMixin.conditions[predicate] = wrapped
        return method

    return wrapper
