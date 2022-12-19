from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
import os
import MySQLdb.cursors
import mysql.connector
import MySQLdb.cursors
from flask_cors import CORS

import jwt as JWTT

from datetime import datetime, date, timedelta, time
import datetime

from flask_jwt_extended import (JWTManager, create_access_token, get_jwt_identity,
                                 jwt_required, get_jwt, get_jwt_header)

ACCESS_EXPIRES = timedelta(hours=1)                                 

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']= 'pymysql://root:''@localhost/foodapi'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES


jwt = JWTManager(app)

mydb = mysql.connector.connect(
    host='localhost',
    user ='root',
    password ='',
    database ='foodapi'
    )

my_cursor =mydb.cursor(buffered=True)  




@app.before_request
def  is_not_blacklisted():
    authorization = request.headers.get('Authorization')
    if authorization:
        try:
            token = authorization.split(" ")[1] 
            decode = JWTT.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            
            jti = decode['jti']
            my_cursor.execute('SELECT * FROM black_list WHERE jti=%s  ', [jti])
            query = my_cursor.fetchone()
            if query:
                return jsonify(success= False, msg= "this is currently unavailable to you, login"),401
        except Exception as e:
            # print(e)
            return jsonify(msg="signature has expired"),500
        
                  
                

# app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:''@localhost/foodapi'
