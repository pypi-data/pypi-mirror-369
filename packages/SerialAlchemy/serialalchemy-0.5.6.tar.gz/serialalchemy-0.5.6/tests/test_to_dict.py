'''Tests for to_dict() method'''

import pprint
from .models import *
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy import select

def compare_dicts(expected, test):
    '''recursive dict comparison'''

    keys = set(expected.keys()) | set(test.keys())

    for key in keys:
        if isinstance(expected[key], dict) and isinstance(test[key], dict):
            compare_dicts(expected[key], test[key])
        else:
            assert test[key] == expected[key]



def test_plain(session):
    '''Serialize single object, no relationships'''
    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(relationships=False)

    expected = {
            'id': 1,
            'firstname': 'test',
            'lastname': 'test',
            'number': 21.3534,
            'flt': 1.3432,
            'created': '2015-08-31 15:28:33',
            'pickled': ['one', 'two'],
            'selections': 'one',
            'something': False,
            'birthdate': '2015-09-05',
            'alarm': '15:28:33',
            'interval': -864000.0,
            'username': 'uname',
            'two': 2,
            'password': None,
            'smalltext': None,
            'four': 4,
            'blob': b'\x01\x02\x03\x04',
            'address_count': 2,
            }

    compare_dicts(expected, data)

def test_fields(session):
    '''Serialize single object, no relationships, limiting fields'''
    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(fields=('firstname', 'lastname'), relationships=False)

    expected = {
            'firstname': 'test',
            'lastname': 'test',
            }

    compare_dicts(expected, data)

def test_fields2(session):
    '''Serialize single object, no relationships, limiting fields, this time
    with properties and non-existent fields'''
    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(fields=('firstname', 'lastname', 'two', 'nonexistent'), relationships=False)

    expected = {
            'firstname': 'test',
            'lastname': 'test',
            'two': 2
            }

    compare_dicts(expected, data)

def test_fields3(session):
    '''Serialize single object, no relationships, limiting fields, this time
    ignoring properties that are not decorated with serializable_property'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(fields=('firstname', 'lastname', 'two', 'three'), relationships=False)

    expected = {
            'firstname': 'test',
            'lastname': 'test',
            'two': 2
            }

    compare_dicts(expected, data)


def test_fields4(session):
    '''Serialize single object, with relationships, limiting fields, and
        related objects have a serializable_property'''

    stmt = (select(Profile)
            .options(joinedload(Profile.user)
                     .load_only(User.id))
            .where(Profile.id == 1))

    profile = session.scalars(
        stmt
    ).one()

    data = profile.to_dict(fields=('id', 'user'))

    expected = {
            'id': 1,
            'user': {
                'id': 1,
                'two': 2,
                'four': 4,
                },
            }

    compare_dicts(expected, data)


def test_exclude_fields(session):
    '''Serialize single object no relationship, excluding fields'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(fields=['~firstname'], relationships=False)

    assert 'firstname' not in data



def test_relationships(session):
    '''Serialize object with related objects. MTM relationships return PK only
    (default setup)'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict()

    expected = {
            'id': 1,
            'firstname': 'test',
            'lastname': 'test',
            'number': 21.3534,
            'flt': 1.3432,
            'created': '2015-08-31 15:28:33',
            'pickled': ['one', 'two'],
            'selections': 'one',
            'something': False,
            'birthdate': '2015-09-05',
            'alarm': '15:28:33',
            'interval': -864000.0,
            'username': 'uname',
            'password': None,
            'smalltext': None,
            'two': 2,
            'profile': {
                'id': 1,
                'user_id': 1,
                'somefield': 'somevalue'
                },
            'groups': [6, 50],
            'four': 4,
            'blob': b'\x01\x02\x03\x04',
            'addresses': [
                {'id': 1, 'user_id': 1, 'address': 'yay'},
                {'id': 2, 'user_id': 1, 'address': 'yay 2'},
            ],
            'address_count': 2,
            }


    compare_dicts(expected, data)


def test_relationships_fullmtm(session):
    '''Serialize object with related objects. Full MTM objects returned.'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(mtm_pkonly=False)

    expected = {
            'id': 1,
            'firstname': 'test',
            'lastname': 'test',
            'number': 21.3534,
            'flt': 1.3432,
            'created': '2015-08-31 15:28:33',
            'pickled': ['one', 'two'],
            'selections': 'one',
            'something': False,
            'birthdate': '2015-09-05',
            'alarm': '15:28:33',
            'interval': -864000.0,
            'username': 'uname',
            'password': None,
            'two': 2,
            'smalltext': None,
            'four': 4,
            'blob': b'\x01\x02\x03\x04',
            'profile': {
                'id': 1,
                'user_id': 1,
                'somefield': 'somevalue'
                },
            'groups': [
                {'id': 6, 'name': 'group1'},
                {'id': 50, 'name': 'group2'},
                ],
            'addresses': [
                {'id': 1, 'user_id': 1, 'address': 'yay'},
                {'id': 2, 'user_id': 1, 'address': 'yay 2'},
            ],
            'address_count': 2,
            }

    compare_dicts(expected, data)


def test_relationships_loadonly(session):
    '''Serialize object with related objects, limiting field output on parent
        and child.'''


    stmt = (
        select(User)
        .options(joinedload(User.profile)
                 .load_only(Profile.somefield))
        .where(User.id == 3)
    )
    print(stmt)
    user = session.scalars(
        stmt
    ).one()

    data = user.to_dict(['firstname', 'profile'])


    expected = {
            'firstname': 'test',
            'profile': {
                'id': 3,
                'somefield': 'somevalue',
                },
            }

    compare_dicts(expected, data)


def test_self_ref(session):
    '''Serialize object of a model with a self-reference'''

    page = session.scalars(
        select(Page).where(Page.id == 1)
    ).one()

    data = page.to_dict()

    # pprint.pprint(data)

    expected = {
            'id': 1,
            'parent_id': None,
            'title': 'Test Page',
            'content': 'test',
            'children': [
                {
                    'title': 'Test Page',
                    'content': 'test',
                    'parent_id': 1,
                    'id': 2,
                },
                ]
            }

    compare_dicts(expected, data)


def test_self_ref_empty(session):
    '''Serialize object of a model with a self-reference'''

    page = session.scalars(
        select(Page).where(Page.id == 3)
    ).one()

    data = page.to_dict()

    expected = {
            'id': 3,
            'parent_id': None,
            'title': 'Test Page',
            'content': 'test',
            }

    compare_dicts(expected, data)

def test_hybrid_property(session):
    '''Test serialization of hybrid attribute'''

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    data = user.to_dict(fields=('firstname', 'lastname', 'four'), relationships=False)

    expected = {
            'firstname': 'test',
            'lastname': 'test',
            'four': 4,
            }


    compare_dicts(expected, data)

