# 📋 Dynamic Menu Based on Registration Status - Implementation Plan

**Version**: v2.11.0 (Planned)  
**Feature**: Registration-Aware Inline Menu System  
**Status**: 📝 **PLANNING PHASE**

---

## 🎯 **REQUIREMENTS SUMMARY**

### **Core Functionality**
1. **Telegram User Profile Collection** - Extract full user data when bot is called
2. **Registration Status Check** - Verify if user exists in DB by `telegram_chat_id` or `telegram_user_id`
3. **Dynamic Menu Generation** - Show different menu items based on registration status
4. **User Data Persistence** - Store Telegram profile data for unregistered users
5. **Magic Link Generation** - Create magic links for registered users
6. **Conditional Menu Items** - Balance/LastActions only for registered users

---

## 📊 **AVAILABLE TELEGRAM USER DATA**

From Telegram API `user` object (`inline_query.from` or `callback_query.from`):

```python
{
    "id": 123456789,                    # ✅ Telegram User ID (unique)
    "is_bot": false,                    # Bot flag
    "first_name": "John",               # ✅ First name
    "last_name": "Doe",                 # ✅ Last name (optional)
    "username": "johndoe",              # ✅ Telegram username (@johndoe)
    "language_code": "en",              # ✅ Language (already used)
    "is_premium": false,                # Premium status (optional)
    "photo_url": "...",                 # Profile photo URL (optional, rarely available)
}
```

**Fields we'll collect:**
- ✅ `id` → `telegram_user_id` (new field in DB)
- ✅ `username` → `telegram_username` (already in some models)
- ✅ `first_name` → `first_name` (new field)
- ✅ `last_name` → `last_name` (new field, optional)
- ✅ `language_code` → Already used for i18n
- ✅ `is_premium` → `is_premium` (optional metadata)

---

## 🗄️ **DATABASE SCHEMA UPDATES**

### **Current User Model** (backend/server.py):
```python
class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str
    telegram_chat_id: str      # Current field
    is_verified: bool
    created_at: datetime
    updated_at: datetime
```

### **Required Updates**:
```python
class User(BaseModel):
    id: str
    name: str
    email: EmailStr              # Required for registered users
    phone: str                   # Required for registered users
    telegram_chat_id: str        # Keep existing
    telegram_user_id: int        # ✅ NEW: Telegram User ID (from user.id)
    telegram_username: str       # ✅ NEW: @username (optional)
    first_name: str              # ✅ NEW: From Telegram
    last_name: Optional[str]      # ✅ NEW: From Telegram (optional)
    language_code: str           # ✅ NEW: Store user's language
    is_premium: bool             # ✅ NEW: Premium status (optional)
    is_verified: bool
    registration_status: str     # ✅ NEW: "pending", "registered", "verified"
    created_at: datetime
    updated_at: datetime
```

### **New Collection: `telegram_users` (for unregistered users)**:
```python
{
    "telegram_user_id": 123456789,
    "telegram_username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "language_code": "en",
    "is_premium": false,
    "collected_at": datetime,
    "registration_pending": true
}
```

---

## 🔄 **IMPLEMENTATION FLOW**

### **1. User Calls Bot (@taxoin_bot)**

```
User types @taxoin_bot
    ↓
Telegram sends inline_query with user data
    ↓
Extract full user profile:
    - telegram_user_id (user.id)
    - username (user.username)
    - first_name (user.first_name)
    - last_name (user.last_name)
    - language_code (user.language_code)
    ↓
Check registration status in DB
    ↓
[BRANCH A] User is REGISTERED
[BRANCH B] User is NOT REGISTERED
```

---

### **2. BRANCH A: Registered User Flow**

