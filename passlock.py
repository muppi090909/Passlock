from flask import Flask, request, render_template
import hashlib
import json
import os
auth = False
app = Flask(__name__)
vault = {}


def init(storage):
    global vault
    f = open(storage, "r")
    vault = json.loads(f.read())
    f.close()


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    master_pass = request.form['passwd']
    hashed_pass = hashlib.sha256(master_pass.encode()).hexdigest()
    if (hashed_pass == vault.get("master")):
        return render_template('menu.html')
    else:
        return render_template('error.html', message='Invalid Username or password')


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
    app = request.form['app']
    if (app in vault.keys()):
        result = {}
        result['application'] = app
        result['username'] = vault.get(app).get('username')
        result['password'] = vault.get(app).get('password')
        return render_template('success.html', result=result)
    else:
        return render_template('error.html', message='Application does not exist')


@app.route('/write', methods=['POST'])
def write():
    storage = os.path.join(app.root_path, "resources/storage.json")
    f = open(storage, "w")
    app_name = request.form['app']
    new_login = request.form['username']
    new_passwd = request.form['password']
    entry = {}
    entry["username"] = new_login
    entry["password"] = new_passwd
    vault[app_name] = entry
    f.write(json.dumps(vault))
    f.close()
    return render_template('success.html', result=entry)


@app.route('/update', methods=['POST'])
def update():
    old = request.form['old']
    new = request.form['new']
    confirm = request.form['confirm']

    if (confirm != new):
        return render_template('error.html', message='Passwords do not match')
    hashold = hashlib.sha256(old.encode()).hexdigest()
    if (hashold != vault.get('master')):
        return render_template('error.html', message='Invalid old password')

    hashnew = hashlib.sha256(new.encode()).hexdigest()
    vault['master'] = hashnew
    storage = os.path.join(app.root_path, "resources/storage.json")
    f = open(storage, 'w')
    f.write(json.dumps(vault))
    f.close()  
    result = {}
    result['old_password'] = old
    result['new_password'] = new
    return render_template('success.html', result=result)

@app.route('/startover', methods=['POST'])
def startover():
    return render_template('menu.html')


if __name__ == '__main__':
    storage = os.path.join(app.root_path, "resources/storage.json")
    init(storage)
    app.run('0.0.0.0', 5000)
