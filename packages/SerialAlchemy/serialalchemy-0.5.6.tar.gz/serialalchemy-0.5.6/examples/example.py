from models import *
from testdata import *

from sqlalchemy.orm import joinedload

import pprint
import json

user = User.query.get(1)
pprint.pprint(user.to_dict())
'''>>>
{'addresses': [],
 'alarm': '15:28:33',
 'birthdate': '2015-09-05',
 'created': '2015-08-31 15:28:33',
 'firstname': 'test',
 'flt': 1.3432,
 'groups': [6, 50],
 'id': 1,
 'interval': -864000.0,
 'lastname': 'test',
 'number': 21.3534,
 'password': None,
 'pickled': ['one', 'two'],
 'profile': {'id': 1, 'somefield': 'somevalue', 'user_id': 1},
 'selections': 'one',
 'something': False,
 'two': 2,
 'username': 'uname'}
'''

pprint.pprint(user.to_dict(fields=['id', 'firstname', 'lastname']))
'''>>>
{'firstname': 'test', 'id': 1, 'lastname': 'test'}
'''

#SQLAlchemy caches results, so get a different user
user = User.query.\
        options(joinedload(User.profile).load_only('somefield')).\
        get(2)
pprint.pprint(user.to_dict(fields=['id', 'profile']))
'''>>>
{'id': 2, 'profile': {'somefield': 'somevalue'}}
'''

#JSON utility
gen = User.json_factory(user, fields=['id', 'profile'])
for item in gen():
    print(item)
'''>>>
{"user": {"id": 2, "profile": {"somefield": "somevalue"}}}
'''


u = User()
errors = u.populate({
    'smalltext': 'jfiodsajofidiojsfojdsa',
    }, swallow_exceptions=True)

print(errors)