```python
# User found in DB with is_verified=True
registered_user = await db.users.find_one({
    "$or": [
        {"telegram_user_id": user_id},
        {"telegram_chat_id": str(user_id)}
    ],
    "is_verified": True
})

if registered_user:
    # Show "Welcome Back" menu
    menu_items = [
        {
            "id": "1",
            "action": "welcomeBack",
            "title": "👋 Welcome Back, {name}!",
            "description": "Continue to your account",
            "button": "👋 Welcome Back",
            "response": "Welcome back message",
            "magic_link": generate_magic_link(registered_user.email)
        },
        {
            "id": "3",
            "action": "whatIsMyBalance",
            "title": "💰 What Is My Balance",
            "description": "Check your account balance"
        },
        {
            "id": "4",
            "action": "showLastactions",
            "title": "📋 Show Last Actions",
            "description": "View your recent activity"
        }
    ]
```

**Magic Link Generation:**
```python
def generate_welcome_magic_link(user_id: str, email: str) -> str:
    """Generate magic link for registered user login - REUSE EXISTING OTP VERIFICATION ENDPOINT"""
    # ✅ Use SAME magic link system as OTP verification
    # Generate token using existing create_magic_link_token() function
    # Token format: email:otp:timestamp (same as registration flow)
    # Reuse existing /api/verify-magic-link endpoint - NO NEW ENDPOINT NEEDED
    from backend.server import create_magic_link_token
    
    # For registered users, we can use email + current timestamp as "OTP" 
    # OR generate a session token. The verify-magic-link endpoint will authenticate user.
    token = create_magic_link_token(email, str(user_id))  # Using user_id as "OTP" for simplicity
    return f"https://putana.date/api/verify-magic-link?token={token}"
```

---

### **3. BRANCH B: Unregistered User Flow**

```python
# User NOT found in DB
if not registered_user:
    # Collect Telegram profile data
    telegram_profile = {
        "telegram_user_id": user.get("id"),
        "telegram_username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "language_code": user.get("language_code", "en"),
        "is_premium": user.get("is_premium", False),
        "collected_at": datetime.now(timezone.utc),
        "registration_pending": True
    }
    
    # Persist to telegram_users collection (upsert)
    await db.telegram_users.update_one(
        {"telegram_user_id": user.get("id")},
        {"$set": telegram_profile},
        upsert=True
    )
    
    # Show "Join To Me" menu (registration flow)
    menu_items = [
        {
            "id": "1",
            "action": "joinToMe",
            "title": "👥 Join To Me",
            "description": "Start your registration",
            "button": "👥 Start Registration",
            "response": "Registration welcome message",
            "registration_url": "https://putana.date/registrationOfNewUser?telegram_user_id={user_id}"
        },
        {
            "id": "2",
            "action": "explainWhatIsThis",
            "title": "📖 Explain What Is This",
            "description": "Learn about Telega2Go"
        }
        # NO Balance or LastActions for unregistered users
    ]
```

---

## 🎨 **MENU STRUCTURE BY REGISTRATION STATUS**

### **Registered Users Menu (3-4 items)**
```
1. 👋 Welcome Back, {name}!
   → Shows: "Welcome back" message
   → Button: "🔗 Continue to Account" (Magic Link)
   
2. 💰 What Is My Balance
   → Shows: Current balance info
   
3. 📋 Show Last Actions
   → Shows: Recent activity history
   
[Optional] 4. 📖 Explain What Is This
```

### **Unregistered Users Menu (2 items)**
```
1. 👥 Join To Me
   → Shows: Registration welcome message
   → Button: "🚀 Start Registration" (VeryFirstWelcomeScreen URL)
   
2. 📖 Explain What Is This
   → Shows: System explanation
```

---

## 🔧 **TECHNICAL IMPLEMENTATION STEPS**

### **Step 1: Database Service Layer**

