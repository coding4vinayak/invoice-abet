from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# PostgreSQL configuration with SSL mode
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://avnadmin:{'avion_password'}@pg-17ae6fae-vinayakdb.a.aivencloud.com:28101/defaultdb'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'sslmode': 'require',
        'sslrootcert': 'flask_invoice_app/ca/ca.pem'
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    recipient = db.Column(db.String(200), nullable=False)
    ship_to = db.Column(db.String(200), nullable=False)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)

def generate_pdf(invoice, items, subtotal, sales_tax, shipping_handling, total_due):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    company_name = "Abet Works"
    elements.append(Paragraph(company_name, styles['Title']))
    elements.append(Paragraph(f"Invoice Number: {invoice.invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {invoice.date}", styles['Normal']))
    elements.append(Paragraph(f"Recipient: {invoice.recipient}", styles['Normal']))
    elements.append(Paragraph(f"Ship To: {invoice.ship_to}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in items:
        data.append([item.description, item.quantity, f"${item.unit_price:.2f}", f"${item.total:.2f}"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)

    elements.append(Paragraph(f"<br/>Subtotal: ${subtotal:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Sales Tax: {sales_tax:.2f}%", styles['Normal']))
    elements.append(Paragraph(f"Shipping & Handling: ${shipping_handling:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total Due: ${total_due:.2f}", styles['Normal']))

    doc.build(elements)

    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    data = request.get_json()
    invoice_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    recipient = data['recipient']
    ship_to = data['ship_to']
    sales_tax = float(data['sales_tax'])
    shipping_handling = float(data['shipping_handling'])

    invoice = Invoice(invoice_number=invoice_number, recipient=recipient, ship_to=ship_to)
    db.session.add(invoice)
    db.session.commit()

    subtotal = 0
    items = []
    for item in data['items']:
        description = item['description']
        quantity = int(item['quantity'])
        unit_price = float(item['unit_price'])
        total = quantity * unit_price

        invoice_item = InvoiceItem(description=description, quantity=quantity, unit_price=unit_price, total=total, invoice_id=invoice.id)
        db.session.add(invoice_item)
        items.append(invoice_item)
        subtotal += total

    db.session.commit()

    total_due = subtotal + (subtotal * (sales_tax / 100)) + shipping_handling

    # Generate PDF
    pdf_buffer = generate_pdf(invoice, items, subtotal, sales_tax, shipping_handling, total_due)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'invoice_{invoice.invoice_number}.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
