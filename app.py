# version 1.1 created dec 8 2024,
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson import ObjectId
from datetime import datetime, timedelta
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from wtforms import FloatField
from wtforms.validators import DataRequired, NumberRange


mongo_uri = 'mongodb://mongodb:27017/formDB'
#mongo_uri = 'mongodb://172.18.0.2:27017/formDB'
# Try connecting to MongoDB, with retries, shtoto Lora reve che ne vinagi trygva.
for i in range(10):  # Retry 10 times
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  # 5 seconds timeout
        client.server_info()  # This will throw an exception if MongoDB is not available
        print("Connected to MongoDB!")
        break
    except ConnectionError:
        print(f"Attempt {i + 1} failed. Retrying...")
        time.sleep(8)  # Wait for 5 seconds before retrying
else:
    print("Failed to connect to MongoDB after several retries.")
    exit(1)



app = Flask(__name__,static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/formDB'  # Update with your MongoDB connection URI
#app.config['MONGO_URI'] = 'mongodb://172.18.0.2:27017/formDB'  # Update with your MongoDB connection URI
mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# route for protocol template page
@app.route('/protocol_template.html')
def protocol_template():
    return render_template('protocol_template.html')

# route for protocol repaired device template page
@app.route('/protocol_repaired_device.html')
def protocol_repaired_device():
    return render_template('protocol_repaired_device.html')

@app.route('/submit-form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        # Extract data from form fields (replace with actual field IDs)
        datetime_utc_now = datetime.now()
        created_date = datetime_utc_now.strftime('%d/%m/%y')

        checkbox_names = ['accessory_case', 'accessory_bag', 'accessory_charger', 'accessory_sim']  # Example names
        # Extract checkbox values and set to True if checked, False if not
        accessories = {checkbox_name: bool(request.form.get(checkbox_name)) for checkbox_name in checkbox_names}

        form_data = {
            'model': request.form.get('model'),
            'phone': request.form.get('phone'),
            'device_type': request.form.get('device_type'),
            'offered_price': request.form.get('offered_price'),
            'created_date': created_date,
            'info': request.form.get('info'),
            'status': 'приет за ремонт',
            'pincode':request.form.get('pincode'),
            'passcode': request.form.get('passcode'),
            'other_info': request.form.get('other_info'),
            'accessories': accessories

            # ... include all other form fields here ...
        }
        last_order = mongo.db.forms_collection.find_one(sort=[("order_number", -1)])
        # Check if the 'order_number' field exists in the last_order and assign next_order_number
        if last_order and 'order_number' in last_order:
            next_order_number = last_order['order_number'] + 1
        else:
            next_order_number = 1
        # Add the order number to form_data
        form_data['order_number'] = next_order_number
        # Insert data into MongoDB (replace 'forms_collection' with your collection name)
        mongo.db.forms_collection.insert_one(form_data)

        flash('Form submitted successfully!')
        return redirect(url_for('form_submitted'))  # Redirect to a confirmation page


@app.route('/view-forms')
@app.route('/view-forms/<int:page>')
@login_required
def view_forms(page=1):
    per_page = 15
    status_filter = request.args.get('status', '')  # Get the status filter from query parameters

    # MongoDB query with conditional filtering by status
    query = {}
    if status_filter:
        query['status'] = status_filter

    # MongoDB aggregation pipeline
    pipeline = [
        {'$match': query},  # Apply the status filter
        {
            '$sort': {
                'status_order_filter': 1,  # Sort by status_order_filter
                'created_date': 1  # Then sort by created_date in descending order
            }
        },
        {'$skip': (page - 1) * per_page},
        {'$limit': per_page}
    ]

    forms = list(mongo.db.forms_collection.aggregate(pipeline))
    total_count = mongo.db.forms_collection.count_documents(query)
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('view_forms.html', forms=forms, page=page, total_pages=total_pages, status_filter=status_filter)



#route for form submitting
@app.route('/view-forms')
def form_submitted():
    return redirect(url_for('view_forms'))


class MyForm(FlaskForm):


    phone = StringField('Phone', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    info = StringField('Information', default='Information', validators=[DataRequired()])
    offered_price = StringField('Offered Price', default='0', validators=[DataRequired()])
    device_type = StringField('Device type', default='Телефон', validators=[DataRequired()])
    pincode = StringField('Pincode')
    passcode = StringField('Passcode')
    status = StringField('status')
    other_info = StringField('Other Info')
    case = StringField('case')
    created_date = StringField('created_date')
    accessories = {}
    part_price = StringField('part_price')
    warranty = StringField('warranty')
    repair_details = StringField('repair_details')
    repaired_date = StringField('repaired_date')
    status_order_filter = StringField('status_order_filter')
    technician = StringField('technician')
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Route for handling login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Replace with your actual authentication logic
        if username == 'admin' and password == 'password':
            user = User(username)
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)


# Route for handling logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Index route (landing page)
@app.route('/')
@login_required
def index():
    return render_template('landing.html')


def check_if_repaired_date_exist(form_id):
    form_id = ObjectId(form_id)

    # Search for the document
    form_document = mongo.db.forms_collection.find_one({'_id': form_id})

    # Retrieve the 'repaired_date' field
    repaired_date = form_document.get('repaired_date') if form_document else None

    return repaired_date

# Route for form filling
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    form = MyForm()

    if form.validate_on_submit():
        datetime_utc_now = datetime.now()
        created_date = datetime_utc_now
        form_data = {
            'phone': form.phone.data,
            'model': form.model.data,
            'info': form.info.data,
            'user_id': current_user.id,
            'offered_price': form.offered_price.data,
            'created_date': created_date,
            'status': 'приет за ремонт',
            'device_type': form.device_type.data,
            'pincode' : form.pincode.data,
            'passcode' : form.passcode.data,
            'other_info' : form.other_info.data,
            'status_order_filter' : '1'
        }
        result = mongo.db.forms.insert_one(form_data)

        flash('Form submitted successfully', 'success')

        # Redirect to the submitted form page
        return redirect(url_for('submitted_form', form_id=str(result.inserted_id)))

    return render_template('form.html', form=form)

@app.route('/update-order-status/<form_id>')
def update_order_status(form_id):

    update_data = {
        'status': 'готов за получаване',
        'status_order_filter' : '2',

    }
    mongo.db.forms_collection.update_one({'_id': ObjectId(form_id)}, {'$set': update_data})
    print(update_data)
    return redirect(url_for('view_forms'))

@app.route('/edit-form/<form_id>', methods=['GET', 'POST'])
def edit_form(form_id):
    form_data = mongo.db.forms_collection.find_one({'_id': ObjectId(form_id)})

    if form_data:
        technician = form_data.get('technician', '')
        # Initialize the form without passing obj=form_data
        form = MyForm()

        # Manually set form fields' data if it's a GET request
        if request.method == 'GET':

            form.phone.data = form_data.get('phone', '')
            form.model.data = form_data.get('model', '')
            form.info.data = form_data.get('info', '')
            form.offered_price.data = form_data.get('offered_price', '')
            form.device_type.data = form_data.get('device_type', '')
            form.passcode.data = form_data.get('passcode','')
            form.other_info.data = form_data.get('other_info','')
            form.pincode.data = form_data.get('pincode','')
            form.created_date.data = form_data.get('created_date','')
            form.status.data = form_data.get('status','')
            form.part_price.data = form_data.get('part_price','')
            form.warranty.data = form_data.get('warranty', '')
            form.repair_details.data = form_data.get('repair_details', '')
            accessories = form_data.get('accessories', {})
            form.repaired_date.data = form_data.get('repaired_date', '')
            form.technician.data = form_data.get('technician', '')
            for accessory_key, is_checked in accessories.items():
                setattr(form, accessory_key, is_checked)  #
            print(form.data)
        # Simple if statement to check the validation erros
        if request.method == 'POST':
            if form.validate():
                pass
            else:
                app.logger.debug('Form errors: %s', form.errors)
        if request.method == 'POST' and form.validate_on_submit():

            #get the current order status
            status = request.form.get('status')
            status_order_filter = request.form.get('status_order_filter','')

            # logic to handle status orders in order to make easy sorting on view_forms
            if status == "приключен ремонт":
                status_order_filter = "3"
            elif status == "готов за получаване":
                status_order_filter = "2"
            elif status == "приет за ремонт":
                status_order_filter = "1"
            update_data = {'status': status, 'status_order_filter': status_order_filter }
            print('update data' + str(update_data))

            # Check if the status is "completed" and update additional fields
            if status == 'приключен ремонт' or status == "готов за получаване":
                print('vytre sym')
                update_data = {
                    'part_price': request.form.get('part_price'),
                    'warranty': request.form.get('warranty'),
                    'repair_details' :request.form.get('repair_details'),
                    'status_order_filter':status_order_filter
                }
                mongo.db.forms_collection.update_one({'_id': ObjectId(form_id)}, {'$set': update_data})
                print(update_data)
            # Logic to check if repaired_date exist, and put in database only if it's missing.
            repaired_date = check_if_repaired_date_exist(form_id)
            if status == 'приключен ремонт' and repaired_date is None:

                datetime_utc_now = datetime.now()
                repaired_date = datetime.now()
                update_data = {
                    'repaired_date':repaired_date
                }
                mongo.db.forms_collection.update_one({'_id': ObjectId(form_id)}, {'$set': update_data})
                print(repaired_date)

           # if status == 'приключен ремонт' and not technician:
            #    flash('Please select a technician for completed repairs.', 'error')
            #    return redirect(url_for('edit_form', form_id=form_id))
            checkboxes = ['accessory_case', 'accessory_bag', 'accessory_charger',
                          'accessory_sim']  # Replace these with your actual checkbox names
            accessories = {checkbox: checkbox in request.form for checkbox in checkboxes}
            update_data = {
                'phone': form.phone.data,
                'model': form.model.data,
                'info': form.info.data,
                'offered_price': form.offered_price.data,
                'device_type' : form.device_type.data,
                'passcode' : form.passcode.data,
                'pincode': form.pincode.data,
                'other_info': form.other_info.data,
                'accessories': accessories,
                'status': request.form.get('status'),
                'status_order_filter': status_order_filter,
                'technician': request.form.get('technician')
                # Add any other fields you have in your form
            }
            print(update_data)
            mongo.db.forms_collection.update_one({'_id': ObjectId(form_id)}, {'$set': update_data})
            flash('Form updated successfully!')
            return redirect(url_for('view_forms'))

        return render_template('edit_form.html', form=form, technician=technician,form_id=form_id,accessories=accessories)
    else:
        flash('Form not found!')
        return redirect(url_for('view_forms'))

#  delete entry functionality on view_form
@app.route('/delete-form/<form_id>')
def delete_form(form_id):
    mongo.db.forms_collection.delete_one({'_id': ObjectId(form_id)})
    flash('Entry deleted successfully')
    return redirect(url_for('view_forms'))

@app.route('/search-forms', methods=['GET', 'POST'])
def search_forms():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search_query = {"$or": [
        {"order_number": {"$regex": query, "$options": "i"}},
        {"phone": {"$regex": query, "$options": "i"}},
        {"device_type": {"$regex": query, "$options": "i"}},
        {"model": {"$regex": query, "$options": "i"}},
        {"offered_price": {"$regex": query, "$options": "i"}},
        {"status": {"$regex": query, "$options": "i"}},
        # Add other fields you want to search by
    ]}
    total_count = mongo.db.forms_collection.count_documents(search_query)
    total_pages = (total_count + per_page - 1) // per_page
    search_results = mongo.db.forms_collection.find(search_query).skip((page - 1) * per_page).limit(per_page)
    search_results = list(search_results)

    return render_template('view_forms.html', forms=search_results, page=page, total_pages=total_pages, query=query)


# Logic for generating reports
@app.route('/reports', methods=['GET'])
@login_required
def reports():
    start_date_str = request.args.get('start_date')  # Get start date from query parameters
    end_date_str = request.args.get('end_date')      # Get end date from query parameters
    technician_filter = request.args.get('technician')
    page = int(request.args.get('page', 1))  # Get the current page number, default to 1
    limit = 15  # Number of items per page

    # Default values if no dates are provided
    start_date = datetime.min
    end_date = datetime.max

    # Parse the dates if provided
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to 00:00:00
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)  # Set time to 23:59:59

    # MongoDB query to filter by repaired_date within the range and status
    query = {
        'repaired_date': {
            '$gte': start_date,
            '$lte': end_date
        },
        'status': 'приключен ремонт'  # Filter by status
    }
    if technician_filter:
        query['technician'] = technician_filter  # Filter by technician if provided
    # Skip and limit logic for pagination
    skip = (page - 1) * limit
    total_orders_count = mongo.db.forms_collection.count_documents(query)  # Total count of items
    orders = (
        mongo.db.forms_collection.find(query)
        .sort('repaired_date', 1)
        .skip(skip)
        .limit(limit)
    )

    # Calculate the report data
    report_data = []
    total_offered_price = 0
    total_part_price = 0
    total_difference = 0

    for order in orders:
        offered_price = float(order.get('offered_price', 0) or 0)
        part_price = float(order.get('part_price', 0) or 0)
        difference = offered_price - part_price

        repaired_date_raw = order.get('repaired_date')  # Assuming this is a datetime object
        repaired_date = repaired_date_raw.strftime('%Y-%m-%d') if repaired_date_raw else ''

        report_data.append({
            'model': order.get('model'),
            'info': order.get('info'),
            'offered_price': offered_price,
            'part_price': part_price,
            'difference': difference,
            'repaired_date': repaired_date,
            'technician': order.get('technician', '')
        })

        # Accumulate totals for summary
    all_orders = list(mongo.db.forms_collection.find(query))  # Convert cursor to a list

    def safe_float(value):
        """
        Safely convert a value to a float. If the value is None, empty, or invalid, return 0.0.
        """
        try:
            return float(value) if value and str(value).strip() else 0.0
        except (ValueError, TypeError):
            return 0.0

    total_offered_price = sum(safe_float(order.get('offered_price')) for order in all_orders)
    total_part_price = sum(safe_float(order.get('part_price')) for order in all_orders)

    #print(f"Total Part Price: {total_part_price}")
    #print(f"Total Offered Price: {total_offered_price}")

    total_difference = total_offered_price - total_part_price
    # Create summary data
    summary_data = {
        'total_orders': total_orders_count,
        'total_difference': total_difference,
        'total_part_price': total_part_price
    }

    # Calculate total pages
    total_pages = (total_orders_count + limit - 1) // limit
    technicians = ['Ники', 'Лъчо', 'Десо','Митко Гарата','Митко PS','Боби', 'Impulse', 'Други']

    return render_template(
        'reports.html',
        report_data=report_data,
        summary_data=summary_data,
        current_page=page,
        total_pages=total_pages,
        technicians=technicians,  # Pass technician filter options to the template
        technician_filter=technician_filter
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
