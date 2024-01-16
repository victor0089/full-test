from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# app.py

from flask import Flask, render_template, redirect, url_for, flash
from extensions import db, login_manager
from forms import RegistrationForm
from models import User
# ... (other imports)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
login_manager.init_app(app)
# ......

app = Flask(__name__)

# Create an empty DataFrame to store sales data
sales_data = pd.DataFrame(columns=["Date", "Product", "Quantity", "Price"])

@app.route('/')
def index():
    return render_template('index.html', sales_data=sales_data.to_html())

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        df = pd.read_excel(file)
        sales_data.append(df, ignore_index=True)
        return redirect(url_for('index'))
# ...

# Create an empty DataFrame to store sales and payment data
all_data = pd.DataFrame(columns=["Date", "Product", "Quantity", "Price", "Payment"])

@app.route('/')
def index():
    return render_template('index.html', all_data=all_data.to_html())

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        df = pd.read_excel(file)
        all_data = pd.concat([all_data, df], ignore_index=True)
        return redirect(url_for('index'))

# ...
# ...

@app.route('/generate-accounts')
def generate_accounts():
    # Perform calculations to generate accounts
    # For example, summing up payments for each customer or product

    # Dummy example: Sum payment amounts for each product
    account_data = all_data.groupby('Product')['Payment'].sum().reset_index()

    return render_template('accounts.html', account_data=account_data.to_html())

# ...
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

# Define a model for sales and payment data
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    product = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment = db.Column(db.Float, nullable=True)

db.create_all()
# .....
# ...

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        df = pd.read_excel(file)
        df.to_sql('data', con=db.engine, index=False, if_exists='append')
        return redirect(url_for('index'))

# ...

#.....
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define a User class for login management
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# ...

@app.route('/login')
def login():
    # Implement a login route or use a third-party service for authentication
    # For simplicity, create a dummy user
    user = User()
    user.id = 1
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ...
# ...

from flask import flash

# ...

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))

    if file:
        try:
            df = pd.read_excel(file)
            df.to_sql('data', con=db.engine, index=False, if_exists='append')
            flash('File uploaded successfully', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')

    return redirect(url_for('index'))

# ...

# ...

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    product = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment = db.Column(db.Float, nullable=True)

# ...

# ...

from flask_login import current_user

# ...

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))

    if file:
        try:
            df = pd.read_excel(file)
            # Associate data with the current user
            df['user_id'] = current_user.id
            df.to_sql('data', con=db.engine, index=False, if_exists='append')
            flash('File uploaded successfully', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')

    return redirect(url_for('index'))

# ...

# ...

from flask import Response

# ...

@app.route('/download-accounts')
@login_required
def download_accounts():
    # Retrieve user-specific account data
    account_data = pd.read_sql(f"SELECT product, SUM(payment) as total_payment FROM data WHERE user_id = {current_user.id} GROUP BY product", con=db.engine)
    
    # Convert to CSV format
    csv_data = account_data.to_csv(index=False)

    # Create a response with the CSV data
    response = Response(csv_data, mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=account_sheet.csv"

    return response

# ...
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# ...

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Create a new user (you may want to hash the password in a real application)
        user = User()
        user.id = len(users) + 1  # You may want to use a database to manage user data
        user.username = form.username.data
        user.email = form.email.data
        users.append(user)

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ...


# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Create a new user with a hashed password
        user = User()
        user.id = len(users) + 1  # You may want to use a database to manage user data
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)  # Hash the password
        users.append(user)

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ...


# ...

@app.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    # Retrieve user-specific data
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id}", con=db.engine)

    return render_template('user_profile.html', user_data=user_data.to_html())

# ...

# ...

from flask_wtf import FlaskForm

# ...

class UpdateProfileForm(FlaskForm):
    new_username = StringField('New Username', validators=[Length(min=4, max=20)])
    new_email = StringField('New Email', validators=[Email()])
    submit = SubmitField('Update Profile')

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form)

# ...

# ...

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ...


# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form)

# ...
# ...

import plotly.express as px
from io import BytesIO
import base64

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    # Create a simple bar chart
    chart_data = user_data.groupby('Product')['Quantity'].sum().reset_index()
    fig = px.bar(chart_data, x='Product', y='Quantity', title='Product Quantity Chart')

    # Save the chart as an image
    img = BytesIO()
    fig.write_image(img, format='png')
    img_data = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data)

# ...


# ...

from flask_uploads import UploadSet, configure_uploads, IMAGES, DOCUMENTS

# ...

app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/photos'
app.config['UPLOADED_DOCUMENTS_DEST'] = 'uploads/documents'

photos = UploadSet('photos', IMAGES)
documents = UploadSet('documents', DOCUMENTS)
configure_uploads(app, (photos, documents))

# ...

class FileUploadForm(FlaskForm):
    photo = FileField('Upload Photo', validators=[FileAllowed(photos, 'Images only!')])
    document = FileField('Upload Document', validators=[FileAllowed(documents, 'Documents only!')])
    submit = SubmitField('Upload Files')

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()
    file_upload_form = FileUploadForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Handle file uploads
    if file_upload_form.validate_on_submit():
        photo = file_upload_form.photo.data
        document = file_upload_form.document.data

        if photo:
            filename = photos.save(photo)
            flash(f'Photo "{filename}" uploaded successfully', 'success')

        if document:
            filename = documents.save(document)
            flash(f'Document "{filename}" uploaded successfully', 'success')

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data, file_upload_form=file_upload_form)

