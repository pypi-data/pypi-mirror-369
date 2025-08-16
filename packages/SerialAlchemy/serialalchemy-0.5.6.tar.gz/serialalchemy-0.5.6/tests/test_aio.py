'''Tests for the async_factory() method.'''

from sqlalchemy import select
from sqlalchemy.orm import load_only
from .models import *
import json

import pytest

@pytest.mark.asyncio
async def test_async_factory_single(session):

    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    expected = b'''{"user": {"id": 1, "firstname": "test"}}'''

    generator = await User.async_factory(user, fields=('id', 'firstname'),
            relationships=False)

    items = []
    async for j in generator():
        items.append(j)

    test = b''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_multiple(session):

    # users = User.query.filter(User.id.in_((1, 2)))
    users = session.scalars(
        select(User)
        .options(load_only(User.id, User.firstname))
        .where(User.id.in_((1, 2)))
    )

    expected = b'''{"users": [{"id": 1, "firstname": "test"},{"id": 2, "firstname": "test"}]}'''

    generator = await User.async_factory(users, fields=('id', 'firstname'),
            relationships=False)

    items = []
    async for j in generator():
        items.append(j)

    test = b''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_empty(session):

    # users = User.query.filter(User.id.in_((345432, 3412)))
    users = session.scalars(
        select(User).where(User.id.in_((345432, 3412)))
    )

    expected = b'''{"users": []}'''

    generator = await User.async_factory(users, fields=('id', 'firstname'),
            relationships=False)

    items = []
    async for j in generator():
        items.append(j)

    test = b''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_none(session):

    # user = User.query.\
    #     filter(User.id == 52354).\
    #     first()
    user = session.scalars(
        select(User).where(User.id == 52354)
    ).first()

    expected = b'''{"user": null}'''

    generator = await User.async_factory(user, fields=('id', 'firstname'),
            relationships=False)

    items = []
    async for j in generator():
        items.append(j)

    test = b''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)


@pytest.mark.asyncio
async def test_async_factory_single_str(session):

    # user = User.query.\
    #     filter(User.id == 1).\
    #     one()
    user = session.scalars(
        select(User).where(User.id == 1)
    ).one()

    expected = '''{"user": {"id": 1, "firstname": "test"}}'''

    generator = await User.async_factory(user, fields=('id', 'firstname'),
            relationships=False, encoding=False)

    items = []
    async for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_multiple_str(session):

    # users = User.query.filter(User.id.in_((1, 2)))
    users = session.scalars(
        select(User).where(User.id.in_((1, 2)))
    )

    expected = '''{"users": [{"id": 1, "firstname": "test"},{"id": 2, "firstname": "test"}]}'''

    generator = await User.async_factory(users, fields=('id', 'firstname'),
            relationships=False, encoding=False)

    items = []
    async for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_empty_str(session):

    # users = User.query.filter(User.id.in_((345432, 3412)))
    users = session.scalars(
        select(User).where(User.id.in_((345432, 3412)))
    )

    expected = '''{"users": []}'''

    generator = await User.async_factory(users, fields=('id', 'firstname'),
            relationships=False, encoding=False)

    items = []
    async for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

@pytest.mark.asyncio
async def test_async_factory_none_str(session):

    # user = User.query.\
    #     filter(User.id == 52354).\
    #     first()
    user = session.scalars(
        select(User).where(User.id == 52354)
    ).first()

    expected = '''{"user": null}'''

    generator = await User.async_factory(user, fields=('id', 'firstname'),
            relationships=False, encoding=False)

    items = []
    async for j in generator():
        items.append(j)

    test = ''.join(items)

    de = json.loads(expected)
    dt = json.loads(test)

    assert json.dumps(de) == json.dumps(dt)

