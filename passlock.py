from flask import Flask, request, render_template, session
from flask_mongoengine import MongoEngine
import hashlib

app = Flask(__name__)
app.secret_key = '60308ba9bddf0845786b0824'
app.config['MONGODB_SETTINGS'] = {
    'db': 'passlock',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


class Users(db.Document):
    name = db.StringField()
    password = db.StringField()


class credentials(db.Document):
    user = db.StringField()
    app_name = db.StringField()
    login = db.StringField()
    password = db.StringField()


@app.route('/')
def home():
    return render_template('login.html', message='Login to proceed')


@app.route('/login', methods=['POST'])
def login():
    pass_entry = request.form['passwd']
    pass_hash = hashlib.sha256(pass_entry.encode()).hexdigest()
    user = Users.objects(name=request.form['user']).first()
    if user and user['password'] == pass_hash:
        session['user'] = request.form['user']
        return render_template('menu.html', username=session['user'])
    else:
        return render_template('login.html', message='Invalid username or password')


@app.route('/menu', methods=['POST'])
def menu():
    if not 'user' in session:
        return render_template('login.html', message='Login to proceed')

    choice = request.form['menu']
    if choice == 'read':
        return render_template('read.html')
    elif choice == 'write':
        return render_template('write.html')
    elif choice == 'update':
        return render_template('update.html')
    elif choice == 'logout':
        session.pop('user', None)
        return render_template('login.html')
    else:
        return render_template('error.html', meesage='Invalid choice')


@app.route('/read', methods=['POST'])
def read():
    if not 'user' in session:
        return render_template('login.html', message='Login to proceed')

    entry = credentials.objects(
        user=session['user'], app_name=request.form['app']).first()
    if entry:
        result = {}
        result['application'] = entry.app_name
        result['username'] = entry.login
        result['password'] = entry.password
        return render_template('success.html', result=result)
    else:
        return render_template('error.html', message='Application does not exist')


@app.route('/write', methods=['POST'])
def write():
    if not 'user' in session:
        return render_template('login.html', message='Login to proceed')

    entry = credentials.objects(
        user=session['user'], app_name=request.form['app']).first()
    if entry:
        entry.update(user=session['user'], app_name=request.form['app'],
                     login=request.form['username'], password=request.form['password'])
    else:
        entry = credentials(user=session['user'], app_name=request.form['app'],
                            login=request.form['username'], password=request.form['password'])
        entry.save()
    return render_template('noresult.html')


@app.route('/update', methods=['POST'])
def update():

    if not 'user' in session:
        return render_template('login.html', message='Login to proceed')

    old_pass = request.form['old']
    new_pass = request.form['new']
    confirm_pass = request.form['confirm']
    old_hash = hashlib.sha256(old_pass.encode()).hexdigest()
    new_hash = hashlib.sha256(new_pass.encode()).hexdigest()

    user = Users.objects(name=session['user']).first()
    if user and user['password'] == old_hash:
        if new_pass == confirm_pass:
            user.update(password=new_hash)
            return render_template('noresult.html')
        else:
            return render_template('error.html', message='Passwords do not match')
    else:
        return render_template('error.html', message='Invalid old password')


@app.route('/startover', methods=['POST'])
def startover():
    return render_template('menu.html', username=session['user'])


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
