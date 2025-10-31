# 🔒 Name Availability Logic - Critical Implementation

## ⚠️ **CRITICAL REQUIREMENT**

Users must be able to change their name independently from Telegram. If Telegram name already exists in DB, user MUST provide a different name.

---

## 📋 **NAME HANDLING RULES**

### **Rule 1: Name Uniqueness**
- Names MUST be unique in the database
- Cannot register with a name that already exists
- Check happens BEFORE registration completion

### **Rule 2: Telegram Name Pre-fill Logic**
```
IF telegram_first_name EXISTS in DB:
    ❌ Do NOT pre-fill name field
    ✅ Show empty field
    ✅ Display message: "Name '{telegram_name}' is already taken. Please choose another."
    ✅ User MUST provide unique name

ELSE (name is FREE):
    ✅ Pre-fill name field with telegram_first_name
    ✅ Allow user to edit/change
    ✅ User can submit with Telegram name or change it
```

### **Rule 3: User Always Has Control**
- User can ALWAYS change name from Telegram value
- Name in system is independent from Telegram
- After registration, user can update name anytime

---

## 🔧 **IMPLEMENTATION**

### **Backend Endpoint: GET `/api/registrationOfNewUser`**

```python
@api_router.get("/registrationOfNewUser")
async def get_registration_form_data(telegram_user_id: int = Query(...)):
    """Get Telegram user data for registration form pre-filling"""
    
    # Load Telegram profile
    telegram_profile = await db.telegram_users.find_one(
        {"telegram_user_id": telegram_user_id}
    )
    
    if not telegram_profile:
        raise HTTPException(
            status_code=404, 
            detail="Telegram profile not found. Please call the bot first."
        )
    
    telegram_first_name = telegram_profile.get("first_name", "")
    
    # ✅ CRITICAL: Check name availability
    name_available = await check_name_availability(telegram_first_name)
    
    return {
        "telegram_user_id": telegram_user_id,
        "telegram_username": telegram_profile.get("telegram_username"),
        "first_name": telegram_profile.get("first_name"),
        "last_name": telegram_profile.get("last_name"),
        "language_code": telegram_profile.get("language_code", "en"),
        "name_available": name_available["available"],
        "suggested_name": name_available["suggestion"],  # Telegram name if free, None if taken
        "name_message": name_available["message"]  # Error message if name taken
    }

async def check_name_availability(name: str) -> dict:
    """Check if name is available in database"""
    if not name:
        return {
            "available": False,
            "suggestion": None,
            "message": "Name cannot be empty"
        }
    
    # Check if name exists (case-insensitive)
    existing_user = await db.users.find_one({
        "name": {"$regex": f"^{name}$", "$options": "i"}  # Case-insensitive
    })
    
    if existing_user:
        return {
            "available": False,
            "suggestion": None,  # Don't suggest taken name
            "message": f"Name '{name}' is already taken. Please choose a different name."
        }
    else:
        return {
            "available": True,
            "suggestion": name,  # Suggest Telegram name
            "message": None
        }
```

### **Frontend Registration Form Logic**

```javascript
// Load registration data
const response = await fetch(
    `/api/registrationOfNewUser?telegram_user_id=${telegramUserId}`
);
const data = await response.json();

// Name field handling
if (data.name_available) {
    // ✅ Name is FREE - pre-fill with Telegram name
    setName(data.suggested_name);
    setShowNameWarning(false);
} else {
    // ❌ Name is TAKEN - show empty field + warning
    setName("");
    setShowNameWarning(true);
    setNameWarningMessage(data.name_message);
}

// User can always edit name
// On submit, validate name uniqueness again
```

### **Registration Submission Validation**

```python
@api_router.post("/register")
async def register_user(registration: UserRegistration):
    """Register new user - VALIDATE NAME UNIQUENESS"""
    
    # ✅ CRITICAL: Check name uniqueness
    existing_user_by_name = await db.users.find_one({
        "name": {"$regex": f"^{registration.name}$", "$options": "i"}
    })
    
    if existing_user_by_name:
        raise HTTPException(
            status_code=400,
            detail=f"Name '{registration.name}' is already taken. Please choose a different name."
        )
    
    # Also check email uniqueness (existing check)
    existing_user_by_email = await db.users.find_one({"email": registration.email})
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Continue with registration...
    # Link telegram_user_id from telegram_users collection
```

---

## 🌍 **I18N ERROR MESSAGES**

Add translations for name conflicts:

```python
"errors": {
    "name_taken": {
        "en": "Name '{name}' is already taken. Please choose a different name.",
        "ru": "Имя '{name}' уже занято. Пожалуйста, выберите другое имя.",
        "es": "El nombre '{name}' ya está en uso. Por favor elige otro nombre.",
        "de": "Der Name '{name}' ist bereits vergeben. Bitte wähle einen anderen Namen."
    },
    "name_empty": {
        "en": "Name cannot be empty",
        "ru": "Имя не может быть пустым",
        "es": "El nombre no puede estar vacío",
        "de": "Der Name darf nicht leer sein"
    }
}
```

---

## ✅ **TEST CASES**

### **Test 1: Telegram name is FREE**
1. User "John" calls bot (name not in DB)
2. Clicks "Join To Me"
3. Registration form loads with `name = "John"` (pre-filled)
4. User can edit or submit as-is
5. ✅ Registration succeeds

### **Test 2: Telegram name is TAKEN**
1. User "John" already exists in DB
2. New user "John" calls bot
3. Clicks "Join To Me"
4. Registration form loads with `name = ""` (empty)
5. Shows message: "Name 'John' is already taken..."
6. User must provide different name (e.g., "John Smith")
7. ✅ Registration succeeds with unique name

### **Test 3: User changes pre-filled name**
1. Telegram name "John" is FREE
2. Form pre-fills with "John"
3. User edits to "Johnny"
4. ✅ Registration succeeds with "Johnny"

### **Test 4: Name validation on submit**
1. User enters name "John"
2. Between form load and submit, "John" gets registered by another user
3. On submit, backend validates again
4. ✅ Returns error: "Name 'John' is already taken"
5. User must choose different name

---

## 🔒 **DATABASE CONSTRAINTS**

### **Application-Level Constraints** (MongoDB doesn't enforce, but we check):

```python
# Before inserting user
async def validate_user_uniqueness(user_data: dict):
    """Validate user data uniqueness before registration"""
    checks = []
    
    # Check name uniqueness
    name_check = await db.users.find_one({
        "name": {"$regex": f"^{user_data['name']}$", "$options": "i"}
    })
    if name_check:
        checks.append(f"Name '{user_data['name']}' is already taken")
    
    # Check email uniqueness
    email_check = await db.users.find_one({"email": user_data["email"]})
    if email_check:
        checks.append(f"Email '{user_data['email']}' is already registered")
    
    if checks:
        raise HTTPException(status_code=400, detail="; ".join(checks))
```

---

**Status**: ✅ **CRITICAL LOGIC DOCUMENTED**  
**Priority**: 🔴 **HIGHEST** - Name handling is core requirement

