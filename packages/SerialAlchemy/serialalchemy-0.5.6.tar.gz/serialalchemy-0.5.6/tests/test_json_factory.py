'''Tests for the json_factory() method.'''

from sqlalchemy import select
from .models import *
import json

def test_json_factory_single(session):

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    expected = '''{"user": {"id": 1, "firstname": "test"}}'''

    generator = User.json_factory(user, fields=('id', 'firstname'),
            relationships=False)

    items = []
    for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_json_factory_multiple(session):

    users = session.scalars(
        select(User).where(User.id.in_((1, 2)))
    )

    expected = '''{"users": [{"id": 1, "firstname": "test"},{"id": 2, "firstname": "test"}]}'''

    generator = User.json_factory(users, fields=('id', 'firstname'),
            relationships=False)

    items = []
    for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_json_factory_empty(session):

    users = session.scalars(
        select(User).where(User.id.in_((345432, 3412)))
    )

    expected = '''{"users": []}'''

    generator = User.json_factory(users, fields=('id', 'firstname'),
            relationships=False)

    items = []
    for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_json_factory_none(session):

    user = session.scalars(
        select(User).where(User.id == 23213412)
    ).first()

    expected = '''{"user": null}'''

    generator = User.json_factory(user, fields=('id', 'firstname'),
            relationships=False)

    items = []
    for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

