Changelog
=========

2.0.0 - 2024-07-08
------------------

Added:
~~~~~~
* Support python 3.10

Removed:
~~~~~~~~
* Revert dependency tree generation command (**breaking**)
* Drop support python 2 and 3.4

1.2.0
-----

Added:
~~~~~~
* add migration dependency tree generation command

1.1.0
-----

Added:
~~~~~~
* add down_revision to migration data

Removed:
~~~~~~~~
* reverse migration order to simplify the application

1.0.5
-----

Added:
~~~~~~
* correctly handle multi-phased migration data extraction

1.0.4
-----

Added:
~~~~~~
* online script execution implemented
* `get_migrations_data` API

1.0.3
-----

Added:
~~~~~~
* Added arbitrary script operation
* Strict phases configuration assertions for phased migration decorator
* `get_migration_data` API

1.0.0
-----

Added:
~~~~~~
* Initial public release
