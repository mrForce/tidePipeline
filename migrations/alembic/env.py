from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine
from logging.config import fileConfig
import os
import sys
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
print('cwd: ' + os.getcwd())
from DB import BaseTable
target_metadata = BaseTable.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL

    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    print('running migration offline')
    project_location = os.getenv('PIPELINE_PROJECT', '')
    if len(project_location) < 1:
        print('Did someone forget to set PIPELINE_PROJECT?')
        sys.exit()
    url = 'sqlite:///' + os.path.join(project_location, 'database.db')
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    print('running migration online')
    project_location = os.getenv('PIPELINE_PROJECT', '')
    if len(project_location) < 1:
        print('Did someone forget to set PIPELINE_PROJECT?')
        sys.exit()
    print('project location')
    print(project_location)
    url = 'sqlite:///' + os.path.join(project_location, 'database.db')

    connectable = engine_from_config(
        {'sqlalchemy.url': url},
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
             render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
