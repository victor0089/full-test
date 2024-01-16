# routes.py

# ...

from flask import Response
import io
from openpyxl import Workbook

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
