# 🔐 OTP Social Gateway

A **production-ready, lightweight REST microservice** for sending One-Time Passwords (OTPs) via **Telegram Bot API** with **self-destructing messages**.

## ✨ Features

- 📨 Send OTPs via Telegram with REST API
- ⏱️ **Auto-delete messages** after 5–60 seconds
- 🚦 Built-in rate limiting (5 OTPs/user/hour)
- 🔒 Zero persistence - OTPs never stored
- 📊 Prometheus metrics endpoint
- 🏥 Health check endpoint
- 🐳 Docker-ready with multi-stage build (<100 MB)
- 📚 Auto-generated OpenAPI documentation
- 🛡️ Input validation & security best practices

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Telegram Bot Token (see setup below)

### 1️⃣ Create Telegram Bot

**Step-by-step guide to create your bot:**

1. **Open Telegram** and search for **@BotFather** (official bot for creating bots)

2. **Start conversation** with BotFather by clicking **START**

3. **Create new bot** by sending:
   ```
   /newbot
   ```

4. **Choose bot name** (display name):
   ```
   My OTP Gateway Bot
   ```

5. **Choose bot username** (must end in 'bot'):
   ```
   my_otp_gateway_bot
   ```

6. **Copy the bot token** - BotFather will respond with:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/my_otp_gateway_bot.
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

7. **Save this token** - you'll need it for `TELEGRAM_BOT_TOKEN`

**Optional: Customize your bot**
- Set description: `/setdescription`
- Set profile picture: `/setuserpic`
- Set about text: `/setabouttext`

---

### 2️⃣ Get User Chat ID

To send OTPs to a user, you need their **chat_id**.

**Method 1: Using your bot**

1. User searches for your bot in Telegram (e.g., `@my_otp_gateway_bot`)
2. User clicks **START** or sends any message
3. Get updates from Telegram API:
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Look for `"chat":{"id":123456789}` in the response

**Method 2: Using @userinfobot**

1. User opens Telegram and searches for **@userinfobot**
2. Clicks **START**
3. Bot responds with: `Id: 123456789`

**Method 3: Using @get_id_bot**

1. Search for **@get_id_bot** in Telegram
2. Send `/start`
3. Bot replies with your chat ID

---

### 3️⃣ Setup & Run

**Clone/Download this repository:**
```bash
cd otp-social-gateway
```

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env` and add your bot token:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5
PORT=55155
```

**Build and run with Docker Compose:**
```bash
docker-compose up --build
```

**Verify it's running:**
```bash
curl http://localhost:55155/health
```

**Expected response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-28T12:00:00.000Z",
  "version": "1.0.0"
}
```

---

## 📖 API Usage

### Send OTP

**Endpoint:** `POST /send-otp`

**Request:**
```bash
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "otp": "483920",
    "expire_seconds": 30
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "message_id": 42,
  "sent_at": "2025-10-28T12:00:00.000Z",
  "delete_at": "2025-10-28T12:00:30.000Z",
  "chat_id": "123456789"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Failed to send OTP",
  "details": "Chat not found"
}
```

---

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/send-otp` | POST | Send OTP with auto-delete |
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | OpenAPI documentation (Swagger UI) |
| `/redoc` | GET | ReDoc documentation |
| `/` | GET | API info |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | **Yes** | - | Your Telegram bot token from @BotFather |
| `DEFAULT_EXPIRE_SECONDS` | No | 30 | Default message auto-delete time (5-60) |
| `MIN_EXPIRE_SECONDS` | No | 5 | Minimum allowed expire time |
| `MAX_EXPIRE_SECONDS` | No | 60 | Maximum allowed expire time |
| `RATE_LIMIT_PER_USER` | No | 5 | Max OTPs per user per time window |
| `RATE_LIMIT_WINDOW_HOURS` | No | 1 | Rate limit time window in hours |
| `PORT` | No | 55155 | Server port |
| `HOST` | No | 0.0.0.0 | Server host |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

### Custom Message Template

Modify `app/config.py` to customize the OTP message:

```python
message_template: str = "🔐 Your OTP is: {otp}\n\n⏱ Expires in {sec} seconds."
```

---

## 🔒 Security Features

### Input Validation
- **chat_id**: Must be numeric string (validates Telegram user ID format)
- **otp**: Must be 4-8 digits only
- **expire_seconds**: Must be between 5-60 seconds

### Rate Limiting
- **Per-user limit**: 5 OTPs per hour (configurable)
- **Global limit**: 10 requests/minute per IP
- **In-memory tracking**: No persistent storage

### Data Protection
- **Zero persistence**: OTPs are never stored or logged
- **PII protection**: No personally identifiable information in logs
- **Auto-cleanup**: Messages self-destruct after expiration

### Network Security
- Non-root Docker user
- Minimal attack surface (<100 MB image)
- Health checks for monitoring

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:55155/health
```

### Prometheus Metrics
```bash
curl http://localhost:55155/metrics
```

**Available metrics:**
- `otp_sent_total` - Total OTPs successfully sent
- `otp_failed_total` - Total OTP send failures
- `rate_limit_exceeded_total` - Rate limit violations

### Logs
Structured JSON logs with timestamps:
```bash
docker-compose logs -f otp-gateway
```

---

## 🧪 Testing

### Manual Testing

1. **Start the service:**
   ```bash
   docker-compose up
   ```

2. **Send test OTP:**
   ```bash
   curl -X POST http://localhost:55155/send-otp \
     -H "Content-Type: application/json" \
     -d '{
       "chat_id": "YOUR_CHAT_ID",
       "otp": "123456",
       "expire_seconds": 10
     }'
   ```

3. **Check Telegram** - you should receive the OTP
4. **Wait 10 seconds** - message should auto-delete

### Test Invalid Inputs

**Invalid OTP (too short):**
```bash
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123", "otp": "12"}'
```

**Invalid expire_seconds:**
```bash
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123", "otp": "1234", "expire_seconds": 100}'
```

### Test Rate Limiting

Send 6 OTPs in quick succession to trigger rate limit:
```bash
for i in {1..6}; do
  curl -X POST http://localhost:55155/send-otp \
    -H "Content-Type: application/json" \
    -d '{"chat_id": "123456789", "otp": "123456"}'
  echo ""
