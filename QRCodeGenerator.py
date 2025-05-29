import qrcode

product_id = 7
qr_data = f"product:{product_id}"  # This will embed "product:7" in the QR
img = qrcode.make(qr_data)         # Create QR code image
img.save("product_7_qr.png")       # Save it to file
