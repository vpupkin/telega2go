# 🚨 NEXT STEPS TODO - Telegram ID Resolution (PENALTY MODE)

**Date**: 2025-11-01  
**Status**: 🔴 **PENALTY - CRITICAL FIX REQUIRED**  
**Priority**: **HIGHEST**

---

## 📋 **REQUIREMENTS (CORRECT LOGIC)**

### **1. WRONG Error Message ❌**
```
❌ WRONG: "telegram_chat_id is required for OTP delivery when using username. Please provide Chat ID in the form."
```
This error should NEVER appear. Backend should resolve username → chatID automatically.

### **2. Form With UserID → No ChatID Required ✅**
- User enters **only** `@username` (userID)
- Backend resolves `@username` → `chatID` via Telegram API
- Form should NOT ask for chatID when username is selected

### **3. Form With ChatID → No UserID Required ✅**
- User enters **only** `chatID`
- Backend resolves `chatID` → `@username` via Telegram API
- Form should NOT ask for userID when chatID is selected

### **4. Backend Can Resolve ChatID from UserID ✅**
- Telegram Bot API: `getChat` with `@username` → returns `chatID`
- Implementation required in backend
- Use `TELEGRAM_BOT_TOKEN` to query Telegram API

### **5. Backend Can Resolve UserID from ChatID ✅**
- Telegram Bot API: `getChatMember` with `chatID` → returns user info including `@username`
- Implementation required in backend
- Use `TELEGRAM_BOT_TOKEN` to query Telegram API

### **6. Database Stores BOTH ChatID and UserID ✅**
- `User` model should have both fields:
  - `telegram_chat_id: str`
  - `telegram_username: str`
- Both should be persisted after resolution
- Both available for future lookups

### **7. Form NEVER Asks for BOTH ❌**
- **CRITICAL**: Form should show EITHER:
  - `@username` field (toggle: Username)
  - `chatID` field (toggle: Chat ID)
- **NEVER** show both fields at the same time
- Toggle switches between the two options

### **8. Tests Must Cover All Cases ✅**
- Test: Username only → Backend resolves chatID
- Test: ChatID only → Backend resolves username
- Test: Both provided → Error (form should prevent this)
- Test: Neither provided → Error
- Test: Resolution fails → Graceful error handling
- Test: Database stores both after resolution

---

## 🔧 **IMPLEMENTATION PLAN**

### **Phase 1: Backend Resolution Logic**
1. Create `resolve_telegram_ids()` function:
   - Input: `chat_id` OR `username` (one or the other)
   - Output: `{"chat_id": "...", "username": "..."}` (both)
   - Uses Telegram Bot API:
     - `getChat(chat_id)` → get username
     - `getChatMember(chat_id, user_id)` → get user info
     - `getChat("@username")` → get chat_id
   - Error handling for invalid IDs

2. Update `POST /api/register`:
   - Accept EITHER `chat_id` OR `username`
   - Call `resolve_telegram_ids()` to get the missing one
   - Store BOTH in database
   - Use `chat_id` for OTP delivery

### **Phase 2: Frontend Toggle Restoration**
1. Restore username toggle:
   - Two buttons: "Username" / "Chat ID"
   - Show only ONE input field at a time
   - Based on toggle selection
   - Send only the selected identifier

2. Remove wrong error messages
3. Update validation to allow either

### **Phase 3: Database Schema**
1. Ensure `User` model has:
   - `telegram_chat_id: Optional[str]`
   - `telegram_username: Optional[str]`
2. Both fields populated after registration
3. Both fields available for lookups

### **Phase 4: Comprehensive Tests**
1. `test_username_resolution.py`:
   - Username → chatID resolution
   - OTP delivery with resolved chatID
   - Database stores both

2. `test_chatid_resolution.py`:
   - ChatID → username resolution
   - Database stores both

3. `test_both_provided_error.py`:
   - Form should prevent both
   - Backend should reject both

4. `test_resolution_failures.py`:
   - Invalid username handling
   - Invalid chatID handling
   - API errors

---

## 📋 **API ENDPOINTS NEEDED**

### **Telegram Bot API Calls**

1. **Get Chat by Username:**
   ```
   GET https://api.telegram.org/bot{TOKEN}/getChat?chat_id=@username
   Returns: {"ok": true, "result": {"id": 123456789, ...}}
   ```

2. **Get Chat Member:**
   ```
   GET https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat_id}&user_id={chat_id}
   Returns: {"ok": true, "result": {"user": {"username": "@username", ...}}}
   ```

3. **Get Me (Bot Info):**
   ```
   GET https://api.telegram.org/bot{TOKEN}/getMe
   Returns: Bot information
   ```

---

## ✅ **ACCEPTANCE CRITERIA**

- [ ] Form shows toggle: Username / Chat ID
- [ ] Only ONE field shown at a time
- [ ] Backend resolves missing ID via Telegram API
- [ ] Database stores BOTH chatID and userID
- [ ] OTP delivery works with resolved chatID
- [ ] Error message "chat_id required for OTP" NEVER appears
- [ ] Tests cover all resolution cases
- [ ] Tests cover both input scenarios (username-only, chatID-only)
- [ ] Tests verify database stores both IDs

---

## 🚨 **CRITICAL NOTES**

1. **NEVER** show both fields in form
2. **NEVER** require both from user
3. **ALWAYS** resolve missing ID via Telegram API
4. **ALWAYS** store both IDs in database
5. **ALWAYS** handle resolution failures gracefully

---

**Status**: 🔴 **PENALTY MODE - FIX REQUIRED IMMEDIATELY**

