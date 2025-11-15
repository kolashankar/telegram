"""UPI QR Code Generator"""
import qrcode
import io
from typing import Optional


def generate_upi_qr(upi_id: str, amount: float, name: str = "OTT Subscription", transaction_id: Optional[str] = None) -> bytes:
    """
    Generate UPI QR code for payment
    
    Args:
        upi_id: UPI ID of the payee
        amount: Amount to be paid
        name: Payment description
        transaction_id: Optional transaction ID
    
    Returns:
        bytes: QR code image as bytes
    """
    # Create UPI payment string
    upi_string = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    
    if transaction_id:
        upi_string += f"&tn={transaction_id}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def generate_payment_text(upi_id: str, amount: float, platforms: list) -> str:
    """
    Generate payment instruction text
    
    Args:
        upi_id: UPI ID
        amount: Amount to pay
        platforms: List of platforms
    
    Returns:
        str: Formatted payment instructions
    """
    platforms_text = ", ".join(platforms)
    
    text = f"""
💳 **Payment Details**

**Amount:** ₹{amount}
**Platforms:** {platforms_text}
**UPI ID:** `{upi_id}`

📱 **How to Pay:**
1. Open any UPI app (GPay, PhonePe, Paytm)
2. Scan the QR code above OR use UPI ID
3. Pay ₹{amount}
4. Take a screenshot of payment confirmation
5. Upload the screenshot using the button below

✅ After uploading, admin will verify and activate your subscription within 24 hours.
"""
    return text
