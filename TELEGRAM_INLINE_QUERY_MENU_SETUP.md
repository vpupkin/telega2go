# 📱 Telegram Inline Query Menu Setup Guide

**Version**: v2.9.0 - Inline Query Menu Feature  
**Status**: ✅ Fully Implemented  
**Date**: 2025-10-31

---

## 🎯 **OVERVIEW**

The Telegram bot now supports **Inline Query Mode**, allowing users to access an interactive menu by typing `@bot_username` in any Telegram chat. This provides a quick and convenient way to access bot features without starting a private conversation.

---

## ✨ **FEATURES**

### **Menu Actions (4 Options)**
1. **👥 Join To Me** - Connect and join the community
2. **📖 Explain What Is This** - Learn about Telega2Go and its features
3. **💰 What Is My Balance** - Check your account balance
4. **📋 Show Last Actions** - View your recent activity history

### **How It Works**
- User types `@bot_username` in any Telegram chat
- Bot shows interactive menu with 4 options
- User selects an option → Message with button is sent
- User clicks button → Bot posts answer into chat

---

## 🔧 **SETUP INSTRUCTIONS**

### **Step 1: Enable Inline Mode in BotFather**

1. **Open Telegram** and search for `@BotFather`

2. **Send the command**: `/setinline`

3. **Select your bot** from the list: `taxoin_bot`

4. **Set inline placeholder text**:
   ```
   Telega2Go Interactive Menu
   ```
   Or any descriptive text you prefer (e.g., "Tap to see menu options")

5. **Confirm** - BotFather will confirm that inline mode is enabled

### **Step 2: Configure Webhook (If Not Already Done)**

The webhook must be configured to receive Telegram updates. The endpoint is already implemented at `/webhook`.

**Webhook Configuration:**
```bash
# Using curl (replace with your actual webhook URL)
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/otp/webhook"
```

**For Development:**
```bash
# Using ngrok or similar tunneling service
ngrok http 55551

# Then set webhook to ngrok URL
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-ngrok-url.ngrok.io/otp/webhook"
```

### **Step 3: Verify Webhook is Active**

