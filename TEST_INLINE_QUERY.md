# 🧪 Testing Inline Query Menu - Step by Step Guide

## ✅ **Prequisites Checklist**

Before testing, ensure these are done:

### **1. Enable Inline Mode in BotFather** ⚠️ **CRITICAL**

1. Open Telegram → Search for `@BotFather`
2. Send: `/setinline`
3. Select: `taxoin_bot`
4. Set placeholder: `Telega2Go Menu` (or any text)
5. BotFather will confirm: "Success! Inline mode is now enabled."

**Without this, inline queries will NOT work!**

### **2. Verify Webhook is Configured**

```bash
# Get webhook info (replace with your bot token)
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**Expected:**
```json
{
  "ok": true,
  "result": {
    "url": "https://your-domain.com/otp/webhook",
    "pending_update_count": 0
  }
}
```

### **3. Verify OTP Gateway is Running**

```bash
# Check container
docker ps | grep otp-gateway

# Check health
curl http://localhost:55551/health
```

---

## 🧪 **Testing Methods**

### **Method 1: Test in Telegram (REAL TEST)**

**This is the only way to really test it!**

1. **Open any Telegram chat** (group, private, or channel)
2. **Type**: `@taxoin_bot` (start typing and select from suggestions)
3. **Wait 1-2 seconds** - Menu should appear automatically
4. **You should see** 4 options:
   - 👥 Join To Me
   - 📖 Explain What Is This
   - 💰 What Is My Balance
   - 📋 Show Last Actions

**If menu doesn't appear:**
- Check Step 1: Is inline mode enabled?
- Check webhook is receiving updates
- Check logs: `docker logs telega2go-otp-gateway -f`

### **Method 2: Monitor Webhook Logs**

```bash
# Watch for incoming inline queries
docker logs telega2go-otp-gateway -f | grep -i "inline\|query"
```

Then try typing `@taxoin_bot` in Telegram. You should see log entries.

### **Method 3: Test Webhook Endpoint**

```bash
# Test if webhook accepts inline queries (will fail with fake ID, but tests format)
python3 test_inline_query.py
```

**Note:** This will show "400 Bad Request" because we use a fake query ID, but it confirms:
- ✅ Webhook endpoint is working
- ✅ Code is processing inline queries
- ✅ Format is correct (after our fix)

---

## 🔍 **Troubleshooting**

### **Issue: Menu Doesn't Appear When Typing @taxoin_bot**

**Checklist:**
1. ✅ **Inline mode enabled?** Go to BotFather → `/mybots` → Select `taxoin_bot` → Bot Settings → Inline Mode → Should show "Enabled"
2. ✅ **Webhook configured?** Check webhook URL is correct
3. ✅ **OTP Gateway running?** `docker ps | grep otp-gateway`
4. ✅ **Bot username correct?** Type exactly `@taxoin_bot` (case-sensitive)
5. ✅ **Wait for suggestions?** Type `@tax` and wait for Telegram to suggest bot names

### **Issue: Menu Appears But Shows Empty**

- Check logs for errors: `docker logs telega2go-otp-gateway -f`
- Verify bot token is correct in environment

### **Issue: Buttons Don't Work**

- Check callback query handler is working
- Check logs when clicking buttons
- Verify webhook is receiving callback queries

---

## 📊 **Verification Commands**

```bash
# 1. Check OTP Gateway health
curl http://localhost:55551/health

# 2. Check webhook endpoint exists
curl -X POST http://localhost:55551/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id":1}'

# 3. Check webhook from Telegram side
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# 4. Check if inline mode is enabled (via BotFather)
# Send /mybots in BotFather → Select taxoin_bot → Check settings
```

---

## ✅ **Success Indicators**

When working correctly:
- ✅ Typing `@taxoin_bot` shows 4 menu options instantly
- ✅ Selecting an option sends message with button
- ✅ Clicking button posts response in chat
- ✅ Logs show successful inline query handling
- ✅ No errors in `docker logs telega2go-otp-gateway`

---

## 🎯 **Next Steps**

1. **Enable inline mode** in BotFather (if not done)
2. **Test in Telegram** by typing `@taxoin_bot`
3. **Check logs** if it doesn't work: `docker logs telega2go-otp-gateway -f`
4. **Report results** so we can debug further if needed

