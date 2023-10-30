from repository.SQL_query import caras_totales, caras_identificadas, login_query
from werkzeug.security import check_password_hash
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

#Verificacion de admins, login
@auth.verify_password
def verify_password_home(username, password):
    global users
    users=login_query()
    if username in users and \
            check_password_hash(users.get(username),password):
        return username


def home_funcionarios():
    #préstamos totales
    cartotal=caras_totales()
    #préstamos hoy
    carid=caras_identificadas()
    #pendiente por devolver
    
    
    #_reparar
    data_final = {
    "cartotal": cartotal,
    "carid": carid,
    
    }
    return data_final