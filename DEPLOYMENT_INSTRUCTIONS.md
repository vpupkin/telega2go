# 🚀 IMMEDIATE PRODUCTION DEPLOYMENT INSTRUCTIONS

**Date:** 2025-11-01  
**Priority:** 🔴 **CRITICAL - USER-BLOCKING BUG**

---

## ⚠️ **CURRENT STATUS**

**Production Status:** ❌ **STILL RUNNING OLD CODE**
- ERROR 19 (500 Internal Server Error) still occurring
- Backend needs to pull and restart

**Local Status:** ✅ **FIXED AND TESTED**
- Code committed: `4283ee4`
- Tagged: `v2.13.2-error19-fix`
- Pushed to: `origin/PRE_QR_CODE`

---

## 📋 **DEPLOYMENT STEPS (REMOTE SERVER)**

### **Step 1: SSH to Production Server**
```bash
ssh user@putana.date
cd /path/to/telega2go
```

### **Step 2: Pull Latest Code**
```bash
# If production uses PRE_QR_CODE branch:
git fetch origin
git checkout PRE_QR_CODE
git pull origin PRE_QR_CODE

# OR if production uses main branch:
git checkout main
git merge PRE_QR_CODE  # Merge ERROR 19 fix to main
git push origin main   # Push merged fix
```

### **Step 3: Restart Backend Service**
```bash
# Using start.sh (recommended):
./start.sh full

# OR using docker compose directly:
docker compose restart backend

# OR rebuild backend:
docker compose up -d --build backend
```

### **Step 4: Verify Deployment**
```bash
# Check backend logs for ERROR 19 fix:
docker compose logs backend --tail=50 | grep -E "(Step 1.5|raw pymongo|ERROR|hour must be)"

# Should see:
# ✅ "Step 1.5: Querying database for urr_id: ... (using raw pymongo)"
# ✅ "Step 1.5a: Retrieved via raw pymongo, converted datetime fields to ISO strings"
# ❌ Should NOT see: "Error in register_telegram_user: hour must be in 0..23"

# Test endpoint:
curl -X POST https://putana.date/api/register-telegram \
  -H "Content-Type: application/json" \
  -d '{"urr_id": "test-urr-id", "password": "test123456"}'

# Expected responses:
# ✅ 400 "Registration request not found" (expected if URR_ID doesn't exist)
# ✅ 200 Success (if URR_ID exists and valid)
# ❌ 500 Internal Server Error (ERROR 19 - should NOT happen after fix)
```

---

## 🔍 **WHAT WAS FIXED**

**File:** `backend/server.py` (lines 539-584)

**Change:**
- **OLD:** `registration_request = await db.registration_requests.find_one(...)`
  - Motor auto-converts datetime → causes ERROR 19
- **NEW:** `raw_doc = mongo_db.registration_requests.find_one(...)`
  - Raw pymongo client → no auto-conversion → ERROR 19 fixed

**Test Results:**
- ✅ All 4 penalty tests passing
- ✅ No 500 errors locally
- ✅ DateTime conversion handled correctly

---

## 📊 **VERIFICATION CHECKLIST**

After deployment, verify:

- [ ] Backend logs show "Step 1.5: Querying database for urr_id: ... (using raw pymongo)"
- [ ] Backend logs show "Step 1.5a: Retrieved via raw pymongo, converted datetime fields to ISO strings"
- [ ] Backend logs do NOT show "Error in register_telegram_user: hour must be in 0..23"
- [ ] Test registration: Returns 400 (not found) or 200 (success), NOT 500
- [ ] Frontend registration form works without 500 errors

---

## 🚨 **IF ERRORS PERSIST**

1. **Check which branch production is using:**
   ```bash
   git branch
   git log --oneline -5
   ```

2. **Verify fix is in the code:**
   ```bash
   grep -A 10 "raw pymongo" backend/server.py
   # Should show the fix code
   ```

3. **Check backend service is restarted:**
   ```bash
   docker compose ps backend
   # Should show recent restart time
   ```

4. **Check backend logs:**
   ```bash
   docker compose logs backend --tail=100
   # Look for ERROR 19 or Step 1.5 logs
   ```

---

## ✅ **SUCCESS CRITERIA**

After deployment:
- ✅ No more 500 Internal Server Error on `/api/register-telegram`
- ✅ Registration flow completes successfully
- ✅ Backend logs show raw pymongo being used
- ✅ All 4 penalty tests passing (verify locally after deployment)

---

**🚨 CRITICAL: Deploy immediately - users cannot complete registration until this is deployed.**

