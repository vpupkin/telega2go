# 🚀 Quick Start Guide

## Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow prompts:
   - Bot name: `My OTP Gateway`
   - Bot username: `my_otp_gateway_bot` (must end in 'bot')
4. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Get Your Chat ID (1 minute)

**Method A: Using @userinfobot**
1. Search for `@userinfobot` in Telegram
2. Click START
3. Bot replies with your ID: `123456789`

**Method B: Using your bot**
1. Search for your bot (e.g., `@my_otp_gateway_bot`)
2. Click START
3. Run:
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Look for `\"chat\":{\"id\":123456789}`

## Step 3: Configure & Run (3 minutes)

```bash
cd otp-social-gateway

# Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5
PORT=55155
LOG_LEVEL=INFO
EOF

# Start with Docker
docker-compose up --build

# Or run locally
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 55155
```

## Step 4: Test (1 minute)

```bash
# Health check
curl http://localhost:55155/health

# Send test OTP
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "YOUR_CHAT_ID",
    "otp": "123456",
    "expire_seconds": 30
  }'
```

**Check Telegram** - you should receive the OTP!  
**Wait 30 seconds** - message auto-deletes! 🎉

## Step 5: Integrate (5 minutes)

### Python
```python
import requests

def send_user_otp(chat_id, otp_code):
    response = requests.post(
        'http://localhost:55155/send-otp',
        json={
            'chat_id': chat_id,
            'otp': otp_code,
            'expire_seconds': 30
        }
    )
    return response.json()

# Usage
result = send_user_otp('123456789', '483920')
print(result)
```

### Node.js
```javascript
const axios = require('axios');

async function sendUserOTP(chatId, otpCode) {
  const response = await axios.post('http://localhost:55155/send-otp', {
    chat_id: chatId,
    otp: otpCode,
    expire_seconds: 30
  });
  return response.data;
}

// Usage
sendUserOTP('123456789', '483920').then(console.log);
```

### cURL (for testing)
```bash
# Generate random OTP and send
OTP=$(openssl rand -hex 3 | cut -c1-6)
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"$CHAT_ID\", \"otp\": \"$OTP\"}"
```

## 📚 More Examples

See `examples/` directory:
- `python_client.py` - Full Python client
- `nodejs_client.js` - Full Node.js client  
- `test_api.sh` - Complete test suite

Run them:
```bash
# Python
python examples/python_client.py YOUR_CHAT_ID

# Node.js
node examples/nodejs_client.js YOUR_CHAT_ID

# Test suite
bash examples/test_api.sh YOUR_CHAT_ID
```

## 🔍 Troubleshooting

**Issue: \"Invalid TELEGRAM_BOT_TOKEN\"**
- Verify token in `.env` (no spaces, complete string)
- Test: `curl https://api.telegram.org/bot<TOKEN>/getMe`

**Issue: \"Chat not found\"**
- User must click START on your bot first
- Verify chat_id is correct (use @userinfobot)

**Issue: Service won't start**
- Check logs: `docker-compose logs -f`
- Verify port 55155 is not in use: `lsof -i :55155`

## 📖 Full Documentation

See [README.md](README.md) for:
- Complete API reference
- Security best practices
- Production deployment
- Monitoring & metrics
- Advanced configuration

## 🎯 What You Get

✅ OTP delivery via Telegram in <1 second  
✅ Auto-delete messages (5-60 seconds)  
✅ Rate limiting (5 OTPs/user/hour)  
✅ Input validation & security  
✅ Prometheus metrics  
✅ Production-ready Docker image  

**Total setup time: ~10 minutes** ⏱️

Happy coding! 🚀
