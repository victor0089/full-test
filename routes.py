# routes.py

# ...

from flask import Response
import io
from flask import make_response
from openpyxl import Workbook
from sqlalchemy import func
from datetime import datetime
from flask import current_app
import pandas as pd
from sqlalchemy import create_engine
from flask import request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import plotly.express as px
from flask import render_template


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
# ...

from flask_login import login_user, logout_user, login_required

# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

# ...

from flask_login import current_user, login_user, logout_user, login_required

# ...

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

# ...

@app.route('/update_password/<int:user_id>', methods=['POST'])
@login_required
def update_password(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdatePasswordForm()

    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password updated successfully', 'success')
        else:
            flash('Incorrect old password. Please try again.', 'danger')

    return redirect(url_for('user_profile', user_id=user_id))
#...

class DeleteAccountForm(FlaskForm):
    confirm_delete = StringField('Type "DELETE" to confirm', validators=[DataRequired(), EqualTo('delete')])
    delete = HiddenField()
    submit = SubmitField('Delete Account')

# ...

@app.route('/delete_account/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_account(user_id):
    user = User.query.get_or_404(user_id)
    form = DeleteAccountForm()

    if form.validate_on_submit():
        if form.confirm_delete.data == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            logout_user()
            flash('Your account has been successfully deleted.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Account deletion confirmation did not match. Please try again.', 'danger')

# ...

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    # ... (existing code)

    # Retrieve user-specific data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = f"SELECT * FROM data WHERE user_id = {user_id}"
    user_data = pd.read_sql(query, con=db.engine)
    
    user_data = user_data.sort_values(by='date', ascending=False).reset_index(drop=True)
    user_data = user_data.iloc[(page-1)*per_page:page*per_page]

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data, form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents, search_query=search_query, start_date=start_date, end_date=end_date, excel_data=excel_io.getvalue())
# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    # ... (existing code)

    # Retrieve user-specific data with pagination and search
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')

    query = f"SELECT * FROM data WHERE user_id = {user_id}"

    if search_query:
        query += f" AND (product LIKE '%{search_query}%' OR date LIKE '%{search_query}%')"

    user_data = pd.read_sql(query, con=db.engine)
    
    user_data = user_data.sort_values(by='date', ascending=False).reset_index(drop=True)
    user_data = user_data.iloc[(page-1)*per_page:page*per_page]

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data, form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents, search_query=search_query, start_date=start_date, end_date=end_date, excel_data=excel_io.getvalue())

# ...

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    # ... (existing code)

    # Retrieve user-specific data with pagination, search, and date filtering
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = f"SELECT * FROM data WHERE user_id = {user_id}"

    if search_query:
        query += f" AND (product LIKE '%{search_query}%' OR date LIKE '%{search_query}%')"

    if start_date and end_date:
        query += f" AND date BETWEEN '{start_date}' AND '{end_date}'"

    user_data = pd.read_sql(query, con=db.engine)
    
    user_data = user_data.sort_values(by='date', ascending=False).reset_index(drop=True)
    user_data = user_data.iloc[(page-1)*per_page:page*per_page]

    # ... (existing code)

    return render_template('user_profile.html', user=user, user_data=user_data, form=form, chart=img_data, file_upload_form=file_upload_form, uploaded_photos=uploaded_photos, uploaded_documents=uploaded_documents, search_query=search_query, start_date=start_date, end_date=end_date, excel_data=excel_io.getvalue())
# ...

@app.route('/export_excel/<int:user_id>', methods=['POST'])
@login_required
def export_excel(user_id):
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id}", con=db.engine)

    # Create an in-memory Excel file
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine='xlsxwriter') as writer:
        user_data.to_excel(writer, index=False, sheet_name='Sales Data')

    # Set up response headers
    response = make_response(excel_io.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=sales_data.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response
# ...

@app.route('/sales_chart/<int:user_id>', methods=['GET'])
@login_required
def sales_chart(user_id):
    user_data = pd.read_sql(f"SELECT * FROM data WHERE user_id = {user_id}", con=db.engine)

    # Group sales data by date and calculate total sales for each date
    sales_by_date = user_data.groupby('date')['amount'].sum().reset_index()

    # Create an interactive line chart using Plotly
    fig = px.line(sales_by_date, x='date', y='amount', title='Sales Over Time', labels={'amount': 'Total Sales'}, line_shape='linear')

    # Set chart layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Total Sales',
        hovermode='x unified',
    )

    # Convert the chart to HTML
    chart_html = fig.to_html(full_html=False)

    return render_template('sales_chart.html', chart_html=chart_html)
# ...

# Define the allowed file extensions and the upload folder
ALLOWED_EXTENSIONS = {'xlsx'}
UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file/<int:user_id>', methods=['GET', 'POST'])
@login_required
def upload_file(user_id):
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        # Check if the file has the allowed extension
        if file and allowed_file(file.filename):
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the uploaded file (e.g., read Excel data, update database)
            process_uploaded_file(file_path, user_id)

            flash('File successfully uploaded and processed', 'success')
            return redirect(url_for('user_profile', user_id=user_id))

    return render_template('upload_file.html')
