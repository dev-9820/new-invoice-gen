from flask import Flask, send_file, request
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import io


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for now

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    
    # Create a BytesIO buffer to hold the PDF data
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Placeholder: Load and draw the company logo
    logo_path = "logo.jpg"
    try:
        image = Image.open(logo_path)
        pdf.drawInlineImage(logo_path, 30, 750, width=100, height=50)  # Adjust position and size
    except IOError:
        print("Logo not found.")
    
    # Seller Info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(30, 720, f"Sold By: {data['seller']['name']}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(30, 705, f"{data['seller']['address']}")
    pdf.drawString(30, 690, f"{data['seller']['city']}, {data['seller']['state']} - {data['seller']['pincode']}")
    pdf.drawString(30, 675, f"PAN No: {data['seller']['pan_no']}")
    pdf.drawString(30, 660, f"GST Registration No: {data['seller']['gst_no']}")
    
    # Billing Info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(30, 630, "Billing Address:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(30, 615, f"{data['billing']['name']}")
    pdf.drawString(30, 600, f"{data['billing']['address']}")
    pdf.drawString(30, 585, f"{data['billing']['city']}, {data['billing']['state']} - {data['billing']['pincode']}")
    pdf.drawString(30, 570, f"State/UT Code: {data['billing']['state_code']}")
    
    # Shipping Info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(30, 540, "Shipping Address:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(30, 525, f"{data['shipping']['name']}")
    pdf.drawString(30, 510, f"{data['shipping']['address']}")
    pdf.drawString(30, 495, f"{data['shipping']['city']}, {data['shipping']['state']} - {data['shipping']['pincode']}")
    pdf.drawString(30, 480, f"State/UT Code: {data['shipping']['state_code']}")
    
    # Order Info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, 750, f"Order Number: {data['order']['order_no']}")
    pdf.drawString(400, 735, f"Order Date: {data['order']['order_date']}")
    pdf.drawString(400, 720, f"Invoice No: {data['invoice']['invoice_no']}")
    pdf.drawString(400, 705, f"Invoice Date: {data['invoice']['invoice_date']}")
    pdf.drawString(400, 690, f"Reverse Charge: {data['invoice']['reverse_charge']}")

    pdf.setFillColor(colors.lightgrey)
    pdf.rect(20, 440, 550, 30, fill=1, stroke=0)  # Light gray background for header
    pdf.setFillColor(colors.black)
    
    # Table for Items
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(30, 450, "Description")
    pdf.drawString(250, 450, "Unit Price")
    pdf.drawString(350, 450, "Quantity")
    pdf.drawString(400, 450, "Net Amount")
    pdf.drawString(480, 450, "Tax")
    
    
    

    # Draw items
    y = 430
    total = 0
    pdf.setFont("Helvetica", 10)
    for item in data['items']:
        
        pdf.rect(20,470, 550, -15 * (len(item) + 1), stroke=1, fill=0)  # Create border for the table
        unit_price = float(item.get('unit_price', 0))
        quantity = int(item.get('quantity', 1))
        discount = float(item.get('discount', 0))

        tax_rate = float(item.get('tax_rate', 18)) / 100.0
        net_amount = unit_price * quantity 
        tax = net_amount * tax_rate / 100
        total += net_amount + tax
        pdf.drawString(30, y, item['description'])
        pdf.drawString(250, y, f"{item['unit_price']}")
        pdf.drawString(350, y, f"{item['quantity']}")
        pdf.drawString(400, y, f"{net_amount}")
        pdf.drawString(480, y, f"{tax}")
        y -= 20
    
    # Total
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, y, f"Total: {total}")
    
    # Finish up the PDF
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    
    # Return the generated PDF
    return send_file(buffer, as_attachment=True, download_name="invoice.pdf", mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True)