Create `telegram_user_service.py`:
```python
class TelegramUserService:
    async def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[User]:
        """Get registered user by Telegram User ID"""
        return await db.users.find_one({
            "$or": [
                {"telegram_user_id": telegram_user_id},
                {"telegram_chat_id": str(telegram_user_id)}
            ],
            "is_verified": True
        })
    
    async def save_telegram_profile(self, user_data: dict):
        """Save/update Telegram profile for unregistered user"""
        await db.telegram_users.update_one(
            {"telegram_user_id": user_data["id"]},
            {"$set": {
                "telegram_user_id": user_data["id"],
                "telegram_username": user_data.get("username"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "language_code": user_data.get("language_code", "en"),
                "is_premium": user_data.get("is_premium", False),
                "collected_at": datetime.now(timezone.utc),
                "registration_pending": True
            }},
            upsert=True
        )
    
    async def check_registration_status(self, telegram_user_id: int) -> dict:
        """Check if user is registered and verified"""
        user = await self.get_user_by_telegram_id(telegram_user_id)
        if user:
            return {
                "is_registered": True,
                "is_verified": user.get("is_verified", False),
                "user": user
            }
        return {
            "is_registered": False,
            "is_verified": False,
            "user": None
        }
```

### **Step 2: Update Inline Query Handler**

Modify `handle_inline_query()` in `bot_commands.py`:

```python
async def handle_inline_query(
    self, 
    inline_query_id: str, 
    query: str, 
    user_id: str, 
    language_code: Optional[str] = None,
    full_user_data: Optional[dict] = None  # ✅ NEW: Full Telegram user object
) -> bool:
    """Handle inline queries with registration-aware menu"""
    try:
        lang = self._get_language(language_code)
        
        # ✅ NEW: Extract full user profile
        telegram_user_id = full_user_data.get("id") if full_user_data else int(user_id)
        telegram_username = full_user_data.get("username") if full_user_data else None
        first_name = full_user_data.get("first_name") if full_user_data else None
        last_name = full_user_data.get("last_name") if full_user_data else None
        
        # ✅ NEW: Check registration status
        user_service = TelegramUserService()
        registration_status = await user_service.check_registration_status(telegram_user_id)
        
        # ✅ NEW: Generate menu based on registration status
        if registration_status["is_registered"] and registration_status["is_verified"]:
            # REGISTERED USER MENU
            menu_items = self._get_registered_user_menu(
                registration_status["user"], 
                language_code
            )
        else:
            # UNREGISTERED USER MENU
            # Save Telegram profile data
            await user_service.save_telegram_profile(full_user_data or {})
            
            menu_items = self._get_unregistered_user_menu(
            telegram_user_id, 
            language_code
        )
        
        # Build inline query results
        results = []
        for item in menu_items:
            # ... build results with translations ...
```

### **Step 3: Menu Generation Methods**

```python
def _get_registered_user_menu(self, user: dict, language_code: Optional[str]) -> List[dict]:
    """Generate menu for registered users"""
    lang = self._get_language(language_code)
    
    # Generate magic link
    magic_link = self._generate_welcome_magic_link(user["id"], user["email"])
    
    return [
        {
            "id": "1",
            "action_key": "welcomeBack",
            "title": self._get_translation(lang, "menu.welcomeBack.title", {"name": user.get("name", "User")}),
            "description": self._get_translation(lang, "menu.welcomeBack.description"),
            "button": self._get_translation(lang, "menu.welcomeBack.button"),
            "initial": self._get_translation(lang, "menu.welcomeBack.initial", {"name": user.get("name")}),
            "magic_link": magic_link,
            "callback_data": "action_welcomeBack"
        },
        {
            "id": "2",
            "action_key": "whatIsMyBalance",
            # ... balance menu item ...
        },
        {
            "id": "3",
            "action_key": "showLastactions",
            # ... last actions menu item ...
        }
    ]

def _get_unregistered_user_menu(
    self, 
    telegram_user_id: int, 
    language_code: Optional[str]
) -> List[dict]:
    """Generate menu for unregistered users"""
    lang = self._get_language(language_code)
    
    # ✅ Registration URL includes telegram_user_id for pre-filling
    registration_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
    
    return [
        {
            "id": "1",
            "action_key": "joinToMe",
            "title": self._get_translation(lang, "menu.joinToMe.title"),
            "description": self._get_translation(lang, "menu.joinToMe.description"),
            "button": self._get_translation(lang, "menu.joinToMe.button"),
            "registration_url": registration_url,  # ✅ Includes telegram_user_id
            "callback_data": "action_joinToMe"
        },
        {
            "id": "2",
            "action_key": "explainWhatIsThis",
            # ... explain menu item ...
        }
    ]
```

