import gettext
import locale
import os
from collections import namedtuple

__all__ = (
    "_",
    "ALL_ROOMS",
    "CONFIRMATIONS",
    "DEFAULT_ROOM_NAMES",
    "ROOMS",
    "get_translations",
    "ngettext",
    "room_with_article",
    "room_with_preposition",
)


def get_translations(path: str, domain: str = "messages"):
    "Install translations"
    language, encoding = locale.getlocale()
    assert type(language) is str, "Unsupported locale: %s" % locale.getlocale()
    locale.setlocale(locale.LC_ALL, (language, encoding))
    translation = gettext.translation(
        domain,
        localedir=os.path.join(os.path.dirname(path), "locale"),
        languages=[language],
        fallback=True,
    )
    return translation.gettext, translation.ngettext


_, ngettext = get_translations(__file__, "snips_skill")

RoomName = namedtuple("RoomName", "with_article, with_preposition")

CONFIRMATIONS = (
    _("done"),
    _("here you are"),
    _("OK"),
    _("yes"),
    _("finished"),
    _("alright"),
    _("at your service"),
)

DEFAULT_ROOM_NAMES = (
    _("here"),
    _("this room"),
)

ALL_ROOMS = (
    _("all"),
    _("everywhere"),
    _("everything"),
)

ROOMS = {
    # Map translated room names to room names with articles and prepositions
    # for languages that use genders for room names, e.g. German
    _("bathroom").lower(): RoomName(_("the bathroom"), _("in the bathroom")),
    _("bedroom").lower(): RoomName(_("the bedroom"), _("in the bedroom")),
    _("dining room").lower(): RoomName(_("the dining room"), _("in the dining room")),
    _("livingroom").lower(): RoomName(_("the livingroom"), _("in the livingroom")),
    _("kid's room").lower(): RoomName(_("the kid's room"), _("in the kid's room")),
    _("kitchen").lower(): RoomName(_("the kitchen"), _("in the kitchen")),
    _("office").lower(): RoomName(_("the office"), _("in the office")),
    _("hall").lower(): RoomName(_("the hall"), _("in the hall")),
    _("garden").lower(): RoomName(_("the garden"), _("in the garden")),
    _("unknown room").lower(): RoomName(_("an unknown room"), _("in an unknown room")),
}


def room_with_article(room_name: str) -> str:
    "Get the spoken room name with the definite article"
    room = ROOMS.get(room_name.lower())
    return room.with_article if room else _("the {room}").format(room=room_name)


def room_with_preposition(room_name: str) -> str:
    'Get the spoken room name with "in" preposition'
    room = ROOMS.get(room_name.lower())
    return room.with_preposition if room else _("in the {room}").format(room=room_name)
