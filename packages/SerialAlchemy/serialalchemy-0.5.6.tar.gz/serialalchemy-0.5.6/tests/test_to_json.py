'''Tests for the to_json() method.'''

from sqlalchemy import select
from sqlalchemy.orm import joinedload, load_only
from .models import *
import json

def test_to_json_single(session):

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    expected = '''{"user": {"id": 1, "firstname": "test"}}'''

    test = User.to_json(user, fields=('id', 'firstname'),
            relationships=False)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_to_json_multiple(session):

    users = session.scalars(
        select(User).where(User.id.in_((1, 2)))
    )

    expected = '''{"users": [{"id": 1, "firstname": "test"},{"id": 2, "firstname": "test"}]}'''

    test = User.to_json(users, fields=('id', 'firstname'),
            relationships=False)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_to_json_empty(session):

    users = session.scalars(
        select(User).where(User.id.in_((345432, 3412)))
    )
    expected = '''{"users": []}'''

    test = User.to_json(users, fields=('id', 'firstname'),
            relationships=False)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


def test_to_json_none(session):

    user = session.scalars(
        select(User).where(User.id == 52354)
    ).first()

    expected = '''{"user": null}'''

    test = User.to_json(user, fields=('id', 'firstname'),
            relationships=False)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

def test_to_json_blob(session):

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    expected = '''{"user": {"id": 1, "blob": "AQIDBA=="}}'''

    test = User.to_json(user, fields=('id', 'blob'),
            relationships=False)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)
