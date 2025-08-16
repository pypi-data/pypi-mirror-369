* 2025-08-15
    Release 0.5.6

    - Add support for column_property
    - I can't remember if I released 0.5.5 or not


* 2024-09-12
    Release 0.5.4

    (hey almost exactly 6 months. how about that)
    - Add more and fix existing documentation
    - Document serializable_hybrid properly
    - Add dict_factory class method (like json_factory but returns regular
      python dicts)

* 2024-03-13
    - Fix to allow none value for columns that are nullable in populate()

* 2023-08-04
    - Fix sqlalchemy requirements

* 2023-07-10
  Release 0.5.0

    - Update to work with SQLAlchemy 2.0
    - Add more tests
    - Add a strict type parameter to populate method
    - Also skip version 0.4 because I forgot to release it


* 2021-08-06
  Release 0.3.6

    - Handle bytes better
    - Convert bytes to base64 string when using json.dumps 

* 2021-01-06
  Release 0.3.5

    - Rework tests to be compatible with SA 1.3 and 1.4

* 2019-10-17
  Release 0.3.4-1

    - Add encoding param to `async_factory`
    - Encoding defaults to utf-8

* 2019-10-16
  Release 0.3.4

    - I forgot to add 0.3.3
    - Also add `async_factory` method that uses async generator
    - Seems to work?

* 2018-01-10
  Release 0.3.2
    
    - Changed code to include serializable_properties on related objects

* 2017-06-12
  Release 0.3.1

    - Fixed schema_info brokenness

* 2017-05-19
  Release 0.3.0

    - Added `schema_info` method

* 2016-12-29
  Release 0.2.2

    - Added `to_json` method and tests
    - Fixed sqlite bug in Compkey example
    - Updated example with always_excluded column

* 2016-09-28
  Release 0.2.1

    - Added a way to exclude columns via info keyword

* 2016-09-15
  Release 0.2.0

    - Added `serializable_property` decorator
    - Fixed issue #2

* 2015-09-30
  Release 0.1.1-1

    - Fixed wheel configuration

* 2015-09-30
  Initial Release 0.1.1
