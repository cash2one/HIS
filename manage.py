#!/usr/bin/env python
import os
from app import create_app, db
from app.models import Patient, Doctor, Admin, Registrar
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def fullfillstring(string):
    if not string:
        return "hardtofindstring"
    return string

app.jinja_env.filters['fullfillstring']=fullfillstring

def make_shell_context():
    return dict(app=app, db=db, Patient=Patient, Doctor=Doctor, Admin=Admin, Registrar=Registrar)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()