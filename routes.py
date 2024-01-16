# routes.py

# ...

from flask import Response
import io
from openpyxl import Workbook

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
