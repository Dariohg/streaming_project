import os
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db_path = current_app.config['DATABASE']

        if not os.path.exists(db_path):
            db = get_db()

            with app.open_resource('database/schema.sql') as f:
                db.executescript(f.read().decode('utf8'))

            current_app.logger.info("Base de datos inicializada.")

        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa la base de datos."""
    db = get_db()

    with current_app.open_resource('database/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    click.echo('Base de datos inicializada.')