from flask import Flask, request, render_template
from flask_mongoengine import MongoEngine
import hashlib

app = Flask(__name__)
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
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    pass_entry = request.form['passwd']
    pass_hash = hashlib.sha256(pass_entry.encode()).hexdigest()
    user = Users.objects(name=request.form['user']).first()
    if user and user['password'] == pass_hash:
        return render_template('menu.html')
    else:
        return render_template('login.html')


@app.route('/menu', methods=['POST'])
def menu():
    choice = request.form['menu']
    print(choice)
    if (choice == 'read'):
        return render_template('read.html')
    elif (choice == 'write'):
        return render_template('write.html')
    elif (choice == 'update'):
        return render_template('update.html')
    else:
        return render_template('error.html', meesage='Invalid choice')


@app.route('/read', methods=['POST'])
def read():
    entry = credentials.objects(
        user='admin', app_name=request.form['app']).first()
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
    entry = credentials.objects(user='admin', app_name=request.form['app']).first()
    if entry:
        entry.update(user='admin', app_name=request.form['app'], 
                    login=request.form['username'], password=request.form['password'])
    else:
        entry = credentials(user='admin', app_name=request.form['app'], 
                    login=request.form['username'], password=request.form['password'])
        entry.save()

    result = {}
    result['application'] = request.form['app']
    result['username'] = request.form['username']
    result['password'] = request.form['password']
    return render_template('success.html', result=result)


@app.route('/update', methods=['POST'])
def update():
    old_pass = request.form['old']
    new_pass = request.form['new']
    confirm_pass = request.form['confirm']
    old_hash = hashlib.sha256(old_pass.encode()).hexdigest()
    new_hash = hashlib.sha256(new_pass.encode()).hexdigest()

    user = Users.objects(name='admin').first()
    if user and user['password'] == old_hash:
        if new_pass == confirm_pass:
            user.update(password=new_hash)
            result = {}
            result['username'] = 'admin'
            result['password'] = new_pass
            return render_template('success.html', result=result)
        else:
            return render_template('error.html', message='Passwords do not match')
    else:
        return render_template('error.html', message='Invalid old password')


@app.route('/startover', methods=['POST'])
def startover():
    return render_template('menu.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
