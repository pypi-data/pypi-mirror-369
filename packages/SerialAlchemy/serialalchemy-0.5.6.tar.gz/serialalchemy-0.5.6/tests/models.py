from typing import List, Optional
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from sqlalchemy import (
    Integer,
    PickleType,
    Text,
    Date,
    DateTime,
    String,
    ForeignKey,
    Numeric,
    Float,
    Boolean,
    LargeBinary,
    Enum,
    Interval,
    Identity,
    Table,
    Column,
    inspect,
    select,
    func
)
from sqlalchemy.orm import (
    aliased, column_property, relationship, validates, DeclarativeBase,
    mapped_column, Mapped,
    sessionmaker, scoped_session,
)


from serialalchemy import (
    Serializable, serializable_property,
    serializable_hybrid
)

class Base(DeclarativeBase):
    pass

session_factory = sessionmaker()
Session = scoped_session(session_factory)
# Base.query = Session.query_property()


users_groups = Table('users_groups', Base.metadata,
        Column('user_id', Integer, ForeignKey('users.id',
            onupdate='cascade', ondelete='cascade'), primary_key=True),
        Column('group_id', Integer, ForeignKey('groups.id',
            onupdate='cascade', ondelete='cascade'), primary_key=True)
    )


class ValidationError(Exception):
    pass


class User(Base, Serializable):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    username: Mapped[Optional[str]] = mapped_column(Text)
    password: Mapped[Optional[str]] = mapped_column(Text)

    firstname: Mapped[Optional[str]] = mapped_column(String(100))
    lastname: Mapped[Optional[str]] = mapped_column(String(100))
    birthdate: Mapped[Optional[date]]

    alarm: Mapped[Optional[time]]
    pickled: Mapped[Optional[bytes]] = mapped_column(PickleType)
    number: Mapped[Optional[Decimal]]
    flt: Mapped[Optional[float]]
    something: Mapped[Optional[bool]]
    blob: Mapped[Optional[bytes]]
    always_excluded: Mapped[Optional[str]] = mapped_column(Text, info={'serializable': False})

    selections: Mapped[Optional[str]] = mapped_column(Enum('one', 'two', 'three'))
    interval: Mapped[Optional[timedelta]]
    smalltext: Mapped[Optional[str]] = mapped_column(String(5))

    created: Mapped[Optional[datetime]] = mapped_column(DateTime(True))

    profile: Mapped["Profile"] = relationship(back_populates="user")
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    groups: Mapped[List["Group"]] = relationship(secondary=users_groups, back_populates="users")


    @serializable_property
    def two(self):
        return 1 + 1

    @property
    def three(self):
        return 3

    @validates('smalltext')
    def valid_len(self, key, value):
        if len(value) > 5:
            raise ValidationError(key, 'Invalid length')
        return value

    @validates('password')
    def pw_len(self, key, value):
        if len(value) < 8:
            raise ValidationError(key, 'Password is too short')
        return value

    @serializable_hybrid
    def four(self):
        return 4


class Profile(Base, Serializable):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id',
                                         onupdate='cascade',
                                         ondelete='cascade'))

    somefield: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship('User', back_populates='profile', uselist=False)


class Address(Base, Serializable):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id',
        onupdate='cascade', ondelete='cascade'))

    address: Mapped[Optional[str]] = mapped_column(Text)
    user: Mapped["User"] = relationship(back_populates="addresses")


User.address_count = column_property(
    select(func.count(Address.id))
    .where(Address.user_id == User.id)
    .scalar_subquery()
    .label('address_count')
)


class Group(Base, Serializable):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped[List["User"]] = relationship(secondary=users_groups, back_populates="groups")



class Compkey(Base, Serializable):
    __tablename__ = 'compkeys'

    left_id: Mapped[int] = mapped_column(primary_key=True)
    right_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(Text)



class Page(Base, Serializable):
    __tablename__ = 'pages'

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    parent_id = mapped_column(ForeignKey('pages.id',
        onupdate='cascade', ondelete='cascade'))

    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)

    children: Mapped[List['Page']] = relationship('Page', back_populates='parent')
    parent: Mapped['Page'] = relationship('Page', back_populates='children',
                          remote_side=[id])

