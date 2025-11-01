# 🔧 Magic Link Apache Proxy Error Fix

## 🎯 Problem
Apache reverse proxy was returning "Proxy Error: invalid response from upstream server" when accessing magic link verification URLs.

**Error:** `Proxy Error: The proxy server received an invalid response from an upstream server`

## 🔍 Root Cause
The backend was returning **relative URLs** in redirect responses (e.g., `/?token=...`). Apache reverse proxy requires **absolute URLs** for proper proxying.

## ✅ Solution

### Backend Changes (`backend/server.py`)
- Modified `verify_magic_link()` endpoint to accept `Request` parameter
- Extract `base_url` from the request object (works with reverse proxies)
- Remove `/api` suffix if present (Apache adds it to the base URL)
- Use **absolute URLs** in all redirect responses

**Before:**
```python
return RedirectResponse(url=f"/?token={access_token}", status_code=302)
```

**After:**
```python
base_url = str(request.base_url).rstrip('/')
if base_url.endswith('/api'):
    base_url = base_url[:-4]
redirect_url = f"{base_url}/?token={access_token}"
return RedirectResponse(url=redirect_url, status_code=302)
```

## 📋 Technical Details

### Apache Proxy Configuration
The production server uses Apache2 with ProxyPass:
```apache
ProxyPass /api/  http://127.0.0.1:55552/api/
ProxyPassReverse /api/  http://127.0.0.1:55552/api/
```

### Why Relative URLs Fail
- Apache forwards requests to backend
- Backend returns `302 Found` with `Location: /?token=...`
- Apache doesn't know how to resolve the relative URL
- Results in "invalid response from upstream server"

### Why Absolute URLs Work
- Backend returns `302 Found` with `Location: https://putana.date/?token=...`
- Apache can properly forward the redirect
- Client browser receives correct redirect URL

## ✅ Test Results

**Before Fix:**
- Apache returns 502 Proxy Error
- "invalid response from upstream server"

**After Fix:**
- Backend returns proper 302 redirect with absolute URL
- Apache successfully proxies the redirect
- Client browser redirects correctly

## 📋 Files Changed
1. `backend/server.py` - Added `Request` parameter and absolute URL construction

## 🚀 Deployment Notes
- **Local testing:** ✅ Verified working with absolute URLs
- **Production:** Requires backend deployment
- **Backward compatibility:** Works with both direct access and reverse proxy

---
**Date:** 2025-11-01  
**Version:** v2.15.6-magic-link-proxy-fix  
**Status:** ✅ Ready for Production Deployment

