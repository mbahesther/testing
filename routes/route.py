from run import app, my_cursor, mydb, MySQLdb, CORS, jwt, is_not_blacklisted
from flask import request, json, jsonify


from flask_jwt_extended import ( JWTManager,create_access_token, get_jwt_identity,
                jwt_required, current_user)


from datetime import datetime, date, timedelta, time
import datetime

from werkzeug.utils import secure_filename
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

jwt_manager = JWTManager(app)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  
allowed_extensions = ['jpg', 'png', 'jpeg']

    
#allowed images extensions
def check_file_extension(filename):
   return filename.split('.')[-1] in allowed_extensions

# restaurant add food menu
@app.route('/api/merchant/add_food_menu', methods= ['POST'])
@jwt_required()
def add_food_menu():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    food_title = request.form['food_title']
    description = request.form['description']
    price = request.form['price']

    category = request.form['category']

    app.logger.info('in upload route')

    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('CLOUD_API_KEY'), 
      api_secret=os.getenv('CLOUD_API_SECRET'))
    upload_result = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder='merchant')
            #image = app.logger.info(upload_result)
            image = upload_result['secure_url']

            my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            my_cursor.execute('INSERT INTO food_menu(food_title, description, price, food_images, category, restaurant_id) VALUES (%s,%s,%s,%s,%s,%s)', [food_title, description, price, image,category, restaurant_id])
            mydb.commit()
            my_cursor.close()
            mydb.close()
            return jsonify({'msg':'food menu added successfully'}),200 
    
    return jsonify({'msg':'Can\'t, add food menu '}),200 

    
# restaurant update or edit their food menu
@app.route('/api/merchant/add_food_menu/<int:menu_id>', methods=['PUT'])
@jwt_required()
def edit_menu(menu_id):
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    food_title = request.form['food_title']
    description = request.form['description']
    price = request.form['price']
    category = request.form['category']

    app.logger.info('in upload route')

    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('CLOUD_API_KEY'), 
      api_secret=os.getenv('CLOUD_API_SECRET'))
    upload_result = None
    if request.method == 'PUT':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder='merchant')
            #image = app.logger.info(upload_result)
            image = upload_result['secure_url']
            my_cursor.execute('SELECT * FROM food_menu WHERE menu_id =%s AND restaurant_id=%s', [menu_id, restaurant_id ])
            query = my_cursor.fetchone() 
            if query:
                my_cursor.execute('UPDATE food_menu SET food_title=%s, description=%s, price=%s, food_images=%s, category=%s WHERE menu_id=%s', [food_title, description, price, image,category, menu_id ])
                mydb.commit()
                my_cursor.close()
                mydb.close()
                return jsonify({'msg':'Food menu Updated successfully'}),200
            else:
                return jsonify({'msg':'food_menu doesn\'t exist'})
    return jsonify({'msg':'Can\'t, add food menu '}),200           


#delete restaurant food menu
@app.route('/api/merchant/add_food_menu/<int:menu_id>', methods=['DELETE'])
@jwt_required()
def delete_menu(menu_id):
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_menu WHERE menu_id =%s AND restaurant_id=%s', [menu_id, restaurant_id ])
    query =my_cursor.fetchone() 
    if query:
        my_cursor.execute('DELETE FROM food_menu WHERE menu_id=%s', [menu_id ])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify({'msg':'Food menu Deleted !!!'})
    else:
        return jsonify({'msg':'food_menu doesn\'t exist'})


# retrieve each  food menu from particular restaurant
@app.route('/api/merchant/each_food', methods=['GET'])
@jwt_required()
def each_food():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    data = request.json
    each_food= data['each_food']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_menu WHERE menu_id =%s AND restaurant_id=%s', [each_food, restaurant_id])
    query = my_cursor.fetchone()
    if query:
        each_menu = {}
        each_menu['title']=query[1]
        each_menu['description']=query[2]
        each_menu['price']=query[3]
        each_menu['image']=query[4]
        each_menu['category']=query[5]
        return jsonify(msg = each_menu)
    else:
        return jsonify({'msg':'no food available'})    
   

