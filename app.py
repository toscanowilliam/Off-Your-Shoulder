from flask_sqlalchemy import get_debug_queries,  SQLAlchemy, Pagination
from flask import Flask
from flask_bcrypt import Bcrypt
import os


app = Flask(__name__)
app.config.from_object("config.BaseConfig")
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://djxcjdyhbpeair:e48674efafc51273382efc796e52b5f4b184e0209dfc46aba6014391b2d16db6@ec2-54-221-212-15.compute-1.amazonaws.com:5432/df09qaffi29qac"


bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# app = Flask(__name__)
# app.config['DEBUG'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://ixrcltwqldsymi:cfd9ffdfde2c0b07a794c6bf3abcf8c2c4f2fc7a496cf1d14bb86439a1a66590@ec2-184-73-250-50.compute-1.amazonaws.com:5432/dfnvammku29qit"
# db = SQLAlchemy(app)
# app.secret_key = 'y337kGcys&zP3B'


from main import *


def sql_debug(response):
    queries = list(get_debug_queries())
    query_str = ''
    total_duration = 0.0
    for q in queries:
        total_duration += q.duration
        stmt = str(q.statement % q.parameters).replace('\n', '\n       ')
        query_str += 'Query: {0}\nDuration: {1}ms\n\n'.format(stmt, round(q.duration * 1000, 2))

    print('=' * 80)
    print(' SQL Queries - {0} Queries Executed in {1}ms'.format(len(queries), round(total_duration * 1000, 2)))
    print('=' * 80)
    print(query_str.rstrip('\n'))
    print('=' * 80 + '\n')

    return response


if app.debug:
    app.after_request(sql_debug)



if __name__ == "__main__":
    app.run()