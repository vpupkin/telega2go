# 🔐 Google OAuth Authentication Requirements

**Feature Branch**: `googol`  
**Date**: 2025-11-01  
**Status**: 📋 Requirements Document  
**Priority**: High  

---

## 🎯 **OVERVIEW**

### **Goal**
Provide users with the ability to authenticate and register using their Google Account, in addition to the existing Telegram-based authentication system.

### **Benefits**
- ✅ **Multi-provider authentication**: Users can choose between Telegram or Google
- ✅ **Faster registration**: No need for Telegram if user prefers Google
- ✅ **Email verification**: Google accounts are pre-verified
- ✅ **User convenience**: Leverages existing Google accounts
- ✅ **Reduced friction**: One-click authentication with Google

### **Integration Strategy**
- **Parallel authentication**: Google OAuth runs alongside existing Telegram authentication
- **Unified user model**: Both methods create users in the same database
- **Shared session management**: Same JWT token system for both methods
- **Dashboard access**: Both methods provide access to the same user dashboard

---

## 📋 **FUNCTIONAL REQUIREMENTS**

### **FR1: Google OAuth Login Page**
- **Description**: Create a dedicated login page with Google Sign-In button
- **Location**: `/login` or `/auth/google`
- **Components**:
  - Google Sign-In button (Google's official button design)
  - "Sign in with Google" text
  - Option to switch to Telegram authentication
  - Link to registration page for new users

### **FR2: Google OAuth Authentication Flow**
- **User clicks "Sign in with Google"**
- **Redirect to Google OAuth consent screen**
  - Request scopes: `openid`, `email`, `profile`
  - Show "Sign in to PUTANA.DATE" consent message
- **User grants permission**
- **Google redirects back with authorization code**
- **Backend exchanges code for access token**
- **Backend retrieves user info (email, name, profile picture)**
- **Backend creates/updates user in database**
- **Backend generates JWT token**
- **Frontend stores token and redirects to dashboard**

### **FR3: New User Registration via Google**
- **If Google user doesn't exist in database:**
  - Create new user account with Google data:
    - Email (from Google)
    - Name (from Google profile)
    - Profile picture URL (optional)
    - `google_id` (Google user ID)
    - `auth_provider: "google"` (to distinguish from Telegram)
    - `is_verified: true` (Google emails are verified)
    - `balance: 0.0`
    - Set `created_at` timestamp
  - Generate JWT token
  - Redirect to dashboard with welcome message

### **FR4: Existing User Login via Google**
- **If Google email matches existing user:**
  - Link Google account to existing user:
    - Add `google_id` to user document
    - Add `google_auth_provider: true` flag
    - Update profile picture if available
  - Generate JWT token
  - Redirect to dashboard

### **FR5: Account Linking**
- **Scenario**: User has Telegram account, wants to add Google login
- **Flow**:
  - User logs in via Telegram
  - In dashboard: "Link Google Account" option
  - Complete Google OAuth flow
  - Link `google_id` to existing user account
  - User can now login with either Telegram or Google

### **FR6: Profile Picture Display**
- **Use Google profile picture** if available
- **Fallback to default avatar** if not available
- **Display in dashboard** user profile section

### **FR7: Multi-Auth Provider Support**
- **User document should support**:
  - `auth_provider: "telegram" | "google" | "both"`
  - `telegram_user_id` (optional, if Telegram auth exists)
  - `google_id` (optional, if Google auth exists)
  - `email` (from either provider)
  - `name` (from either provider)

### **FR8: Session Management**
- **Use existing JWT token system**
- **Token payload includes**:
  - `sub`: user ID
  - `email`: user email
  - `auth_provider`: "google" | "telegram" | "both"
- **Token expiration**: Same as current (24 hours)

---

## 🔧 **TECHNICAL REQUIREMENTS**

### **TR1: Backend OAuth Implementation**

#### **Required Libraries**
```python
# Add to backend/requirements.txt
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
```

#### **Environment Variables**
```bash
# .env file
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://putana.date/api/auth/google/callback
```

#### **New API Endpoints**

**1. Initiate Google OAuth**
```
GET /api/auth/google
```
- **Purpose**: Start Google OAuth flow
- **Response**: Redirect to Google OAuth consent screen
- **Implementation**:
  - Generate OAuth state token (CSRF protection)
  - Store state in session/cache
  - Build Google OAuth URL with scopes
  - Return redirect to Google

**2. Google OAuth Callback**
```
GET /api/auth/google/callback?code={code}&state={state}
```
- **Purpose**: Handle Google OAuth callback
- **Parameters**:
  - `code`: Authorization code from Google
  - `state`: CSRF protection token
- **Implementation**:
  - Verify state token
  - Exchange authorization code for access token
  - Fetch user info from Google API
  - Check if user exists (by email or google_id)
  - Create or update user
  - Generate JWT token
  - Redirect to frontend with token: `/?token={jwt_token}`

**3. Link Google Account (for existing users)**
```
POST /api/auth/google/link
```
- **Purpose**: Link Google account to existing user
- **Authentication**: Requires valid JWT token (user must be logged in)
- **Request Body**: Authorization code from Google OAuth
- **Implementation**:
  - Verify user is authenticated
  - Exchange code for Google user info
  - Check if Google account is already linked to another user
  - Add `google_id` to current user
  - Update `auth_provider` to "both"
  - Return success response

### **TR2: Frontend Implementation**

#### **New Components**

**1. GoogleLoginButton Component**
```jsx
// frontend/src/components/GoogleLoginButton.jsx
```
- Google Sign-In button (follows Google's design guidelines)
- Handles click event
- Redirects to `/api/auth/google`

**2. LoginPage Component**
```jsx
// frontend/src/components/LoginPage.jsx
```
- Main login page
- Includes GoogleLoginButton
- Includes Telegram login option
- Link to registration page

**3. AccountLinking Component**
```jsx
// frontend/src/components/AccountLinking.jsx
```
- For logged-in users
- "Link Google Account" button
- Shows current auth providers
- Allows unlinking (if multiple providers exist)

#### **New Routes**
```jsx
// frontend/src/App.js
<Route path="/login" element={<LoginPage />} />
<Route path="/auth/google" element={<GoogleOAuthHandler />} />
```

#### **OAuth Handler Component**
```jsx
// frontend/src/components/GoogleOAuthHandler.jsx
```
- Handles OAuth redirects
- Extracts token from URL
- Stores token in localStorage
- Redirects to dashboard

### **TR3: Database Schema Changes**

#### **User Model Updates**
```python
# backend/server.py - User model
class User(BaseModel):
    # ... existing fields ...
    
    # Google OAuth fields
    google_id: Optional[str] = None  # Google user ID
    google_email: Optional[str] = None  # Google email (if different from primary email)
    google_picture: Optional[str] = None  # Google profile picture URL
    auth_provider: str = "telegram"  # "telegram" | "google" | "both"
    google_linked_at: Optional[datetime] = None  # When Google account was linked
```

#### **MongoDB Indexes**
```python
# Add indexes for efficient lookups
db.users.create_index("google_id")  # For Google ID lookups
db.users.create_index("email")  # For email-based lookups (already exists)
```

### **TR4: Security Requirements**

#### **CSRF Protection**
- Generate random state token for each OAuth request
- Store state in server-side session or Redis cache
- Verify state token on callback
- Token should expire after 10 minutes

#### **Token Storage**
- **Server-side**: Store OAuth state tokens securely
- **Client-side**: Store JWT token in localStorage (same as current implementation)

#### **Secret Management**
- Google Client Secret must be stored in environment variables
- Never expose secrets in frontend code
- Use HTTPS for all OAuth redirects

#### **Scope Validation**
- Only request necessary scopes: `openid`, `email`, `profile`
- Validate that returned user info matches requested scopes

---

## 🔄 **USER FLOWS**

### **Flow 1: New User Registration via Google**

```
1. User visits /login
2. User clicks "Sign in with Google"
3. Redirect to Google OAuth consent screen
4. User grants permission
5. Google redirects to /api/auth/google/callback?code=...&state=...
6. Backend:
   - Verifies state token
   - Exchanges code for access token
   - Fetches user info from Google
   - Checks if user exists (by email/google_id)
   - Creates new user:
     - email: from Google
     - name: from Google profile
     - google_id: Google user ID
     - auth_provider: "google"
     - is_verified: true
     - balance: 0.0
   - Generates JWT token
7. Redirect to /?token={jwt_token}
8. Frontend:
   - Extracts token from URL
   - Stores in localStorage
   - Redirects to /admin (dashboard)
9. User sees dashboard with welcome message
```

### **Flow 2: Existing User Login via Google**

```
1. User visits /login
2. User clicks "Sign in with Google"
3. Redirect to Google OAuth consent screen
4. User grants permission
5. Google redirects to /api/auth/google/callback?code=...&state=...
6. Backend:
   - Verifies state token
   - Exchanges code for access token
   - Fetches user info from Google
   - Finds existing user by email or google_id
   - Updates user info if needed
   - Generates JWT token
7. Redirect to /?token={jwt_token}
8. Frontend stores token and redirects to dashboard
```

### **Flow 3: Link Google to Existing Telegram Account**

```
1. User is logged in via Telegram (has JWT token)
2. User visits /admin (dashboard)
3. User clicks "Link Google Account"
4. Redirect to Google OAuth consent screen
5. User grants permission
6. Google redirects to /api/auth/google/callback?code=...&state=...
7. Backend:
   - Verifies user is authenticated (JWT token)
   - Verifies state token
   - Exchanges code for Google user info
   - Checks if Google account is already linked
   - Adds google_id to current user
   - Updates auth_provider to "both"
8. Redirect to dashboard with success message
9. User can now login with either provider
```

---

## 🔐 **SECURITY CONSIDERATIONS**

### **S1: CSRF Protection**
- ✅ **Required**: State token for each OAuth request
- ✅ **Implementation**: Generate random 32-character token
- ✅ **Storage**: Server-side session or Redis cache
- ✅ **Validation**: Verify state matches on callback
- ✅ **Expiration**: 10-minute TTL

### **S2: Token Security**
- ✅ **JWT Secret**: Use existing JWT_SECRET (already secure)
- ✅ **Token Expiration**: 24 hours (same as current)
- ✅ **HTTPS Only**: All OAuth redirects must use HTTPS
- ✅ **Secure Storage**: Client-side localStorage (acceptable for JWT)

### **S3: Account Linking Protection**
- ✅ **Prevent Duplicate Links**: Check if Google account is already linked
- ✅ **User Verification**: Require JWT authentication for linking
- ✅ **Email Validation**: Ensure Google email matches or is unique

### **S4: Data Privacy**
- ✅ **Minimal Data**: Only request necessary scopes
- ✅ **Data Retention**: Same as Telegram users (infinite retention)
- ✅ **GDPR Compliance**: User can unlink Google account

### **S5: Error Handling**
- ✅ **Invalid State**: Return error, don't proceed
- ✅ **Google API Errors**: Log and return user-friendly message
- ✅ **Account Conflicts**: Handle cases where email already exists

---

## 📊 **INTEGRATION POINTS**

### **I1: Existing User Registration**
- **Location**: `frontend/src/components/UserRegistration.jsx`
- **Change**: Add "Sign in with Google" button to registration page
- **Behavior**: Same as login flow, but creates new account

### **I2: Admin Dashboard**
- **Location**: `frontend/src/components/OTPDashboard.jsx`
- **Change**: Add "Account Settings" section
- **Features**:
  - Show current auth providers
  - "Link Google Account" button (if not linked)
  - "Unlink Google Account" option (if linked)
  - Profile picture from Google (if available)

### **I3: JWT Token System**
- **Location**: `backend/server.py`
- **Change**: Add `auth_provider` to JWT payload
- **Usage**: Same token system, just with additional metadata

### **I4: User Model**
- **Location**: `backend/server.py`
- **Change**: Extend User model with Google fields
- **Compatibility**: Existing Telegram users remain unchanged

---

## 🧪 **TESTING REQUIREMENTS**

### **T1: Unit Tests**
- Test Google OAuth token exchange
- Test user creation from Google data
- Test account linking logic
- Test state token validation

### **T2: Integration Tests**
- Test full OAuth flow (mock Google API)
- Test new user registration via Google
- Test existing user login via Google
- Test account linking flow

### **T3: Security Tests**
- Test CSRF protection (invalid state)
- Test token validation
- Test duplicate account prevention
- Test unauthorized account linking

### **T4: UI Tests**
- Test Google Sign-In button renders
- Test login page navigation
- Test dashboard account linking UI
- Test error message display

---

## 📝 **GOOGLE CLOUD CONSOLE SETUP**

### **Steps to Configure Google OAuth**

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Google+ API (if needed)

2. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Name: "PUTANA.DATE Web Client"
   - Authorized redirect URIs:
     - `https://putana.date/api/auth/google/callback` (production)
     - `http://localhost:55552/api/auth/google/callback` (development)

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - User Type: External (or Internal if Google Workspace)
   - App name: "PUTANA.DATE"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: `openid`, `email`, `profile`
   - Save and continue

4. **Get Credentials**
   - Copy Client ID
   - Copy Client Secret
   - Add to `.env` file

---

## 🎨 **UI/UX REQUIREMENTS**

### **U1: Google Sign-In Button**
- **Design**: Follow [Google's Sign-In Branding Guidelines](https://developers.google.com/identity/branding-guidelines)
- **Size**: Standard button size (recommended 240x50px minimum)
- **Text**: "Sign in with Google" (translated if needed)
- **Icon**: Google logo (official assets)

### **U2: Login Page Layout**
```
┌─────────────────────────────────┐
│      PUTANA.DATE Login          │
├─────────────────────────────────┤
│                                 │
│    [🔵 Sign in with Google]     │
│                                 │
│    ──────── or ────────         │
│                                 │
│    [📱 Sign in with Telegram]   │
│                                 │
│    New user? [Register]         │
│                                 │
└─────────────────────────────────┘
```

### **U3: Dashboard Account Section**
- Show current auth providers (icons)
- "Link Google Account" button (if not linked)
- Profile picture (Google or default)
- Last login method displayed

---

## 📦 **DEPENDENCIES**

### **Backend Dependencies**
```txt
# backend/requirements.txt (add these)
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
```

### **Frontend Dependencies**
```json
// frontend/package.json (may already be installed)
// No additional dependencies needed - use standard fetch API
```

---

## 🚀 **IMPLEMENTATION PHASES**

### **Phase 1: Backend OAuth Setup (Week 1)**
- [ ] Install Google OAuth libraries
- [ ] Configure environment variables
- [ ] Implement `/api/auth/google` endpoint
- [ ] Implement `/api/auth/google/callback` endpoint
- [ ] Update User model with Google fields
- [ ] Test OAuth flow with Google

### **Phase 2: Frontend Login Page (Week 1)**
- [ ] Create GoogleLoginButton component
- [ ] Create LoginPage component
- [ ] Add `/login` route
- [ ] Test UI and navigation

### **Phase 3: Account Linking (Week 2)**
- [ ] Implement `/api/auth/google/link` endpoint
- [ ] Create AccountLinking component
- [ ] Add to dashboard
- [ ] Test account linking flow

### **Phase 4: Testing & Polish (Week 2)**
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Security testing
- [ ] UI/UX polish
- [ ] Documentation

---

## ✅ **ACCEPTANCE CRITERIA**

1. ✅ User can register using Google account
2. ✅ User can login using Google account
3. ✅ Existing Telegram user can link Google account
4. ✅ User can login with either provider after linking
5. ✅ Google profile picture displays in dashboard
6. ✅ CSRF protection works correctly
7. ✅ JWT tokens work with Google authentication
8. ✅ All existing functionality remains intact
9. ✅ Error handling is user-friendly
10. ✅ Code follows KISS principle

---

## 📚 **REFERENCES**

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sign-In Branding Guidelines](https://developers.google.com/identity/branding-guidelines)
- [FastAPI OAuth Example](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- [Python google-auth Library](https://google-auth.readthedocs.io/)

---

## 🔄 **OPEN QUESTIONS**

1. **Multiple Email Support**: Should users be able to link multiple Google accounts?
   - **Proposed**: No, one Google account per user (simpler)

2. **Email Conflict Resolution**: What if Google email matches existing Telegram email?
   - **Proposed**: Link accounts automatically (same email = same user)

3. **Account Deletion**: If user unlinks Google account, should account be deleted?
   - **Proposed**: No, account remains with Telegram auth (if available)

4. **Profile Picture Updates**: Should Google profile picture override Telegram profile picture?
   - **Proposed**: Use Google picture if available, fallback to Telegram or default

5. **Username Generation**: How to generate username for Google users?
   - **Proposed**: Use Google email prefix (before @) or Google name, with uniqueness check

---

**Status**: 📋 **Requirements Document Complete**  
**Next Step**: Review and approve requirements, then proceed with Phase 1 implementation