done
```

---

## 🛠️ Development

### Local Development (without Docker)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Set environment variables:**
```bash
export TELEGRAM_BOT_TOKEN="your:token:here"
export PORT=55155
```

**Run the server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 55155 --reload
```

**Access documentation:**
- Swagger UI: http://localhost:55155/docs
- ReDoc: http://localhost:55155/redoc

---

## 🐳 Docker Commands

**Build image:**
```bash
docker build -t otp-social-gateway .
```

**Run container:**
```bash
docker run -d \
  --name otp-gateway \
  -p 55155:55155 \
  -e TELEGRAM_BOT_TOKEN="your:token" \
  otp-social-gateway
```

**View logs:**
```bash
docker logs -f otp-gateway
```

**Stop container:**
```bash
docker stop otp-gateway
```

**Remove container:**
```bash
docker rm otp-gateway
```

---

## 🔧 Troubleshooting

### Issue: "Invalid TELEGRAM_BOT_TOKEN"
**Solution:** 
- Verify token is correct (no spaces, complete)
- Check token with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Regenerate token via @BotFather if needed: `/token`

### Issue: "Chat not found"
**Solution:**
- User must start conversation with bot first (click START)
- Verify chat_id is correct (numeric string)
- Test with: `curl https://api.telegram.org/bot<TOKEN>/getUpdates`

### Issue: Rate limit errors
**Solution:**
- Wait for rate limit window to reset
- Increase `RATE_LIMIT_PER_USER` in `.env`
- Check if multiple services share same IP

### Issue: Messages not deleting
**Solution:**
- Bot must have permission to delete messages
- Check bot logs for delete errors
- Verify user hasn't blocked bot

### Issue: Container health check failing
**Solution:**
```bash
# Check container logs
docker logs otp-gateway

# Verify port is accessible
curl http://localhost:55155/health

# Check if bot token is set
docker exec otp-gateway env | grep TELEGRAM
```

---

## 📦 Production Deployment

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  otp-gateway:
    image: otp-social-gateway:latest
    restart: always
    ports:
      - "55155:55155"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:55155/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Environment Best Practices

1. **Never commit `.env` file** - use secrets management
2. **Use Docker secrets** for production:
   ```yaml
   secrets:
     telegram_token:
       external: true
   ```
3. **Enable HTTPS** with reverse proxy (nginx/traefik)
4. **Monitor metrics** with Prometheus + Grafana
5. **Set up alerts** for failed deliveries

### Scaling

- Stateless design allows horizontal scaling
- Use load balancer for multiple instances
- Consider Redis for distributed rate limiting

---

## 🤝 Integration Examples

### Python Client
```python
import requests

def send_otp_to_user(chat_id: str, otp: str):
    response = requests.post(
        "http://localhost:55155/send-otp",
        json={
            "chat_id": chat_id,
            "otp": otp,
            "expire_seconds": 30
        }
    )
    return response.json()
```

### Node.js Client
```javascript
const axios = require('axios');

async function sendOTP(chatId, otp) {
  const response = await axios.post('http://localhost:55155/send-otp', {
    chat_id: chatId,
    otp: otp,
    expire_seconds: 30
  });
  return response.data;
}
```

### cURL Example
```bash
OTP=$(openssl rand -hex 3 | cut -c1-6)
curl -X POST http://localhost:55155/send-otp \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"$CHAT_ID\", \"otp\": \"$OTP\"}"
```

---

## 📝 API Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | OTP sent successfully |
| 400 | Bad Request | Invalid input (chat_id/otp/expire_seconds) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Telegram API error or server issue |

---

## 🔍 Why Telegram?

| Feature | Telegram | Signal | WhatsApp | SMS |
|---------|----------|--------|----------|-----|
| Bot API | ✅ Official | ⚠️ Unofficial | ⚠️ Business only | ✅ Many providers |
| Self-destruct | ✅ 1-60s | ✅ Custom | ❌ 24h+ | ❌ No |
| No phone needed | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Free | ✅ Yes | ✅ Yes | ⚠️ Business fees | ❌ Paid |
| Rate limits | ✅ Generous | ⚠️ Strict | ⚠️ Strict | ⚠️ Expensive |
| Open-source libs | ✅ Many | ⚠️ Few | ❌ Restricted | ✅ Many |

**Verdict:** Telegram offers the best balance of features, cost, and developer experience for OTP delivery.

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Library](https://github.com/python-telegram-bot/python-telegram-bot)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 📄 License

MIT License - feel free to use in your projects!

---

## 🎯 Summary

You now have a **production-ready OTP gateway** that:

✅ Sends OTPs via Telegram with 5-60 second self-destruct  
✅ Validates all inputs and enforces rate limits  
✅ Provides metrics and health checks  
✅ Runs in a secure, minimal Docker container  
✅ Includes comprehensive documentation  
✅ Ready for horizontal scaling  

**Next Steps:**
1. Create your Telegram bot via @BotFather
2. Update `.env` with your bot token
3. Run `docker-compose up`
4. Test with your chat ID
5. Integrate into your application

**Questions or issues?** Check the troubleshooting section or Telegram Bot API documentation.

---

**Built with ❤️ for secure, ephemeral OTP delivery**