# ...---------------------------

def process_uploaded_file(file_path, user_id):
    # Read the Excel file
    excel_data = pd.read_excel(file_path)

    # Update the database with the sales and payment data
    update_database(excel_data, user_id)

    # Remove the uploaded file after processing
    os.remove(file_path)

def update_database(excel_data, user_id):
    # Update the database with the sales and payment data
    # (Implement your database update logic here)
    pass

# ...--------------------

def process_uploaded_file(file_path, user_id):
    try:
        # Read the Excel file
        excel_data = pd.read_excel(file_path)

        # Update the database with the sales and payment data
        update_database(excel_data, user_id)

        flash('File successfully uploaded and processed', 'success')
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')

    # Remove the uploaded file after processing
    os.remove(file_path)

# ...
# ...

@app.route('/upload_history/<int:user_id>', methods=['GET'])
@login_required
def upload_history(user_id):
    # Retrieve upload history for the user
    history = get_upload_history(user_id)

    return render_template('upload_history.html', user_id=user_id, history=history)
# ...

def process_uploaded_file(file_path, user_id):
    try:
        # Read the Excel file
        excel_data = pd.read_excel(file_path)

        # Update the database with the sales and payment data
        update_database(excel_data, user_id)

        # Log the upload
        log_upload(file_path, user_id)

        flash('File successfully uploaded and processed', 'success')
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')

    # Remove the uploaded file after processing
    os.remove(file_path)

# ...

def log_upload(file_path, user_id):
    file_name = os.path.basename(file_path)
    date_uploaded = datetime.now()

    # Log the upload in the database (Implement your database logic here)
    # For demonstration purposes, we'll print the details
    print(f"User {user_id} uploaded file '{file_name}' on {date_uploaded}")
@app.route('/delete_upload/<int:user_id>/<string:file_name>', methods=['POST'])
@login_required
def delete_upload(user_id, file_name):
    # Delete the file from the server
    delete_file(file_name)

    # Log the deletion
    log_deletion(file_name, user_id)

    flash('File successfully deleted', 'success')

    # Redirect back to the upload history page
    return redirect(url_for('upload_history', user_id=user_id))

# ...

def delete_file(file_name):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    # Delete the file from the server
    if os.path.exists(file_path):
        os.remove(file_path)

# ...

def log_deletion(file_name, user_id):
    date_deleted = datetime.now()

    # Log the deletion in the database (Implement your database logic here)
    # For demonstration purposes, we'll print the details
    print(f"User {user_id} deleted file '{file_name}' on {date_deleted}")
# ...

@app.route('/sales_summary/<int:user_id>', methods=['GET'])
@login_required
def sales_summary(user_id):
    # Retrieve sales summary for the user
    summary = get_sales_summary(user_id)

    return render_template('sales_summary.html', user_id=user_id, summary=summary)
# ...

def get_sales_summary(user_id):
    # Get the total revenue for the user
    total_revenue = db.session.query(func.sum(Data.amount)).filter_by(user_id=user_id).scalar()

    # Get the most sold product for the user
    most_sold_product = db.session.query(Data.product, func.sum(Data.amount)).filter_by(user_id=user_id).group_by(Data.product).order_by(func.sum(Data.amount).desc()).first()

    return {'total_revenue': total_revenue, 'most_sold_product': most_sold_product[0] if most_sold_product else None}
# ...

def get_filtered_sales(user_id, category, start_date, end_date):
    # Build the base query
    query = db.session.query(Data).filter_by(user_id=user_id)

    # Apply filters
    if category:
        query = query.filter_by(product_category=category)

    if start_date:
        query = query.filter(Data.date >= start_date)

    if end_date:
        query = query.filter(Data.date <= end_date)

    # Retrieve the filtered sales data
    filtered_data = query.all()

    return filtered_data
# ...

@app.route('/user_profile/<int:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    # ... (existing code)

    # Paginate the sales data
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjust the number of items per page as needed
    user_data = Data.query.filter_by(user_id=user_id).paginate(page, per_page, error_out=False)

    return render_template('user_profile.html', user=user, user_data=user_data, search_query=search_query,
                           start_date=start_date, end_date=end_date)

# ...
# ...

@app.route('/export_filtered_excel/<int:user_id>/<string:category>/<string:start_date>/<string:end_date>', methods=['POST'])
@login_required
def export_filtered_excel(user_id, category, start_date, end_date):
    # Retrieve the filtered sales data
    filtered_data = get_filtered_sales(user_id, category, start_date, end_date)

    # Create an in-memory Excel workbook
    output = io.BytesIO()
    workbook = Workbook()
    worksheet = workbook.active

    # Add headers to the worksheet
    headers = ['Date', 'Product', 'Amount']
    worksheet.append(headers)

    # Add data rows to the worksheet
    for row in filtered_data:
        worksheet.append([row.date, row.product, row.amount])

    # Save the workbook to the output stream
    workbook.save(output)
    output.seek(0)

    # Create a Flask response with the Excel file
    response = Response(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = f"attachment; filename=filtered_sales_data.xlsx"

    return response
