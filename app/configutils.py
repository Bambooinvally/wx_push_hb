import datetime
import app
from app.models import *

BOARD = "board"
ACCESS_TOKEN = "access_token"


def getconfig(name, default):
    c = get_or_none(Config, name=name)
    if c is None:
        return default
    else:
        return c.value


def getconfigattached(name, default):
    c = get_or_none(Config, name=name)
    if c is None:
        return default
    else:
        return c.valueAttached


def setconfig(name, value):
    c = get_or_none(Config, name=name)
    if c is None:
        Config.objects.create(name=name, value=value)
    else:
        c.value = value
        c.save()


def setconfiga(name, value, valueAttached):
    c = get_or_none(Config, name=name)
    if c is None:
        Config.objects.create(name=name, value=value, valueAttached=valueAttached)
    else:
        c.value = value
        c.valueAttached=valueAttached
        c.save()


def remove_html_RL(html):
    html = html.replace('<br>', '\n')
    html = html.replace('<br/>', '\n')
    return html


def to_html_RL(text):
    html = text.replace('\n', '<br/>')
    return html


def board_as_html():
    boardconf = Config.objects.get(name=BOARD)
    if boardconf is not None \
            and boardconf.textValue is not None \
            and len(boardconf.textValue):
        return to_html_RL(boardconf.textValue)
    else:
        return to_html_RL(app.default_board)


def board_as_text():
    boardconf = Config.objects.get(name=BOARD)
    if boardconf is not None \
            and boardconf.textValue is not None \
            and len(boardconf.textValue):
        return remove_html_RL(boardconf.textValue)
    else:
        return remove_html_RL(app.default_board)


def board(value):
    v = remove_html_RL(value)
    boardconf, iscreate = Config.objects.get_or_create(name=BOARD, defaults={'textValue': v})
    if not iscreate:
        boardconf.textValue = v
        boardconf.save()
    return v
