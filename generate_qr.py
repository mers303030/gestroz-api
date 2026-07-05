import qrcode

url = "https://a1b2c3d4.ngrok.io/static/login.html"  # Remplace par ton URL
img = qrcode.make(url)
img.save("gestroz_qr.png")
print("✅ QR Code mis à jour avec l'URL ngrok")