#retrieve food menu by category        
@app.route('/api/merchant/restaurant_menu_category', methods=['GET'])
@jwt_required()
def  restaurant_menu_category():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    data = request.json
    restaurant_category = data['restaurant_category']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_menu WHERE category =%s AND restaurant_id=%s', [restaurant_category, restaurant_id])
    query = my_cursor.fetchall()
    if query:
        cat_list = []
        for result in query:         
            cat_list.append({
                'food title'  :result[1], 
                'description'  : result[2],
                'price' : result[3] ,
                'images' : result[4] ,
                'category'  :result[5]  
            } )
        return jsonify({'msg':cat_list}),200
    else:
        return jsonify({'msg': 'category doesn\'t exist'})    


#restaurant tp retrieve all food menu
@app.route('/api/merchant/restaurantfood_menu', methods=['GET'])
@jwt_required()
def restaurantfood_menu():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM food_menu WHERE restaurant_id =%s', [restaurant_id])
    food = my_cursor.fetchall()
    if food:
        food_menu = []
        for result in food:
            food_menu.append({
                'food title'  :result[1], 
                'description'  : result[2],
                'price' : result[3] ,
                'image' : result[4] ,
                'category'  :result[5]      
            } )
        return jsonify({'msg':food_menu}),200
    else:
        return jsonify({'msg':'no menu available'}),200

#orders list
@app.route('/api/merchant/orders', methods=['POST'])
@jwt_required()
def orders():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    now = datetime.datetime.now()
    dt_now = now.strftime("%Y-%m-%d %I:%M %p" )

    data = request.json
    menu_id = data['menu_id']
    status = 'pending'
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    #getting from the menu 
    my_cursor.execute('SELECT * FROM food_menu WHERE menu_id =%s AND restaurant_id=%s', [menu_id, restaurant_id])
    menu = my_cursor.fetchone()
    if menu:
        price =menu[3]       
        category_id =menu[5] 

        my_cursor.execute('INSERT INTO sales_history(menu_id, price, category,  status, date_order, restaurant_id) VALUES (%s,%s,%s,%s,%s,%s)', [menu_id, price, category_id, status, dt_now,  restaurant_id ])
        mydb.commit()
        my_cursor.close()
        mydb.close()
        return jsonify({'msg': 'ordered successfully'})
    else:
        return jsonify(msg="no order placed ")    


# each resturant to view all their order
@app.route('/api/merchant/restaurant_order', methods=['GET'])
@jwt_required()
def restaurant_order():
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE restaurant_id =%s ORDER BY id DESC', [restaurant_id])
    food = my_cursor.fetchall()
    if food :
        ordermenu = []
        for result in food:
            ordermenu.append({
                'menu_id'  :result[1], 
                'price'  : result[2],
                'category' : result[3] ,
                'activity' : result[4] ,
                'reasons'  :result[5] ,
                'status'  :result[6] ,
                'date'   : result[7] 
            } )
        return jsonify({'msg':ordermenu}),200
         