```bash
# Check webhook status
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**Expected Response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://your-domain.com/otp/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## 🧪 **TESTING**

### **Test Inline Query Menu**

1. **Open any Telegram chat** (group or private)

2. **Type your bot username**:
   ```
   @taxoin_bot
   ```

3. **You should see**:
   - A popup menu appears showing 4 options:
     - 👥 Join To Me
     - 📖 Explain What Is This
     - 💰 What Is My Balance
     - 📋 Show Last Actions

4. **Select an option**:
   - Tap one of the menu items
   - A message will be sent to the chat with a button

5. **Click the button**:
   - The bot will post the response into the chat
   - Currently shows placeholder text (ready for implementation)

### **Test in Different Contexts**

- ✅ **In Groups** - Works in any group chat
- ✅ **In Private Chats** - Works when typing bot username
- ✅ **In Channels** - Works when typing bot username
- ✅ **Any Chat** - Universal access

---

## 📋 **TECHNICAL DETAILS**

### **Implementation**

**Files Modified:**
- `otp-social-gateway/app/bot_commands.py` - Added inline query and callback handlers
- `otp-social-gateway/app/main.py` - Updated webhook to handle inline/callback queries

**Key Functions:**

1. **`handle_inline_query()`** - Processes when user types `@bot_username`
   - Receives inline query from Telegram
   - Returns 4 menu options as inline results
   - Each option has emoji, title, description

2. **`handle_callback_query()`** - Processes button clicks
   - Receives callback when user clicks button
   - Posts answer message into chat
   - Currently returns placeholder responses

### **API Endpoints**

- **Webhook Endpoint**: `POST /otp/webhook`
- **Health Check**: `GET /otp/health`

### **Update Types Handled**

1. **`inline_query`** - When user types `@bot_username`
2. **`callback_query`** - When user clicks inline button
3. **`message`** - Regular bot commands (existing functionality)

---

## 🔍 **TROUBLESHOOTING**

### **Issue: Menu Doesn't Appear**

**Solution:**
1. ✅ Verify inline mode is enabled in BotFather
   ```bash
   # Check bot settings
   /mybots → Select bot → Bot Settings → Inline Mode
   ```

2. ✅ Verify webhook is configured and active
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

3. ✅ Check OTP Gateway logs for errors
   ```bash
   docker logs telega2go-otp-gateway -f
   ```

4. ✅ Verify bot username is correct (case-sensitive)
   - Type exactly: `@taxoin_bot` (without spaces)
   - Make sure you're typing the exact username as registered in BotFather

### **Issue: Menu Appears But Buttons Don't Work**

**Solution:**
1. ✅ Check webhook is receiving callback queries
2. ✅ Verify callback query handler is working
3. ✅ Check OTP Gateway container is running
   ```bash
   docker ps | grep otp-gateway
   ```

### **Issue: Webhook Not Receiving Updates**

**Solution:**
1. ✅ Verify webhook URL is correct and accessible
2. ✅ Check SSL certificate if using HTTPS
3. ✅ Verify firewall allows incoming connections
4. ✅ Test webhook endpoint manually
   ```bash
   curl -X POST http://localhost:55551/webhook \
     -H "Content-Type: application/json" \
     -d '{"update_id":1,"inline_query":{"id":"test","from":{"id":123},"query":""}}'
   ```

---

## 📊 **CURRENT STATUS**

### **✅ Implemented**
- Inline query handler
- Callback query handler
- 4 menu actions with emojis
- Button interaction
- Placeholder responses

### **🔜 Ready for Implementation**
- **Join To Me** - Community connection logic
- **Explain What Is This** - System documentation
- **What Is My Balance** - Balance tracking system
- **Show Last Actions** - Action history system

---

## 🎨 **CUSTOMIZATION**

### **Adding New Menu Items**

Edit `otp-social-gateway/app/bot_commands.py`:

```python
menu_actions = [
    {
        "id": "5",
        "title": "🆕 New Action",
        "description": "Description of new action",
        "initial_message": "🆕 <b>New Action</b>\n\nSelect an action:",
        "button_text": "🆕 New Action",
        "callback_data": "action_newAction"
    },
    # ... existing actions
]
```

Then add response handler in `handle_callback_query()`:

```python
responses = {
    "action_newAction": "🆕 Your response text here",
    # ... existing responses
}
```

### **Changing Placeholder Text**

Edit response text in `handle_callback_query()` function:

```python
responses = {
    "action_joinToMe": "👥 <b>Your Custom Text</b>\n\n[Implementation details]",
    # ...
}
```

---

## 📝 **BOTFATHER COMMANDS REFERENCE**

```bash
# Enable inline mode
/setinline

# Disable inline mode
/setinlineoff

# Set inline placeholder
/setinlineplaceholder

# Set inline feedback (show feedback when selected)
/setinlinefeedback

# Check bot settings
/mybots → Select bot → Bot Settings
```

---

## 🔗 **RELATED DOCUMENTATION**

- **Bot Commands**: See `FUNNY_TELEGRAM_BOT_COMMANDS_v2.8.0.md`
- **Development Rules**: See `A_DEVELOPMENT_RULES.md`
- **API Documentation**: See `TECHNICAL_DOCUMENTATION.md`

---

## ✅ **QUICK CHECKLIST**

Before using inline query menu:

- [ ] Inline mode enabled in BotFather (`/setinline`)
- [ ] Webhook configured and active
- [ ] OTP Gateway container running
- [ ] Webhook endpoint accessible
- [ ] Bot token configured in environment
- [ ] Tested with `@taxoin_bot` in Telegram

---

## 🎉 **SUCCESS CRITERIA**

✅ Inline mode enabled in BotFather  
✅ Webhook configured correctly  
✅ Menu appears when typing `@taxoin_bot`  
✅ All 4 menu options visible  
✅ Buttons work and post responses  
✅ Responses appear in chat  

---

**For questions or issues, check the logs:**
```bash
docker logs telega2go-otp-gateway -f
```

**Or check health:**
```bash
curl http://localhost:55551/health
```

---

**Last Updated**: 2025-10-31  
**Version**: v2.9.0

