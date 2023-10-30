from flask import request
from repository.SQL_query import login_query, show_admins_db,add_admin_db,edit_admin_db,update_admin_db,delete_admin_db
from werkzeug.security import generate_password_hash

def admin_main():
    users=login_query()
    admins=show_admins_db()
    return users, admins

def add_admin():
    if request.method == 'POST':
        id = request.form['_id']
        nombre = request.form['name']
        email = request.form['email']
        usuario = request.form['user']
        contraseña = generate_password_hash(request.form['password'])
        message=add_admin_db(id,nombre,email,usuario,contraseña)
    return message

def edit_admin(id):
    admin=edit_admin_db(id)
    return admin[0]

def update_admin(id):
    if request.method == 'POST':
        idOld=id
        id = request.form['_id']
        nombre = request.form['name']
        email = request.form['email']
        usuario = request.form['user']
        contraseña = generate_password_hash(request.form['password'])
        message=update_admin_db(id,nombre,email,usuario,contraseña,idOld)
    return message

def delete_admin(id):
    message=delete_admin_db(id)
    return message