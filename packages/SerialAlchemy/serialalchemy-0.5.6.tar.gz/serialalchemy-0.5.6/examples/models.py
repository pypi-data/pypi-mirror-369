import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property

from serialalchemy import *

from custom_types import *

from typing import NewType


class ValidationError(Exception):
    pass


Base = declarative_base()
session_factory = sa.orm.sessionmaker()
Session = sa.orm.scoped_session(session_factory)
Base.query = Session.query_property()


users_groups = sa.Table('users_groups', Base.metadata,
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id',
            onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('group_id', sa.Integer, sa.ForeignKey('groups.id',
            onupdate='cascade', ondelete='cascade'), primary_key=True)
    )

class User(Base, Serializable):
    __tablename__ = 'users'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username: str = sa.Column(sa.UnicodeText, nullable=False)
    password: str = sa.Column(sa.UnicodeText)

    firstname = sa.Column(sa.Unicode(100))
    lastname = sa.Column(sa.Unicode(100))

    birthdate = sa.Column(sa.Date)
    created = sa.Column(sa.DateTime)
    alarm = sa.Column(sa.Time)

    pickled = sa.Column(sa.PickleType)
    number = sa.Column(sa.Numeric)
    flt = sa.Column(sa.Float)
    something = sa.Column(sa.Boolean)

    always_excluded = sa.Column(sa.UnicodeText,
            info={'serializable': False})

    selections = sa.Column(sa.Enum('one', 'two', 'three'))
    interval = sa.Column(sa.Interval)

    guid = sa.Column(GUID)

    smalltext = sa.Column(sa.Unicode(5))

    data = sa.Column(sa.JSON)

    @serializable_property
    def two(self):
        print('two executed')
        return 1 + 1

    @hybrid_property
    def test(self):
        return self.number

    @validates('smalltext')
    def valid_name(self, key, value):
        if len(value) > 5:
            raise ValidationError(key, 'Invalid value size')
        return value


class Profile(Base, Serializable):
    __tablename__ = 'profiles'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
        onupdate='cascade', ondelete='cascade'))

    somefield = sa.Column(sa.UnicodeText)

    user = relationship('User', backref=backref('profile',
        uselist=False))


class Address(Base, Serializable):
    __tablename__ = 'addresses'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
        onupdate='cascade', ondelete='cascade'))

    address = sa.Column(sa.UnicodeText)

    user = relationship('User', backref='addresses')


class Group(Base, Serializable):
    __tablename__ = 'groups'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column(sa.UnicodeText)

    users = relationship('User', secondary=users_groups, backref='groups')


class Compkey(Base, Serializable):
    __tablename__ = 'compkeys'

    left_id = sa.Column(sa.Integer, primary_key=True)
    right_id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column(sa.UnicodeText)


class Page(Base, Serializable):
    __tablename__ = 'pages'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('pages.id',
        onupdate='cascade', ondelete='cascade'))

    title = sa.Column(sa.Unicode(100))
    content = sa.Column(sa.UnicodeText)

    children = relationship('Page',
            backref=backref('parent', remote_side=id, uselist=False))



