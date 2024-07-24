import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(invoice, items, subtotal, sales_tax, shipping_handling, total_due):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    company_name = "Abet works"
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
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    elements.append(Paragraph(f"<br/>Subtotal: ${subtotal:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Sales Tax: {sales_tax:.2f}%", styles['Normal']))
    elements.append(Paragraph(f"Shipping & Handling: ${shipping_handling:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total Due: ${total_due:.2f}", styles['Normal']))

    doc.build(elements)

    buffer.seek(0)
    return buffer