### **Step 4: Update main.py Webhook Handler**

```python
# Handle inline queries (when @taxoin_bot is typed)
if "inline_query" in data:
    inline_query = data["inline_query"]
    inline_query_id = inline_query["id"]
    query = inline_query.get("query", "")
    user = inline_query.get("from", {})  # ✅ Full user object
    
    # ✅ Extract all user data
    user_id = str(user.get("id", ""))
    language_code = user.get("language_code")
    full_user_data = user  # ✅ Pass full user object
    
    if bot_commands:
        success = await bot_commands.handle_inline_query(
            inline_query_id, 
            query, 
            user_id, 
            language_code,
            full_user_data  # ✅ NEW: Pass full user data
        )
```

### **Step 5: Magic Link Generation for Registered Users**

```python
def _generate_welcome_magic_link(self, user_id: str, email: str) -> str:
    """Generate magic link for registered user - REUSE EXISTING OTP VERIFICATION SYSTEM"""
    # ✅ Use the SAME magic link endpoint as OTP verification: /api/verify-magic-link
    # ✅ No need to validate Telegram data twice - we already have all user info
    # ✅ Reuse existing create_magic_link_token() from backend
    
    # Import from backend (or make HTTP call to backend endpoint)
    # For registered users accessing their account, we can create a session token
    # The verify-magic-link endpoint will check user exists and is verified
    
    from backend.server import create_magic_link_token
    
    # Generate token - can use email + user_id as OTP identifier
    # The verify-magic-link endpoint will authenticate the user
    token = create_magic_link_token(email, user_id)
    
    # ✅ Use SAME endpoint as OTP verification
    return f"https://putana.date/api/verify-magic-link?token={token}"
```

---

## 🌍 **I18N TRANSLATIONS TO ADD**

Add new translations for "Welcome Back" menu:

```python
"menu": {
    "welcomeBack": {
        "title": {
            "en": "👋 Welcome Back, {name}!",
            "ru": "👋 С возвращением, {name}!",
            "es": "👋 ¡Bienvenido de nuevo, {name}!",
            "de": "👋 Willkommen zurück, {name}!"
        },
        "description": {
            "en": "Continue to your account",
            "ru": "Перейти в ваш аккаунт",
            "es": "Continuar a tu cuenta",
            "de": "Zu deinem Konto weiterleiten"
        },
        "button": {
            "en": "👋 Welcome Back",
            "ru": "👋 Вернуться",
            "es": "👋 Bienvenido",
            "de": "👋 Willkommen"
        },
        "initial": {
            "en": "👋 <b>Welcome Back!</b>\n\nGreat to see you again!",
            # ... other languages ...
        },
        "response": {
            "en": "👋 <b>Welcome Back, {name}!</b>\n\nYour account is ready. Click the button below to access your dashboard.",
            # ... other languages ...
        }
    }
}
```

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Database & Service Layer**
- [ ] ✅ **USE REAL MONGODB** (`backend/server.py` with motor) - NOT simple version
- [ ] Update User model to include Telegram profile fields
- [ ] Add `name` UNIQUE constraint check (application-level)
- [ ] Create `telegram_users` collection schema (infinite retention)
- [ ] Create `TelegramUserService` class
- [ ] Implement `check_registration_status()` method
- [ ] Implement `save_telegram_profile()` method (persist to MongoDB)
- [ ] Implement `check_name_availability()` method (CRITICAL)
- [ ] Add database indexes for `telegram_user_id`, `telegram_chat_id`, `name` (unique)

### **Phase 2: Menu Generation Logic**
- [ ] Create `_get_registered_user_menu()` method
- [ ] Create `_get_unregistered_user_menu()` method
- [ ] Update `handle_inline_query()` to check registration status
- [ ] Implement magic link generation for registered users
- [ ] Update menu item structure to include URLs/links