# ...


# ...

import os

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()
    file_upload_form = FileUploadForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Handle file uploads
    if file_upload_form.validate_on_submit():
        photo = file_upload_form.photo.data
        document = file_upload_form.document.data

        if photo:
            filename = photos.save(photo)
            flash(f'Photo "{filename}" uploaded successfully', 'success')

        if document:
            filename = documents.save(document)
            flash(f'Document "{filename}" uploaded successfully', 'success')

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    # Retrieve uploaded photos and documents
    uploaded_photos = photos.url(user.id) if os.path.exists(photos.path(user.id)) else None
    uploaded_documents = documents.url(user.id) if os.path.exists(documents.path(user.id)) else None

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents)

# ...


# ...

from flask import send_from_directory

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()
    file_upload_form = FileUploadForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Handle file uploads
    if file_upload_form.validate_on_submit():
        photo = file_upload_form.photo.data
        document = file_upload_form.document.data

        if photo:
            filename = photos.save(photo)
            flash(f'Photo "{filename}" uploaded successfully', 'success')

        if document:
            filename = documents.save(document)
            flash(f'Document "{filename}" uploaded successfully', 'success')

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id} LIMIT {per_page} OFFSET {(page - 1) * per_page}", con=db.engine)

    # Retrieve uploaded photos and documents
    uploaded_photos = photos.url(user.id) if os.path.exists(photos.path(user.id)) else None
    uploaded_documents = documents.url(user.id) if os.path.exists(documents.path(user.id)) else None

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents)

@app.route('/delete_photo/<int:user_id>')
@login_required
def delete_photo(user_id):
    user_photos_path = photos.path(user_id)
    if os.path.exists(user_photos_path):
        os.remove(user_photos_path)
        flash('Photo deleted successfully', 'success')
    return redirect(url_for('user_profile', user_id=user_id))

@app.route('/delete_document/<int:user_id>')
@login_required
def delete_document(user_id):
    user_documents_path = documents.path(user_id)
    if os.path.exists(user_documents_path):
        os.remove(user_documents_path)
        flash('Document deleted successfully', 'success')
    return redirect(url_for('user_profile', user_id=user_id))

# ...


# ...

from datetime import datetime

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()
    file_upload_form = FileUploadForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Handle file uploads
    if file_upload_form.validate_on_submit():
        photo = file_upload_form.photo.data
        document = file_upload_form.document.data

        if photo:
            filename = photos.save(photo)
            flash(f'Photo "{filename}" uploaded successfully', 'success')

        if document:
            filename = documents.save(document)
            flash(f'Document "{filename}" uploaded successfully', 'success')

    # Retrieve user-specific data
    search_query = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = f"SELECT * FROM data WHERE user_id = {user_id}"

    if search_query:
        query += f" AND (product LIKE '%{search_query}%' OR date LIKE '%{search_query}%')"

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        query += f" AND date >= '{start_date}'"

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        query += f" AND date <= '{end_date}'"

    user_data = pd.read_sql(query, con=db.engine)

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents, search_query=search_query, start_date=start_date, end_date=end_date)

# ...

# ...

import io

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm()
    file_upload_form = FileUploadForm()

    if form.validate_on_submit():
        user.update_profile(form.new_username.data, form.new_email.data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    # Handle file uploads
    if file_upload_form.validate_on_submit():
        photo = file_upload_form.photo.data
        document = file_upload_form.document.data

        if photo:
            filename = photos.save(photo)
            flash(f'Photo "{filename}" uploaded successfully', 'success')

        if document:
            filename = documents.save(document)
            flash(f'Document "{filename}" uploaded successfully', 'success')

    # Retrieve user-specific data
    search_query = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = f"SELECT * FROM data WHERE user_id = {user_id}"

    if search_query:
        query += f" AND (product LIKE '%{search_query}%' OR date LIKE '%{search_query}%')"

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        query += f" AND date >= '{start_date}'"

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        query += f" AND date <= '{end_date}'"

    user_data = pd.read_sql(query, con=db.engine)

    # ... (existing code)

    # Export filtered sales data to Excel
    excel_data = user_data.to_excel(index=False, sheet_name='Sales Data')
    excel_io = io.BytesIO()
    excel_io.write(excel_data)
    excel_io.seek(0)

    return render_template('user_profile.html', user=user, user_data=user_data.to_html(), form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents, search_query=search_query, start_date=start_date, end_date=end_date, excel_data=excel_io.getvalue())

# ...


# ...

from flask import send_file

# ...

@app.route('/download_excel/<int:user_id>')
@login_required
def download_excel(user_id):
    user = User.query.get_or_404(user_id)

    excel_data = request.args.get('excel_data', '')
    excel_io = io.BytesIO(excel_data)

    return send_file(excel_io, as_attachment=True, download_name=f'{user.username}_sales_data.xlsx')

# ...




if __name__ == '__main__':
    app.run(debug=True)
