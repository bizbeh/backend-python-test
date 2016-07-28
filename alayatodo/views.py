from alayatodo import app
import json
import math

from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash
    )

ItemPerPage = 5

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s' and user_id = '%s'" % (id , session['user']["id"]))
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s' and user_id = '%s'" % (id , session['user']["id"]))
    todo = json.dumps(dict(cur.fetchone()))
    return render_template('todo-json.html', todo=todo)

@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = Get_todo(0)
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos, cur=1)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    t_Desc = request.form.get('description', '').strip()
    if t_Desc == '' :
        flash('Please Enter a valid description')
        return redirect('/todo')
    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
        % (session['user']['id'], t_Desc)
    )
    g.db.commit()
    flash('Your to do list was successfully added')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    flash('Your to do list was successfully deleted')
    return redirect('/todo')

@app.route('/todoUpdate/<id>', methods=['POST'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET complete = 1 WHERE id ='%s'" % id)
    g.db.commit()
    flash('Congratulations! you have completed a to do list')
    return redirect('/todo')

@app.route('/todoNothing/', methods = ['POST'])
def todo_Nothing():
    pass
    return redirect('/todo')

@app.route('/todoPre/<idx>', methods = ['post'])
def todo_Pre(idx):
    if (int(idx) == 1):
        temp_Idx = int(idx)
    else:
        temp_Idx = int(idx)-1
    cur = Get_todo(((temp_Idx - 1) * ItemPerPage))
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos, cur=temp_Idx)

@app.route('/todoNext/<idx>', methods = ['post'])
def todo_Next(idx):
    cur = g.db.execute("SELECT COUNT(1) FROM todos WHERE user_id = '%s'" % session['user']["id"])
    count = cur.fetchone()[0]
    if (math.ceil(float(count)/ItemPerPage) < int(idx)+1):
        temp_Idx = int(idx)
    else:
        temp_Idx = int(idx)+1
    cur = Get_todo(((temp_Idx-1)*ItemPerPage))
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos, cur=temp_Idx)

def Get_todo(offset):
    cur = g.db.execute("SELECT * FROM todos WHERE user_id = '%s' ORDER BY id ASC LIMIT '%s' OFFSET '%s'" % (
    session['user']["id"], str(ItemPerPage), str(offset)))
    return cur