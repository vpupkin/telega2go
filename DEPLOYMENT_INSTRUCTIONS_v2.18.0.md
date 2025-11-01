# 🚀 DEPLOYMENT INSTRUCTIONS v2.18.0

## ⚠️ **CRITICAL: Production Frontend Bundle is Outdated**

**Error**: `No routes matched location "/telegram-register"`

**Root Cause**: Production bundle was built BEFORE the route was added.

---

## 📋 **STEPS TO DEPLOY**

### **1. Commit Changes (Local)**
```bash
git add frontend/src/App.js frontend/src/components/UserRegistration.jsx frontend/src/components/LoginPage.jsx frontend/public/sw.js
git commit -m "feat: Add /telegram-register route with toggle UI (v2.18.0)"
git push origin <branch-name>
```

### **2. On Production Server**

```bash
# Pull latest code
cd /path/to/telega2go
git pull origin <branch-name>

# Rebuild frontend (this is CRITICAL - the route is only added after rebuild)
./start.sh full
# OR specifically:
docker-compose build frontend
docker-compose up -d frontend

# Verify deployment
docker-compose logs frontend | tail -50
docker-compose ps frontend
```

### **3. Clear Browser Cache**
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Or use incognito/private browsing mode
- Or clear site data in DevTools → Application → Storage

---

## ✅ **VERIFICATION**

After deployment:
1. Visit: `https://putana.date/telegram-register`
2. Should see: Purple-themed Telegram registration form with toggle buttons
3. No errors in browser console

---

**Status**: ⚠️ **DEPLOYMENT REQUIRED**  
**Priority**: **HIGH** - Feature is blocked until deployment
