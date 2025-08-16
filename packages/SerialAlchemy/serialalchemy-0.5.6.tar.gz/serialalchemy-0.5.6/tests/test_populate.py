'''Tests for the populate() method.'''

import pytest
from sqlalchemy import select
from .models import *


def test_populate(session):
    '''Basic field population'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'firstname': 'The',
            'lastname': 'Test',
            }

    user.populate(data)

    assert user.firstname == 'The' and user.lastname == 'Test'
    session.rollback()

def test_populate_with_none(session):
    '''Basic field population with none'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'firstname': None,
            'lastname': 'Test',
            }

    user.populate(data)

    assert user.firstname is None and user.lastname == 'Test'
    session.rollback()


def test_populate_none_fail(session):
    '''Basic field population with none part 2: failing on purpose'''

    user = User()

    data = {
            'id': None,
            'firstname': None,
            'lastname': 'Test',
            }

    with pytest.raises(TypeError):
        user.populate(data, strict_typing=True)

    session.rollback()

def test_populate_none_bypass(session):
    '''Basic field population with none part 2: skipping the whole thing'''

    user = User()

    data = {
            'id': None,
            'firstname': None,
            'lastname': 'Test',
            }

    user.populate(data, strict_typing=False)
    assert user.id is None and user.firstname is None and user.lastname == 'Test'

    session.rollback()

def test_populate_date(session):
    '''Date field population'''

    from datetime import date

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'birthdate': '2016-02-18',
            }

    user.populate(data)

    expected = date(2016, 2, 18)


    assert user.birthdate == expected
    session.rollback()


def test_populate_datetime(session):
    '''Datetime field population'''

    from datetime import datetime

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'created': '2016-02-18 12:34:56'
            }
    user.populate(data)

    expected = datetime(2016, 2, 18, 12, 34, 56)

    assert user.created == expected
    session.rollback()


def test_populate_time(session):
    '''Time field population'''

    from datetime import time

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'alarm': '12:34:56'
            }
    user.populate(data)

    expected = time(12, 34, 56)

    assert user.alarm == expected
    session.rollback()


def test_populate_validation(session):
    '''Validation Helper'''

    data = {
            'username': 'notvalidated',
            'password': 'abcd',
            'smalltext': '12345678',
            }

    u = User()
    errors = u.populate(data, swallow_exceptions=True)

    expected = 2

    assert len(errors) == expected
    session.rollback()


def test_populate_validation2(session):
    '''Validation without exception eating'''

    data = {
            'username': 'notvalidated',
            'password': 'abcd',
            'smalltext': '12345678',
            }

    err = None
    u = User()
    try:
        u.populate(data)
    except ValidationError as ex:
        err = ex

    # For older pythons, we may not know what gets thrown first
    fields = ['password', 'smalltext']

    assert err.args[0] in fields
    session.rollback()


def test_populate_ignore_relationships(session):
    ''' Make sure relationships get ignored '''

    data = {
        'username': 'notvalidated',
        'profile': {
            'somefield': 'OK',
        },
    }

    u = User()
    u.populate(data)

    assert u.profile is None
    session.rollback()


def test_populate_strict(session):
    ''' Test strict typing on populate '''

    data = {
        'username': 'ok',
        'smalltext': 12244,
    }

    u = User()
    field = None

    try:
        u.populate(data, strict_typing=True)
    except TypeError as ex:
        field = ex.args[0]

    assert field == 'smalltext'
    session.rollback()

def test_populate_strict2(session):
    ''' Test strict typing on populate '''

    data = {
        'username': 'ok',
        'smalltext': 12244,
        'password': 'abcd',
    }

    u = User()

    errors = u.populate(data, swallow_exceptions=True, strict_typing=True)
    expected = 2

    assert len(errors) == expected
    session.rollback()

def test_populate_column_prop(session):
    '''Test trying to set column_property columns'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = {
            'firstname': 'The',
            'lastname': 'Test',
            'address_count': 4,
            }

    user.populate(data)

    assert user.firstname == 'The' and user.lastname == 'Test'
    session.rollback()
