############################################### Generate QR Code #################################################
import qrcode # pip install qrcode
from io import BytesIO # handle image data in memory
import base64 # Encode the image in a format suitable for web display

def generateCode(
    amount: int ,
    upi_id: str = "mrvivekkumar7171@oksbi",
    currency: str = "INR",
    note: str = "Payment for Samosa",
    recipient_name: str = "Vivek Kumar",
    img_name: str = 'PaymentQRCode.png'
) -> any:
    """
    Generates a QR code from the given amount,upi_id, currency, note, recipient_name and returns it as a base64-encoded image. Also saves the image with the given name.
    
    Parameters:
    - amount (int):         Specify the amount                  (default 100)
    - upi_id (str):         Takes the upi_id to make payment on (default "mrvivekkumar7171@oksbi")
    - currency (str):       Currency                            (default "INR")
    - note (str):           Transaction note (URL encoded)      (default "Payment for Samosa")
    - recipient_name (str): Recipient's name (URL encoded)      (default "Vivek Kumar")
    - img_name (str):       The filename for the QR Code image  (default "QRCode.png")

    Returns:
    str: A base64-encoded string representing the QR code image.
    """

    # Encode spaces in URL
    # mc=1234 → Merchant code (optional, used for business payments)
    upi_url = f'upi://pay?pa={upi_id}&pn={recipient_name.replace(" ", "%20")}&am={amount}&cu={currency}&tn={note.replace(" ", "%20")}'

    # Create and configure QR code
    code = qrcode.QRCode( # Create a QRCode object with specific settings
        version=1, # Controls the size of the QR code (higher number = larger QR code)
        box_size=10, # Size of each individual box in the QR code
        border=4 # Border thickness (minimum is 4 for readability)
    )
    code.add_data(upi_url) # Add the provided text data to the QR code
    code.make(fit=True) # Adjusts the QR code size to fit the data

    # Generate QR code image
    img = code.make_image(fill_color='#3bc18e', back_color='#252830') # Generate the QR code image

    # Save the image with the provided filename
    # img.save(img_name, format="PNG")

    # Convert the image to base64
    buffer = BytesIO() # Save the image to an in-memory buffer
    img.save(buffer, format="PNG")
    qrCode = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" # Convert the image to a base64 string for embedding in HTML

    return qrCode # Return the encoded QR code image

if __name__ == "__main__":
    generateCode(150, img_name="PaymentQR.png")