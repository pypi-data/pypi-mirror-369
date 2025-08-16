import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date, time, timedelta
import json

from serialalchemy import Serializable

from models import *


def populate_test_data(session):
    for i in range(5, 45):
        u = User()

        u.firstname = "test"
        u.lastname = "test"

        u.number = 21.3534
        u.flt = 1.3432
        u.created = datetime(2015, 8, 31, 15, 28, 33)

        u.pickled = ['one', 'two']
        u.selections = 'one'
        u.something = False

        u.birthdate = date(2015, 9, 5)
        u.alarm = time(15, 28, 33)
        u.interval = timedelta(days=-10)

        u.username = 'uname'

        u.data = {
                'id': 'fdas',
                'value': 'Lorem ipsum',
                children: [
                    {'id': 'fjdiosjo', 'title': 'jiobjvjifog'},
                    {'id': 'fjsdio', 'title': 'fjnan'},
                    {'id': 'ajdoa', 'title': '3u490j3fj'},
                    ]
                }


        p = Profile()
        p.somefield = 'somevalue'
        u.profile = p

        g1 = Group()
        g1.id = i+1
        g1.name = 'group1'

        g2 = Group()
        g2.id = i + 45
        g2.name = 'group2'

        u.groups[:] = [g1, g2]

        session.add(u)
        session.add_all([g1, g2])

    session.commit()

    p = [
         Page(title='Test Page', content='test'),
         Page(title='Test Page', content='test'),
         Page(title='Test Page', content='test'),
         Page(title='Test Page', content='test'),
         ]

    session.add_all(p)
    session.commit()

    p1 = Page.query.get(1)
    p2 = Page.query.get(2)

    p2.parent = p1
    session.commit()



engine = sa.create_engine('sqlite:///:memory:', echo=False)
Session.configure(bind=engine)

session = Session()

Base.metadata.create_all(engine)

populate_test_data(session)
