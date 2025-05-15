from flask.cli import FlaskGroup
from sqlalchemy import text

from project import app, db, User


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    # Drop all tables with CASCADE
    with db.engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(
        username="michael",
        email="michael@mherman.org"
    ))
    db.session.commit()


if __name__ == "__main__":
    cli()