# update edit/update order
@app.route('/api/merchant/restaurant_order/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_restaurant_order(item_id):
    current_restaurant = get_jwt_identity()   
    restaurant_id = current_restaurant[0]
    data = request.json
    food = data['food']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE id =%s AND restaurant_id=%s', [item_id, restaurant_id ])
    query =my_cursor.fetchone() 
    if query:
         my_cursor.execute('UPDATE sales_history SET food_id=%s  WHERE id=%s', [food, item_id ])
         mydb.commit()
         my_cursor.close()
         mydb.close()
         return jsonify({'msg':'order updated !!!'})
    else:
        return jsonify({'msg':'food_menu doesn\'t exist'})


#accept an order
@app.route('/api/merchant/restaurant_accept/<int:user_id>', methods=['PUT'])
@jwt_required()
def accept_orders(user_id):
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    activity = 'Accepted'
    status = 'processing'
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE id=%s  AND restaurant_id=%s ', [user_id, restaurant_id])
    accept = my_cursor.fetchone()
    if accept:
         my_cursor.execute('UPDATE sales_history SET activity=%s, status=%s  WHERE id=%s', [activity, status, user_id ])
         mydb.commit()
         my_cursor.close()
         mydb.close()
         return jsonify({'msg':'Accepted the order and it is being processed'})
    else:
        return jsonify({'msg':'not available'})


#cancel an order with reason
@app.route('/api/merchant/restaurant_cancel/<int:user_id>', methods=['PUT'])
@jwt_required()
def cancel_orders(user_id):
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    activity = 'Cancelled'
    status = 'Cancelled'
    data = request.json
    reasons= data['reasons']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE id=%s  AND restaurant_id=%s ', [user_id, restaurant_id])
    cancel = my_cursor.fetchone()
    if cancel:
         my_cursor.execute('UPDATE sales_history SET activity=%s, status=%s, reasons=%s  WHERE id=%s', [activity, status, reasons, user_id ])
         mydb.commit()
         my_cursor.close()
         mydb.close()
         return jsonify({'msg':'Order Cancelled'})
    else:
        return jsonify({'msg':'not available'})


# updating status of orders
@app.route('/api/merchant/restaurant_status/<int:user_id>', methods=['POST'])
@jwt_required()
def status_orders(user_id):
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    status = 'Out for delivery'
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE id=%s  AND restaurant_id=%s ', [user_id, restaurant_id])
    user = my_cursor.fetchone()
    if user:
         my_cursor.execute('UPDATE sales_history SET status=%s  WHERE id=%s', [status, user_id ])
         mydb.commit()
         my_cursor.close()
         mydb.close()
         return jsonify({'msg':'Out for delivery'})
    else:
        return jsonify({'msg':'not available'})

#completed status
@app.route('/api/merchant/status_complete/<int:user_id>', methods=['PUT'])
@jwt_required()
def status_complete(user_id):
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    status = 'Completed'
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM sales_history WHERE id=%s  AND restaurant_id=%s ', [user_id, restaurant_id])
    user = my_cursor.fetchone()
    if user:
         my_cursor.execute('UPDATE sales_history SET status=%s  WHERE id=%s', [status, user_id ])
         mydb.commit()
         my_cursor.close()
         mydb.close()
         return jsonify({'msg':'Out for delivery'})
    else:
        return jsonify({'msg':'not available'})
 
 
#merchant logo
@app.route('/api/merchant/profile_logo', methods=['POST'])
@jwt_required()
def profile_logo(): 
    current_restaurant = get_jwt_identity()
    restaurant_id = current_restaurant[0]
    print(restaurant_id)
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT id FROM merchant WHERE id=%s', [restaurant_id])
    user = my_cursor.fetchone()
    if user :
        app.logger.info('in upload route')

        cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('CLOUD_API_KEY'), 
        api_secret=os.getenv('CLOUD_API_SECRET'))
        upload_result = None
        if request.method == 'POST':
            file_to_upload = request.files['file']
            app.logger.info('%s file_to_upload', file_to_upload)
            if file_to_upload:
                upload_result = cloudinary.uploader.upload(file_to_upload, folder='merchant')
                #image = app.logger.info(upload_result)
                profile_logo = upload_result['secure_url']

                my_cursor.execute('UPDATE merchant SET profile_logo=%s  WHERE id=%s', [profile_logo, restaurant_id])
                mydb.commit()
                my_cursor.close()
                mydb.close()
                return jsonify({'msg':'logo successfully added'}),200 
    else:
        return jsonify(msg="merchant not found")            

#from hello.app import app as application
  #view all payment received
  #filter by status= completed
# my_cursor.execute('SELECT * FROM sales_history WHERE restaurant_id=%s  AND  status=%s ', [restaurant_id, status])




 # dt_now = now.strftime("%d-%m-%Y %H:%M:%S")
# my_cursor.execute('SELECT amount, type, date FROM transactions WHERE email = %s', [user_id])
# my_cursor.execute('SELECT * FROM food_menu WHERE restaurant_id =%s ORDER BY menu_id DESC', [restaurant_id])