### **Phase 3: I18N Support**
- [ ] Add "welcomeBack" translations to all languages
- [ ] Update existing menu item translations if needed
- [ ] Add dynamic name substitution in translations
- [ ] Add name conflict error messages in all languages

### **Phase 4: Webhook Integration**
- [ ] Update `main.py` to extract full user object from Telegram
- [ ] Pass full user data to `handle_inline_query()`
- [ ] Pass full user data to `handle_callback_query()` (for future use)
- [ ] Ensure ALL Telegram user fields are captured and persisted

### **Phase 5: Callback Query Updates**
- [ ] Update `handle_callback_query()` to handle "welcomeBack" action
- [ ] ✅ Generate magic link URLs using EXISTING `/api/verify-magic-link` endpoint
- [ ] Generate registration URLs: `/registrationOfNewUser?telegram_user_id=XXX`
- [ ] Ensure URLs include proper query parameters

### **Phase 6: Testing**
- [ ] Test with registered user (should see Welcome Back menu)
- [ ] Test with unregistered user (should see Join To Me menu)
- [ ] Test magic link generation and validation
- [ ] Test database persistence of Telegram profiles
- [ ] Test i18n for all menu items
- [ ] Update `test_i18n_features.py` to include registration status tests

### **Phase 7: Documentation**
- [ ] Update `TECHNICAL_DOCUMENTATION.md`
- [ ] Create feature documentation file
- [ ] Update API endpoint documentation

---

## 🚨 **IMPORTANT CONSIDERATIONS**

### **1. User Identification**
- Use `telegram_user_id` (integer) as primary identifier
- Fallback to `telegram_chat_id` (string) for backwards compatibility
- Index both fields for fast lookups

### **2. Privacy & GDPR**
- Only collect data that user explicitly provides
- Store Telegram profile data only for pending registrations
- Clean up unregistered user data after X days (optional)

### **3. Magic Link Security**
- Use same HMAC signing as existing magic links
- Include expiration time (e.g., 24 hours)
- Verify user_id matches when magic link is used

### **4. Registration Flow Integration**
- VeryFirstWelcomeScreen should pre-fill Telegram data
- Registration URL should include `telegram_user_id` parameter
- After registration, link Telegram profile to User record

### **5. Backwards Compatibility**
- Existing registered users (without `telegram_user_id`) should still work
- Use `telegram_chat_id` as fallback identifier
- Migrate existing users to include `telegram_user_id` (optional)

---

## 📝 **API ENDPOINTS TO UPDATE**

### **Backend API (`/api/...`)**

1. **GET/POST `/api/user-by-telegram-id`** (NEW)
   - Check if user is registered by Telegram User ID
   - Return registration status and user data

2. **POST `/api/save-telegram-profile`** (NEW)
   - Save Telegram profile data for unregistered users
   - Called automatically from webhook

3. **POST `/api/verify-magic-link`** (EXISTS, may need updates)
   - Already exists, verify it works with new magic links
   - Should authenticate user and redirect to dashboard

4. **GET `/api/register?telegram_user_id=XXX`** (UPDATE)
   - Pre-fill registration form with Telegram data
   - Link Telegram profile to registration session

---

## 🎯 **SUCCESS CRITERIA**

1. ✅ Registered users see "Welcome Back" menu with Magic Link button
2. ✅ Unregistered users see "Join To Me" menu with Registration URL button
3. ✅ Balance and LastActions only appear for registered users
4. ✅ Telegram profile data is collected and persisted automatically
5. ✅ Magic links work correctly for registered users
6. ✅ Registration flow integrates with Telegram data
7. ✅ All menu items support i18n
8. ✅ Database queries are efficient (indexed fields)

---

## 📅 **ESTIMATED IMPLEMENTATION TIME**

- **Phase 1** (Database & Service): 2-3 hours
- **Phase 2** (Menu Logic): 3-4 hours
- **Phase 3** (I18N): 1-2 hours
- **Phase 4** (Webhook): 1 hour
- **Phase 5** (Callback): 2 hours
- **Phase 6** (Testing): 2-3 hours
- **Phase 7** (Documentation): 1 hour

