from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://off-your-shoulde:baseball1@localhost:8889/off-your-shoulder'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Entry(db.Model): #NEW ENTRY FOR DATABASE

    id = db.Column(db.Integer, primary_key=True) #Creates ID for each entry     
    title = db.Column(db.String(180)) #Adds vairable "title" to Entry
    body = db.Column(db.String(1000)) #adds variable "body" to Entry
    

    def __init__(self, title, body ):
        self.title = title #stores variables in SELF for each entry
        self.body = body

    def is_valid(self):
       
        if self.title and self.body:  #Makes sure each SELF is valid
            return True
        else:
            return False    
        


@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    
    if request.method == 'POST': #Once the user hits submit on new entry....
        new_entry_title = request.form['title'] #gets the title variables from HTML
        new_entry_body = request.form['body'] #gets the body variable from HTML
        new_entry = Entry(new_entry_title, new_entry_body) #calls Entry class and adds to database

        if new_entry.is_valid(): 
            db.session.add(new_entry) #if the SELF is valid, it adds to database
            db.session.commit()

            
            url = "/blog?id=" + str(new_entry.id) #creates a link to just the new ID that was added
            return redirect(url)
        else: #else if the entry isn't Valid
            flash("Please check your entry for errors. Both a title and a body are required.")
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_entry_title=new_entry_title,
                new_entry_body=new_entry_body)

    else: # GET request
            return render_template('new_post.html', title="Create new blog entry")

if __name__ == '__main__':
    app.run()
