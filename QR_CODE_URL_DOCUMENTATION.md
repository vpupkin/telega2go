# 📱 QR Code URL Documentation

**Date**: 2025-11-01  
**Version**: Current Implementation

---

## 🎯 **QR CODE URL FORMAT**

The QR code generated for OTP contains a **magic link URL** with the following format:

```
{magic_link_base_url}/verify-magic-link?token={base64_encoded_token}
```

### **Current Configuration:**

**Base URL:** `https://putana.date/api`  
**Path:** `/verify-magic-link`  
**Token Parameter:** `token`

**Full URL Example:**
```
https://putana.date/api/verify-magic-link?token=dXNlcjEyM0BleGFtcGxlLmNvbToxMjM0NTY6MTcwOTUzNjQyMy4wOmlod3E...
```

---

## 🔧 **IMPLEMENTATION DETAILS**

### **1. Configuration**
**File:** `otp-social-gateway/app/config.py`

```python
magic_link_base_url: str = "https://putana.date/api"
magic_link_secret: str = "your-magic-link-secret-change-in-production"
```

### **2. Magic Link Generation**
**File:** `otp-social-gateway/app/simple_otp_service.py` (lines 135-159)

**Token Contents:**
- Format: `{email}:{otp}:{timestamp}`
- Example: `user123@example.com:123456:1709536423`

**Token Generation Process:**
1. Create token data: `email:otp:timestamp`
2. Generate HMAC signature using `magic_link_secret`
3. Combine: `{token_data}:{base64_signature}`
4. Base64 URL-safe encode the combined string

**Final URL:**
```python
return f"{settings.magic_link_base_url}/verify-magic-link?token={token}"
```

### **3. QR Code Generation**
**File:** `otp-social-gateway/app/simple_otp_service.py` (lines 124-133)

**Process:**
1. Generate magic link URL
2. Create QR code using `qrcode` library
3. Embed the full magic link URL into the QR code
4. Return QR code as PNG image bytes

```python
def _generate_qr_code(self, data: str) -> bytes:
    """Generate QR code as bytes"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)  # ← Full magic link URL goes here
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()
```

---

## 📋 **QR CODE URL BREAKDOWN**

### **Base URL:**
- **Default:** `https://putana.date/api`
- **Source:** `settings.magic_link_base_url` in `otp-social-gateway/app/config.py`
- **Override:** Can be set via environment variable `MAGIC_LINK_BASE_URL`

### **Endpoint Path:**
- **Path:** `/verify-magic-link`
- **Method:** GET
- **Location:** `backend/server.py` - `@api_router.get("/verify-magic-link")`

### **Token Structure:**
- **Format:** Base64 URL-safe encoded string
- **Contains:** 
  1. Email address
  2. OTP code (6 digits)
  3. Unix timestamp
  4. HMAC signature (for security)

### **Token Decoding Example:**
```python
# Decoded token structure:
token_data = "user123@example.com:123456:1709536423"
signature = "base64_hmac_signature"

# Full token (before encoding):
full_token = f"{token_data}:{signature}"
# Then base64 URL-safe encoded
```

---

## 🔐 **SECURITY FEATURES**

1. **HMAC Signature:** Prevents token tampering
2. **Timestamp:** Allows expiration checking
3. **Base64 URL-Safe Encoding:** Safe for URL transmission
4. **Single-Use:** Tokens verified and invalidated after use

---

## 📱 **USER EXPERIENCE**

### **What Users See:**
1. **QR Code Image:** Scannable QR code containing the magic link
2. **OTP Code:** Text display of the OTP (`🔐 Your OTP is: 123456`)
3. **Expiration Time:** How long before the message self-destructs
4. **Clickable Button:** Inline button with link to verify instantly
5. **Instructions:** Text explaining how to use the QR code

### **Telegram Message Format:**
```
[QR CODE IMAGE]

🔐 Your OTP is: 123456

⏱ Expires in 30 seconds.

📱 Scan this QR code with your phone camera for instant verification!

💡 Or tap the button below to verify instantly!

⚠️ This message will self-destruct.

[🔗 Click here to verify] ← Inline button
```

---

## 🔄 **VERIFICATION FLOW**

1. **User scans QR code** → Opens magic link URL
2. **Backend receives request** → `/api/verify-magic-link?token=...`
3. **Token verified** → HMAC signature checked, timestamp validated
4. **User authenticated** → JWT token created
5. **Redirect** → User redirected to dashboard with JWT token

---

## ⚙️ **CONFIGURATION OPTIONS**

### **Environment Variables:**
```bash
MAGIC_LINK_BASE_URL=https://putana.date/api
MAGIC_LINK_SECRET=your-magic-link-secret-change-in-production
```

### **Override in .env:**
```bash
# OTP Gateway .env
MAGIC_LINK_BASE_URL=https://putana.date/api
```

---

## 📍 **CURRENT PRODUCTION URL**

**QR Code Contains:**
```
https://putana.date/api/verify-magic-link?token={base64_token}
```

**Backend Endpoint:**
- **Location:** `backend/server.py`
- **Route:** `GET /api/verify-magic-link`
- **Function:** `verify_magic_link(token: str, request: FastAPIRequest)`

---

## ✅ **SUMMARY**

**QR Code URL Format:**
```
{magic_link_base_url}/verify-magic-link?token={encoded_token}
```

**Current Production:**
```
https://putana.date/api/verify-magic-link?token={base64_encoded_token}
```

**Components:**
- ✅ Base URL: `https://putana.date/api`
- ✅ Endpoint: `/verify-magic-link`
- ✅ Token: Base64 encoded `email:otp:timestamp:signature`
- ✅ QR Code: PNG image containing full URL
- ✅ Security: HMAC signature verification

---

**Status**: ✅ **DOCUMENTED**  
**Location**: OTP Gateway generates QR codes with magic links  
**Verification**: Backend `/api/verify-magic-link` endpoint