**Total**: ~12-16 hours

---

## ✅ **CLARIFICATIONS RECEIVED**

1. **Magic Link**: ✅ **USE EXISTING `/api/verify-magic-link`** - Same endpoint as OTP verification, no new endpoint needed
2. **Registration URL**: ✅ **`/registrationOfNewUser?telegram_user_id=XXX`** - Correct spelling, reflects registration state
3. **Name Handling**: ✅ **CRITICAL** - Check if Telegram name exists in DB:
   - If name is **FREE**: Pre-fill registration form with Telegram name (but user can edit)
   - If name is **TAKEN**: Show empty field or different suggestion (user MUST provide unique name)
   - User **ALWAYS** has ability to change name independently from Telegram
4. **Data Persistence**: ✅ **KEEP INFINITE TIME** - Use REAL MongoDB server (`backend/server.py`), not simple in-memory version
5. **Database**: ✅ **Use `backend/server.py`** with MongoDB for all user data - persistent storage

---

## 🚨 **CRITICAL NAME HANDLING LOGIC**

### **Name Availability Check Flow**:

```python
async def check_name_availability(telegram_name: str) -> dict:
    """Check if name from Telegram is available in database"""
    # Check if name already exists
    existing_user = await db.users.find_one({"name": telegram_name})
    
    if existing_user:
        return {
            "available": False,
            "suggestion": None,  # Don't pre-fill, user must choose
            "message": "This name is already taken. Please choose a different name."
        }
    else:
        return {
            "available": True,
            "suggestion": telegram_name,  # Pre-fill with Telegram name
            "message": None
        }
```

### **Registration Form Behavior**:

```
User clicks "Join To Me" button
    ↓
Redirect to /registrationOfNewUser?telegram_user_id=123
    ↓
Backend checks name availability:
    ↓
[BRANCH A] Name is AVAILABLE:
    - Pre-fill name field with Telegram first_name
    - Allow user to edit
    - Submit registration
    
[BRANCH B] Name is TAKEN:
    - Show empty name field
    - Display message: "Name '{telegram_name}' is already taken. Please choose another."
    - User MUST provide unique name
    - Submit registration
```

---

## 🗄️ **DATABASE: USE REAL MONGODB SERVER**

### **Important**: 
- ✅ **USE `backend/server.py`** (MongoDB with motor)
- ❌ **DO NOT USE `backend/server_simple.py`** (in-memory, temporary)

### **Collections Structure**:

```
users (MongoDB Collection - Persistent, Infinite Retention)
├── id: str
├── name: str (UNIQUE constraint - enforced in application logic)
├── email: EmailStr (UNIQUE)
├── phone: str
├── telegram_chat_id: str
├── telegram_user_id: int (NEW - primary Telegram identifier)
├── telegram_username: str (NEW)
├── first_name: str (NEW - from Telegram)
├── last_name: Optional[str] (NEW)
├── language_code: str (NEW)
├── is_premium: bool (NEW)
├── is_verified: bool
├── created_at: datetime
└── updated_at: datetime

telegram_users (NEW - For unregistered users, also INFINITE retention)
├── telegram_user_id: int (PRIMARY KEY)
├── telegram_username: Optional[str]
├── first_name: str
├── last_name: Optional[str]
├── language_code: str
├── is_premium: bool
├── collected_at: datetime
└── registration_pending: bool (true = not yet registered)
```

### **Indexes Required**:
```python
# In MongoDB (or via Motor):
await db.users.create_index("name", unique=True)  # Enforce unique names
await db.users.create_index("email", unique=True)  # Already exists
await db.users.create_index("telegram_user_id")  # Fast lookup
await db.users.create_index("telegram_chat_id")  # Backwards compatibility
await db.telegram_users.create_index("telegram_user_id", unique=True)
```

---

**Status**: ✅ **PLAN READY FOR REVIEW**  
**Next Step**: Review and approve plan, then proceed with Phase 1 implementation

