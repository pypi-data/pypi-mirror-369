SerialAlchemy might be sticking around
--------------------------------------

Oh hi. Do you actually use SerialAlchemy? Well, I have some news.

With the release of SQLAlchemy 2.0, it's possible to easily integrate 
dataclasses with models... which means it's easy to change models to dicts...
WHICH MEANS it's possible to serialize a model into JSON without the use of 
SerialAlchemy.

However...

After recently trying to make some utilities to work with 
dataclass-based Models, I realized I was basically recreating this 
library. Since this library still works, what's the point of redoing it?

--

SerialAlchemy adds serialization to [SQLAlchemy](https://sqlalchemy.org) ORM
objects via a mixin class. It is tightly coupled with SQLAlchemy, because it's
the best thing ever invented.


About
=====

Here's the elevator pitch: are you defining your models with SQLAlchemy and
again with Pydantic? Do you have trouble keeping clear which models are
SQLAlchemy models and which models are Pydantic models? Do you have a way to
keep your models' models in sync with DB changes?

THAT'S TOO MANY MODELS for my simple brain and my lazy disposition, in any case.

I made SerialAlchemy mainly because I hate repeating myself.

MIT Licensed
