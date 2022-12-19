from run import *
from extension.forgot_password import merchant_forgot_password
from routes import route
from passlib.hash import pbkdf2_sha256 as sha256

import jwt as JWTT

from collections import OrderedDict


#merchant signin
@app.route('/api/merchant/signin', methods=['POST'])
def merchant_signin():
    data = request.json
    email = data['email']
    password = data['password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    inactive = user[7]
    if inactive == 1:
        return jsonify(msg="this account is deactivated")
    else:
        if user and sha256.verify(password, user[8]):
            access_token = create_access_token(identity=user)
            return jsonify(access_token=access_token),200
        else:
            return jsonify({'msg':'incorrect password or phone number'}),401 


# merchant forgot password request
@app.route('/api/merchant/reset_password', methods=['POST'])
def merchant_reset_request():
    data = request.json
    email = data['email']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user is None:
           return jsonify({'msg':'there is no account with that email, you have to signup first'})   
    else:
        mail = merchant_forgot_password(email)
        return jsonify({'msg':'A link has been sent to your Email to reset your password '}),200 

# merchant forgot Password reset
@app.route('/api/merchant/passwordreset/<token>', methods=['POST'])
def merchant_password_reset(token):
    verify=  JWTT.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
    
    if verify is None:
        return jsonify({'msg':'token expired or invalid go back to generate a token to reset your password'}),401  
        
    else:
        email = verify['sub']   
        data = request.json
        password = data['password']
        confirm_password = data['confirm_password']
        if password == confirm_password:
            hash_password = sha256.hash(password)
            my_cursor.execute("""UPDATE merchant SET password=%s WHERE email = %s""", [hash_password, email])
            mydb.commit()
            my_cursor.close()
            mydb.close()
            return jsonify({'msg':'You password has been reset, you can now login with the new password'}),200  
    return jsonify({'msg':'password and confirm password didn\'t match '}),401  


#merchant Reset password
@app.route('/api/merchant/change_password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user_id = current_user[0]
    data = request.json
    current_password = data['current_password']
    new_password =  data['new_password']
    confirm_password = data['confirm_password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant WHERE id =%s''', [user_id])
    user = my_cursor.fetchone()
    if user and sha256.verify(current_password, user[6]):
        if new_password == confirm_password:
             hash_password = sha256.hash(new_password) 
             my_cursor.execute("""UPDATE merchant SET password=%s WHERE id = %s""", [hash_password, user_id])
             mydb.commit() 
             my_cursor.close()
             mydb.close()
             return jsonify({'msg':'Password changed successfully'}),200
        else:
            return jsonify({'msg':'Password didn\'t match'}),401
    else:
        return jsonify({'msg':'Your current password is incorrect'}),401       


#add food category for restarant
@app.route('/api/merchant/add_food_category', methods=['POST'])
@jwt_required()
def add_food_category():
    current_resturant = get_jwt_identity()
    restaurant_id = current_resturant[0]
    data = request.json
    food_category = data['food_category']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor) 
    my_cursor.execute('SELECT * FROM  food_category WHERE restaurant_id=%s AND category=%s',[restaurant_id, food_category])
    query = my_cursor.fetchone()
    if query :
        return jsonify({'msg': 'category already exist'}),401
    else:
          my_cursor.execute('INSERT INTO food_category(category, restaurant_id) VALUES(%s, %s)', [food_category, restaurant_id])
          mydb.commit()
          return jsonify({'msg':'Category added successfully'}),200


#geting each category
# @app.route('/api/merchant/add_food_category/<int:cat_id>', methods=['GET'])
# /api/merchant/add_food_category/4
# @jwt_required()
# def get_food_category(cat_id):
#     my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
#     my_cursor.execute('SELECT * FROM food_category WHERE id =%s AND restaurant_id', [cat_id])
#     query =my_cursor.fetchone()
#     return jsonify({'msg':query})


#edit food category for restaurant
@app.route('/api/merchant/add_food_category/<int:cat_id>', methods=['PUT'])
@jwt_required()
def edit_food_category(cat_id):
    current_resturant = get_jwt_identity()
    restaurant_id = current_resturant[0]
    data = request.json
    food_category = data['food_category']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_category WHERE cat_id =%s AND restaurant_id=%s', [cat_id, restaurant_id ])
    query =my_cursor.fetchone() 
    if query:
        my_cursor.execute('UPDATE food_category SET  category=%s WHERE id=%s', [food_category, cat_id ])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify({'msg':'Category Updated successfully'}),200
    else:
        return jsonify({'msg':'Category doesn\'t exist'}),401


#specific restaurant delete a category
@app.route('/api/merchant/add_food_category/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_food_category(cat_id):
    current_resturant = get_jwt_identity()
    restaurant_id = current_resturant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_category WHERE cat_id =%s AND restaurant_id=%s', [cat_id, restaurant_id ])
    query =my_cursor.fetchone() 
    if query:
        my_cursor.execute('DELETE FROM food_category WHERE id=%s', [cat_id ])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify({'msg':'Category  Deleted'}),200
    else:
        return jsonify({'msg':'Category number doesn\'t exist'}),401


#specific resturant to get all their category
@app.route('/api/merchant/food_category', methods=['GET'])
@jwt_required()
def food_category():
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT LOWER(category) FROM food_category WHERE restaurant_id =%s', [restaurant_id])
    query = my_cursor.fetchall()      
    if query:
        category = []
        for result in query:         
            category.append({
                'category name'  :result[0]                
            } )
        return jsonify({'msg':category}),200      
    else:
        return jsonify({'msg': 'category not available'}),401   

#get address
@app.route('/api/merchant/address', methods=['GET'])
@jwt_required()
def address():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant_address WHERE restaurant_id =%s''', [restaurant_id])
    add = my_cursor.fetchone()
    if add: 
        address = {}
        address['state']= add[1]
        address['address']= add[4]
        return jsonify({'msg':address}),200
    else:
        return jsonify({'msg':'not available'}),401   
   

#merchant address
@app.route('/api/merchant/merchant_address', methods=['POST'])
@jwt_required()
def merchant_address():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    data = request.json
    state = data['state']
    longitude = data['longitude']
    latitude = data['latitude']
    address = data['address']
    open_time = data['open_time']
    close_time = data['close_time']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant_address WHERE restaurant_id =%s''', [restaurant_id])
    add = my_cursor.fetchone()
    if add:
        return jsonify(msg="already added address"),401
    else:    
        my_cursor.execute('INSERT INTO merchant_address(state,longitude, latitude, address,open_time, close_time, restaurant_id) VALUES(%s, %s, %s, %s,%s,%s,%s)', [state, longitude, latitude, address,open_time, close_time, restaurant_id])
        mydb.commit() 
        my_cursor.close()
        mydb.close()
        return jsonify(msg="address added!"),200


#merchant update their address
@app.route('/api/merchant/merchant_address/<int:adrs_id>', methods=['PATCH'])
@jwt_required()
def update_address(adrs_id):
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    data = request.json
    state = data['state']
    longitude = data['longitude']
    latitude = data['latitude']
    address = data['address']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  merchant_address WHERE id=%s AND restaurant_id=%s ''', [adrs_id, restaurant_id])
    add = my_cursor.fetchone()
    if add:
        my_cursor.execute('UPDATE merchant_address SET state=%s, longitude=%s, latitude=%s, address=%s WHERE id=%s', [state, longitude, latitude, address, adrs_id])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify(msg=" Address updated ")
    else:        
        return jsonify(msg=" no address added")


#specific restaurant to see their  account info
@app.route('/api/merchant/merchant_account', methods=['GET' ])
@jwt_required()
def merchant_account():
        current_restaurant = get_jwt_identity()     
        restaurant_name= current_restaurant[1]
        restaurant_email = current_restaurant[2]
        restaurant_phone = current_restaurant[3]  
        restaurant_about = current_restaurant[4]
        return jsonify({
                        'name': restaurant_name, 
                         'email':restaurant_email,
                         'phone_number': restaurant_phone,
                          'about':restaurant_about})

       
#specific restaurant to update their  account info
@app.route('/api/merchant/merchant_account/<int:rest_id>', methods=['PATCH' ])
@jwt_required()
def merchant_update_account(rest_id):
        current_restaurant = get_jwt_identity()
        # current_id = current_restaurant[0]      
        current_name= current_restaurant[1]
        current_email = current_restaurant[2]
        current_phone = current_restaurant[3]
            
        data = request.json
        restaurant_name = data['restaurant_name']
        restaurant_email = data['restaurant_email']
        restaurant_phone_number = data['restaurant_phone_number']
        restaurant_about = data['restaurant_about']
        
        if len(restaurant_phone_number) !=14:
            return jsonify({'msg':'Your phone number is invalid'}),400
        else: 
            if current_email == restaurant_email :
                if  current_phone == restaurant_phone_number :
                    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                    my_cursor.execute('UPDATE merchant SET name=%s, email=%s, phone_number=%s, about_restaurant=%s WHERE id=%s', [restaurant_name, restaurant_email, restaurant_phone_number, restaurant_about, rest_id])
                    mydb.commit()
                    my_cursor.close()
                    return jsonify({'success': True,'msg':'Your account has be updated'}),200
 
                else:  
                    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                    my_cursor.execute('''SELECT * FROM merchant WHERE phone_number =%s''', [restaurant_phone_number])
                    user = my_cursor.fetchone()
                    if user:
                        return jsonify({'msg':'phone exist already exits, use another phone'}),400
                    else:    
                        my_cursor.execute('''SELECT * FROM  merchant WHERE email =%s ''', [restaurant_email])
                        query = my_cursor.fetchone()
                        if query is None:
                            my_cursor.execute('UPDATE merchant SET name=%s, email=%s, phone_number=%s, about_restaurant=%s WHERE id=%s', [restaurant_name, restaurant_email, restaurant_phone_number, restaurant_about, rest_id])
                            mydb.commit()           
                            return jsonify({'success': True,'msg':'Your account has be updated'}),200
            else:  
                return jsonify({'msg':'Email already exits, use another email'}),400


#merchant opening and closing time                           
@app.route('/api/merchant/open_close_time', methods=['GET'])
@jwt_required()
def open_close_time():  
      current_restaurant = get_jwt_identity()   
      restaurant_id = current_restaurant[0]
    #   open_time = datetime.time(hour=10, minute=0, second=0)
    #   close_time = datetime.time(hour=18, minute=0, second=0)
      now = datetime.datetime.now()
      current_time = now.strftime("%H:%M:%S")
      my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
      my_cursor.execute('''SELECT open_time, close_time FROM merchant_address WHERE restaurant_id=%s''', [restaurant_id])
      query = my_cursor.fetchone()
      open_time =query[0]
      close_time =  query[1]
      if open_time < current_time < close_time:
        return jsonify(msg="Open"),200
      else:
        return jsonify(msg="Closed"),200


#soft delete a merchant
@app.route('/api/merchant/delete_account/<int:id>', methods=['POST'])
@jwt_required()
def delete_account(id):
      current_restaurant = get_jwt_identity()   
      restaurant_id = current_restaurant[0]
      my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
      my_cursor.execute('''SELECT * FROM merchant WHERE id=%s''', [id])
      query = my_cursor.fetchone()
      if query:
            inactive = True
            my_cursor.execute('UPDATE merchant SET inactive=%s WHERE id=%s', [inactive, id])
            mydb.commit() 
            return jsonify(msg="your account has be deleted"),200
      else:
        return jsonify(msg="invalid request")


     

#merchant or resturant logout
@app.route('/api/merchant/logout', methods=['DELETE'])
@jwt_required()
def logout():     
    jti = get_jwt()["jti"]
    now = datetime.datetime.now()
    dt_now = now.strftime("%Y-%m-%d %I:%M %p" )
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM black_list WHERE jti =%s''', [jti])
    query = my_cursor.fetchone()
    if query:
        return jsonify({'msg': 'already logout'})
    else:
        my_cursor.execute('INSERT INTO black_list(jti, created) VALUES(%s, %s)', [jti, dt_now])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify(msg="Access token revoked")

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
    #response.access_control_allow_origin = "*"
   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)