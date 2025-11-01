# 🚀 Google OAuth Deployment Instructions

**Date**: 2025-11-01  
**Feature**: Google OAuth Authentication  
**Branch**: `googol`  
**Status**: Ready for Production Deployment  

---

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### **1. Code Status**
- ✅ Phase 1 (Backend): Code committed
- ✅ Phase 2 (Frontend): Code committed
- ✅ Service worker cache updated
- ✅ All changes pushed to remote repository

### **2. Google Cloud Console Setup (REQUIRED)**
- [ ] Create Google Cloud Project
- [ ] Enable Google+ API
- [ ] Create OAuth 2.0 Credentials
  - Application type: Web application
  - Authorized redirect URI: `https://putana.date/api/auth/google/callback`
- [ ] Copy Client ID and Client Secret

### **3. Environment Variables**
Add to production `.env` file:
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://putana.date/api/auth/google/callback
FRONTEND_URL=https://putana.date
```

---

## 🔧 **DEPLOYMENT STEPS (On Production Server)**

### **Step 1: Pull Latest Code**
```bash
cd /path/to/telega2go
git fetch origin
git checkout googol  # or merge googol into your production branch
git pull origin googol
```

### **Step 2: Install New Dependencies**
```bash
# Backend dependencies (Google OAuth libraries)
cd backend
pip install -r requirements.txt
# OR if using Docker, rebuild will handle this
```

### **Step 3: Rebuild Containers**
```bash
# Using start.sh (recommended)
./start.sh full

# OR manually
docker compose build backend frontend
docker compose up -d backend frontend
```

### **Step 4: Verify Deployment**
```bash
# Check backend OAuth endpoint
curl -I https://putana.date/api/auth/google
# Should return 302 (redirect to Google)

# Check frontend login page
curl -I https://putana.date/login
# Should return 200
```

### **Step 5: Test Complete Flow**
1. Visit `https://putana.date/login`
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Verify redirect to dashboard

---

## 🧪 **POST-DEPLOYMENT TESTING**

### **Frontend Tests**
- [ ] `/login` page loads correctly
- [ ] Google Sign-In button visible
- [ ] Button redirects correctly
- [ ] Telegram option available
- [ ] UI renders properly

### **Backend Tests**
- [ ] `GET /api/auth/google` returns redirect
- [ ] `GET /api/auth/google/callback` handles OAuth
- [ ] State token generation works
- [ ] User creation works
- [ ] Account linking works

### **End-to-End Test**
- [ ] Complete OAuth flow works
- [ ] Token stored in localStorage
- [ ] Dashboard accessible after login
- [ ] New users created correctly
- [ ] Existing users linked correctly

---

## ⚠️ **TROUBLESHOOTING**

### **Issue: `/login` route not found (404)**
**Solution**: Frontend container needs rebuild
```bash
docker compose build frontend
docker compose up -d frontend
```

### **Issue: `/api/auth/google` returns 404**
**Solution**: Backend container needs rebuild
```bash
docker compose build backend
docker compose up -d backend
```

### **Issue: OAuth redirect fails**
**Solution**: Check environment variables
```bash
# Verify these are set:
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET
echo $GOOGLE_REDIRECT_URI
```

### **Issue: Google OAuth error**
**Solution**: Verify redirect URI matches Google Console
- Google Console: `https://putana.date/api/auth/google/callback`
- Environment: `GOOGLE_REDIRECT_URI=https://putana.date/api/auth/google/callback`

---

## 📊 **CURRENT STATUS**

### **Local Environment**
- ✅ Code committed and pushed
- ✅ Ready for deployment

### **Production Environment (`putana.date`)**
- ❌ Frontend not rebuilt (old code)
- ❌ Backend not rebuilt (old code)
- ❌ Google OAuth credentials not configured

---

## ✅ **DEPLOYMENT READINESS**

- ✅ Code: **READY**
- ❌ Google OAuth Setup: **PENDING**
- ❌ Production Deployment: **PENDING**
- ❌ Testing: **PENDING**

---

**Action Required**: Deploy to production server and configure Google OAuth credentials
