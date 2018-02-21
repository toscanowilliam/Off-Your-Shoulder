from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://off-your-shoulde:baseball1@localhost:3306/off-your-shoulder'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Entry(db.Model):  # NEW ENTRY FOR DATABASE

    id = db.Column(db.Integer, primary_key=True)  # Creates ID for each entry
    title = db.Column(db.String(180))  # Adds variable "title" to entry
    body = db.Column(db.String(1000))  # adds date
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    comment_id = db.relationship('Comment', backref='comment')

    def __init__(self, title, body, owner):
        self.title = title  # stores variables in SELF for each entry
        self.body = body
        self.owner = owner

    def is_valid(self):

        if self.title and self.body:  # Makes sure each SELF is valid
            return True
        else:
            return False


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    entry = db.relationship('Entry', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Creates ID for each entry
    body = db.Column(db.String(1000))  # adds date
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # entry = db.relationship('Entry', backref='owner')
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False)

    def __init__(self, body, owner):

        self.body = body
        self.owner = owner

    def is_valid(self):

        if self.body:  # Makes sure each SELF is valid
            return True
        else:
            return False


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title='Users', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def display_entries():
    user_id = request.args.get('user')
    entry_id = request.args.get('id')
    if (entry_id):  # if the user clicks on a blog link, it takes them to that entry
        entry = Entry.query.get(entry_id)  # this gets the specific ID for what the user clicked on
        return render_template('single_entry.html', title="Blog Entry", entry=entry)

    if (user_id):
        user_id = int(user_id)
        user = User.query.get(user_id)
        all_entries = user.entry
        return render_template('single_user.html', title="User", all_entries=all_entries, user=user)
    all_entries = Entry.query.order_by(Entry.created.desc()).all()

    return render_template('all_entries.html', title="All Entries", all_entries=all_entries)


@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':  # Once the user hits submit on new entry....
        new_entry_title = request.form['title']  # gets the title and body variables from HTML
        new_entry_body = request.form['body']
        new_entry = Entry(new_entry_title, new_entry_body, owner)  # calls Entry class and adds to database

        if new_entry.is_valid():
            db.session.add(new_entry)  # if the SELF is valid, it adds to database
            db.session.commit()
            url = "/entry?id=" + str(new_entry.id)  # creates a link to just the new ID that was added
            return redirect(url)
        else:
            flash("Please check your entry for errors. Both a title and a body are required.")
            return render_template('new_entry_form.html',
                                   title="Create new blog entry",
                                   new_entry_title=new_entry_title,
                                   new_entry_body=new_entry_body)

    else:  # GET request
        return render_template('new_entry_form.html', title="Create new blog entry")


def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email).first()

        if users and users.password == password:
            session['email'] = users.email
            flash("Logged in")
            print("*" * 50)
            return redirect(url_for(".index"))

        else:
            flash("Incorrect email or password")
            return redirect('/')


@app.route("/logout", methods=['POST'])
def logout():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        session['email'] = owner.email
        del session['email']
        return redirect("/home")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/")
    else:
        return render_template('register.html')


@app.route("/comment", methods=['POST'])
def comment():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':  # Once the user hits submit on new entry....
        new_entry_body = request.form['body']
        new_entry = Comment(new_entry_body, owner)

    if new_entry.is_valid():
        db.session.add(new_entry)  # if the SELF is valid, it adds to database
        db.session.commit()
        # creates a link to just the new ID that was added
        url = "/entry?id=" + str(new_entry.id)
        return redirect(url)


@app.before_request
def require_login():
    endpoints_without_login = ['login', 'register', 'logout', 'display_blog_entries']
    if not ('email' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")


if __name__ == '__main__':
    app.run()
