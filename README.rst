alembic-offline
===============

.. image:: https://api.travis-ci.org/paylogic/alembic-offline.png
   :target: https://travis-ci.org/paylogic/alembic-offline

.. image:: https://pypip.in/v/alembic-offline/badge.png
   :target: https://crate.io/packages/alembic-offline/

.. image:: https://coveralls.io/repos/paylogic/alembic-offline/badge.svg?branch=master
    :target: https://coveralls.io/r/paylogic/alembic-offline?branch=master

.. image:: https://readthedocs.org/projects/alembic-offline/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/alembic-offline/

alembic-offline is an extension for alemic to enrich offline functionality of the migrations

.. contents::


Usage
-----

In your version file:

.. code-block:: python

    from sqlalchemy import INTEGER, VARCHAR, NVARCHAR, TIMESTAMP, Column, func
    from alembic import op

    from alembic_offline import phased, execute_script

    from tests.migrations.scripts import script

    revision = '1'
    down_revision = None


    @phased
    def upgrade():

        op.create_table(
            'account',
            Column('id', INTEGER, primary_key=True),
            Column('name', VARCHAR(50), nullable=False),
            Column('description', NVARCHAR(200)),
            Column('timestamp', TIMESTAMP, server_default=func.now())
        )
        yield
        op.execute("update account set name='some'")
        yield
        execute_script(script.__file__)


    def downgrade():
        pass

Will give the sql output (for sqlite):

.. code-block:: sql

    -- Running upgrade  -> 1

    -- PHASE::0::;

    CREATE TABLE account (
        id INTEGER NOT NULL,{space}
        name VARCHAR(50) NOT NULL,{space}
        description NVARCHAR(200),{space}
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,{space}
        PRIMARY KEY (id)
    );

    -- PHASE::1::;

    update account set name='some';

    -- PHASE::2::;

    -- SCRIPT::/home/vagrant/workspace/alembic-offline/tests/migrations/scripts/script.pyc::;

    INSERT INTO alembic_version (version_num) VALUES ('1');


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/alembic-offline>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

Please refer to the `license file <https://github.com/paylogic/alembic-offline/blob/master/LICENSE.txt>`_


© 2015 Anatoly Bubenkov, Paylogic International and others.
