from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

import os

app.config.from_object("config.BaseConfig")


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()