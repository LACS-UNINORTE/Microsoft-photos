#from flaskext.mysql import MySQL
from decouple import config
import pymysql

 
#DB connection
def connect_db():
    return pymysql.connect(host=config('MYSQL_HOST'), user=config('MYSQL_USER'), password=config('MYSQL_PASSWORD'), db=config('MYSQL_DB'))
    
#Login
def login_query():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT userAdmin,password FROM facelacs.`Admin`;")
        data = cur.fetchall()
        global users
        users = {}
        users={admin[0]:admin[1] for admin in data}
    cur.close()
    return users

#caras totales registradas
def caras_totales():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM facelacs.`facedata`;")
        data_sol = cur.fetchall()
        data_sol2 = data_sol[0]
        cartotal = data_sol2[0]
    cur.close()
    return cartotal

#Caras totales identificadas
def caras_identificadas():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM facelacs.`facereco` ")
        data_sol = cur.fetchall()
        data_sol2 = data_sol[0]
        carid = data_sol2[0]
    cur.close()
    return carid



#Show admins
def show_admins_db():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM facelacs.`Admin`;")
        admins = cur.fetchall()
    cur.close()
    return admins 

#Add admin
def add_admin_db(id,nombre,email,usuario,contraseña):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("INSERT INTO `facelacs`.`Admin` (`idAdmin`, `nomAdmin`, `correoAdmin`, `userAdmin`, `password`) VALUES (%s,%s,%s,%s,%s);",(id,nombre,email,usuario,contraseña))
        connection.commit()
        message = 'Administrador agregado correctamente'
    cur.close() 
    return message

#Edit admin
def edit_admin_db(id):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM facelacs.`Admin` WHERE idAdmin = '{}';".format(id))
        admin = cur.fetchall()
    cur.close() 
    return admin

#Update admin
def update_admin_db(id,nombre,email,usuario,contraseña,idOld):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("UPDATE `facelacs`.`Admin` SET `idAdmin` = '{}', `nomAdmin` = '{}',`correoAdmin` = '{}' ,`userAdmin` = '{}', `password`='{}' WHERE (`idAdmin` = '{}');".format(id,nombre,email,usuario,contraseña,idOld))
        connection.commit()
        message = 'Administrador actualizado correctamente'
    cur.close() 
    return message

#Delete admin
def delete_admin_db(id):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("DELETE FROM `facelacs`.`Admin` WHERE (`idAdmin` = '{}');".format(id))
        connection.commit()
        message = 'Administrador eliminado correctamente'
    cur.close() 
    return message

#agregar cara  a base de datos

def add_face_data(fileID,vector,personID):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("INSERT INTO `facelacs`.`facedata` (`FileID`, `Vector`,`PersonID`) VALUES (%s,%s,%s);",(fileID,vector,personID))
        connection.commit()
        
    cur.close() 
   

def add_reco_db(fileID,vector,photo):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("INSERT INTO `facelacs`.`facereco` (`FileID`, `Vector`,`Photo`) VALUES (%s,%s,%s);",(fileID,vector,photo))
        connection.commit()
        
    cur.close() 
   

def get_id_db():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT ID FROM facelacs.`facereco` ORDER BY ID DESC limit 1 ;")
        admin = cur.fetchall()
    cur.close() 
    return admin

def get_face_db():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT ID,FileID,Vector FROM facelacs.`facereco` ;")
        admin = cur.fetchall()
    cur.close() 
    return admin

def get_file_db():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT FileID FROM facelacs.`facedata` ;")
        admin = cur.fetchall()
    cur.close() 
    return admin

def get_photo_db():
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT ID,Photo FROM facelacs.`facereco` ;")
        admin = cur.fetchall()
    cur.close() 
    return admin

def get_related_photo_db(id,limite,desplazamiento):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT FileID FROM facelacs.facedata WHERE PersonID = {} LIMIT {} OFFSET {};".format(id,limite,desplazamiento))
        admin = cur.fetchall()
    cur.close() 
    return admin

def get_rp_count_db(id):
    connection = connect_db()
    with connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM facelacs.facedata WHERE PersonID = {};".format(id))
        data_sol = cur.fetchall()
        data_sol2 = data_sol[0]
        count = data_sol2[0]
    cur.close() 
    return count

