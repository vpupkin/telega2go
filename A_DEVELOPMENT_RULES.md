# 🚨 DEVELOPMENT RULES - MANDATORY

## ⚠️ **CRITICAL RULES - NO EXCEPTIONS**

### 1. **KISS PRINCIPLE - MANDATORY**
- ✅ **ALWAYS** Keep It Simple, Stupid
- ✅ **ALWAYS** use the simplest solution possible
- ✅ **ALWAYS** one change at a time
- ✅ **ALWAYS** minimal, focused modifications
- ❌ **NEVER** over-engineer solutions
- ❌ **NEVER** use complex methods when simple ones work
- ❌ **NEVER** add unnecessary complexity
- 🚨 **VIOLATION**: Ignoring KISS principle is a CRITICAL RULE VIOLATION

### 2. **NO COMMITS WITHOUT AGREEMENT**
- ❌ **NEVER** commit without explicit user approval
- ❌ **NEVER** make changes without asking first
- ✅ **ALWAYS** ask before any commit
- ✅ **ALWAYS** explain what will be committed

### 3. **NO COMMITS WITHOUT FULLY IMPLEMENTED FEATURE TESTS**
- ❌ **NEVER** commit incomplete features
- ❌ **NEVER** commit untested code
- ✅ **ALWAYS** implement complete features
- ✅ **ALWAYS** test thoroughly before commit
- ✅ **ALWAYS** test all previous tests + new feature tests
- ✅ **ALWAYS** test with running containers (Docker-based app requirement)
- ❌ **NEVER** commit without successful test results

### 4. **PRE-COMMIT RULES ENFORCEMENT**
- ✅ **ALWAYS** run pre-commit hooks before any commit
- ✅ **ALWAYS** ensure all tests pass
- ✅ **ALWAYS** check code quality
- ✅ **ALWAYS** run integration tests after redeployment
- ✅ **ALWAYS** verify no errors before reporting success
- ❌ **NEVER** bypass pre-commit checks
- ❌ **NEVER** report success if errors detected in tests

### 5. **SINGLE DOCKER STARTUP METHOD - MANDATORY**
- ✅ **ONLY** use `./start.sh` to start services
- ✅ **ALWAYS** prefer `./start.sh` for all Docker operations when possible
- ✅ **ALWAYS** use `./start.sh` for: rebuilding, restarting, health checks, backups, rollbacks
- ❌ **NEVER** use `docker-compose` directly
- ❌ **NEVER** use `./docker-simple.sh` or other Docker methods
- ❌ **NEVER** use individual `docker run` commands
- ❌ **NEVER** use `docker build` without rebuilding through start.sh
- ❌ **NEVER** use any other Docker startup method
- ✅ **ALWAYS** use the single, consistent Docker management approach
- 🚨 **VIOLATION**: Using any other Docker method is a CRITICAL RULE VIOLATION

**start.sh Usage:**
- `./start.sh` - Quick start (rebuild OTP Gateway and restart)
- `./start.sh full` - Full deployment with backup
- `./start.sh full test` - Full deployment with tests
- `./start.sh test` - Run tests only
- `./start.sh backup` - Create backup
- `./start.sh rollback` - Rollback to previous backup
- `./start.sh health` - Check service health
- `./start.sh help` - Show all commands

### 6. **NO AUTOMATIC GIT PUSH - MANDATORY**
- ❌ **NEVER** push to remote without explicit user request
- ❌ **NEVER** assume pushing is needed after commit
- ✅ **ALWAYS** commit changes when requested
- ✅ **ALWAYS** wait for user to explicitly ask for push
- ✅ **ALWAYS** inform user that changes are committed and ready to push
- 🚨 **VIOLATION**: Pushing without explicit user request is a CRITICAL RULE VIOLATION

### 7. **MANDATORY TAGGING RULE**
- ✅ **ALWAYS** create a tag when asked to tag the state of development
- ✅ **ALWAYS** use sequential numbering (never less than previous tag)
- ✅ **ALWAYS** include keywords describing the committed changes
- ✅ **ALWAYS** use format: `v{number}-{keyword1}-{keyword2}-{keyword3}`
- ❌ **NEVER** skip tagging when requested
- ❌ **NEVER** use lower numbers than previous tags
- ❌ **NEVER** create tags without descriptive keywords

**Tag Examples:**
- `v1-fix-otp-error-handling`
- `v2-remove-docker-scripts-kiss`
- `v3-add-magic-link-authentication`
- `v4-pwa-registration-system`

### 8. **UI TESTING WITH MCP BROWSER TOOLS**
- ✅ **ALWAYS** use MCP browser tools (Playwright/Chrome DevTools) for UI testing when needed
- ✅ **ALWAYS** trace UI elements by logging DOM texts and UIDs from UI parts
- ✅ **ALWAYS** check network requests when debugging API calls
- ✅ **ALWAYS** take snapshots of page state for debugging
- ✅ **ALWAYS** verify UI elements match expected behavior before reporting success
- ❌ **NEVER** skip UI testing when implementing frontend features
- ❌ **NEVER** assume UI works without visual verification

**MCP Browser Tool Usage:**
- Use `mcp_playwright_browser_navigate` to navigate to pages
- Use `mcp_playwright_browser_snapshot` to capture page state
- Use `mcp_playwright_browser_evaluate` to inspect DOM elements
- Use `mcp_playwright_browser_network_requests` to check API calls
- Use `mcp_chrome-devtools_*` tools for advanced debugging

### 9. **CLEAN FRONTEND URL SEPARATION**
- ✅ **ALWAYS** maintain clean separation of implementation for each URL/route
- ✅ **ALWAYS** create dedicated components for each major URL path
- ✅ **ALWAYS** use React Router for routing (no hardcoded URLs)
- ✅ **ALWAYS** document URL structure and component mapping
- ❌ **NEVER** mix concerns between different routes
- ❌ **NEVER** create monolithic components handling multiple routes

**URL Structure:**
- `/` - Home/Landing page
- `/registrationOfNewUser` - Telegram user registration (with URR_ID support)
- `/admin` - Admin panel (OTP history, user management)
- `/dashboard` - User dashboard (after authentication)
- `/verify-magic-link` - Magic link verification page

**Component Mapping:**
- Each route → Dedicated React component
- Shared components → Reusable UI elements (Button, Input, etc.)
- Route-specific logic → Contained within route component

### 10. **DEVELOPMENT WORKFLOW**
```
1. Identify issue/problem
2. Propose solution (ask for approval)
3. Implement change (KISS principle)
4. Test thoroughly (use ./start.sh test if needed)
5. Rebuild/restart services using ./start.sh
6. Run pre-commit checks
7. Ask for commit approval
8. Commit changes
9. Inform user that changes are committed (DO NOT push automatically)
10. Wait for user to explicitly request push
11. Create tag with sequential number + keywords (if requested)
```

### 9. **CORRECT PORT USAGE - MANDATORY**
- ✅ **ALWAYS** use the correct ports as defined in `docker-compose.yml`
- ✅ **ALWAYS** verify port configuration before testing or accessing services
- ❌ **NEVER** use incorrect ports (e.g., 5573 instead of 55553)
- ❌ **NEVER** hardcode ports without checking `docker-compose.yml`
- 🚨 **VIOLATION**: Using wrong ports is a CRITICAL RULE VIOLATION

**Correct Port Configuration (from docker-compose.yml):**
| Service | External Port | Internal Port | URL |
|---------|---------------|---------------|-----|
| **Frontend PWA** | **55553** | 80 | http://localhost:55553 |
| **Backend API** | **55552** | 8000 | http://localhost:55552 |
| **OTP Gateway** | **55551** | 55155 | http://localhost:55551 |
| **MongoDB** | **55554** | 27017 | mongodb://localhost:55554 |
| **Nginx (Optional)** | 5575 (HTTP), 5576 (HTTPS) | 80, 443 | http://localhost:5575 |

**Port Usage Rules:**
- ✅ **ALWAYS** use `localhost:55553` for frontend (NOT 5573)
- ✅ **ALWAYS** use `localhost:55552` for backend API (NOT 5572)
- ✅ **ALWAYS** use `localhost:55551` for OTP Gateway (NOT 5571)
- ✅ **ALWAYS** verify ports match `docker-compose.yml` before committing
- ✅ **ALWAYS** update test scripts to use correct ports
- ✅ **ALWAYS** check `docker-compose.yml` when in doubt about ports

**For Production/Remote:**
- Frontend: `https://putana.date` (port 80/443)
- Backend API: `https://putana.date/api` (or `https://putana.date:55552/api` if direct access needed)
- OTP Gateway: `https://putana.date/otp` (or `https://putana.date:55551`)

### 11. **ITERATIVE BUG FIXING WORKFLOW - MANDATORY**
- ✅ **ALWAYS** redeploy after fixing bugs on any iteration
- ✅ **ALWAYS** run integration tests and check for errors before reporting success
- ✅ **ALWAYS** document all recognized/detected errors (if any)
- ✅ **ALWAYS** add new errors to error list for next iteration
- ✅ **ALWAYS** iterate until no visible and recognizable errors detected
- ❌ **NEVER** report success or commit if errors are detected
- ❌ **NEVER** skip redeployment after bug fixes
- ❌ **NEVER** skip integration tests before reporting

**Workflow Steps:**
```
1. Fix bug/implement change
2. REDEPLOY (always use ./start.sh)
3. Run integration tests (./start.sh test or manual testing)
4. Check for errors:
   - If errors detected:
     a. Document all errors
     b. Add to error list
     c. Go back to step 1 (fix bugs)
   - If no errors:
     d. Proceed to commit approval
5. Wait for commit confirmation
6. Only then commit and report success
```

**Error Documentation Format:**
- Error type/description
- Location (file, function, line)
- Steps to reproduce
- Expected vs actual behavior
- Priority (critical/high/medium/low)

**Error List Maintenance:**
- Keep track of all detected errors
- Update list after each iteration
- Mark errors as resolved when fixed
- Re-test resolved errors to confirm fix

🚨 **VIOLATION**: Skipping redeployment or tests is a CRITICAL RULE VIOLATION

## 🛠️ **CURRENT SITUATION**

### **Issue**: 500 Internal Server Error in registration
### **Root Cause**: OTP Gateway failure causing backend to throw 500 error
### **Proposed Fix**: Make OTP sending optional for testing (KISS approach)

### **What I Did**:
- Modified backend to handle OTP failures gracefully
- Added fallback response with OTP included for testing
- **DID NOT COMMIT** - waiting for your approval

### **Next Steps** (pending your approval):
1. Rebuild backend container with fix
2. Test the fix thoroughly
3. Run pre-commit checks
4. Ask for commit approval
5. Only then commit

## 📋 **ACKNOWLEDGMENT**

I understand and will follow these rules:
- ✅ **ALWAYS use KISS principle - MANDATORY**
- ✅ No commits without agreement
- ✅ No commits without full testing
- ✅ Always run pre-commit checks
- ✅ Always ask before committing
- ✅ **ONLY use `./start.sh` for Docker operations - MANDATORY**
- ✅ **ALWAYS prefer `./start.sh` for all Docker operations when possible**
- ✅ **ALWAYS use `./start.sh` for rebuilding, restarting, health checks, backups, rollbacks**
- ❌ **NEVER use any other Docker method**
- ✅ **ALWAYS commit changes when requested**
- ❌ **NEVER push to remote without explicit user request**
- ✅ **ALWAYS wait for user to explicitly ask for push**
- ✅ **ALWAYS create tags when requested with sequential numbering + keywords**
- ❌ **NEVER skip tagging or use lower numbers than previous tags**
- ✅ **ALWAYS test all previous tests + new feature tests**
- ✅ **ALWAYS test with running containers (Docker-based app requirement)**
- ❌ **NEVER commit without successful test results**
- ✅ **ALWAYS redeploy after bug fixes (iterative workflow)**
- ✅ **ALWAYS run integration tests and check errors before reporting success**
- ✅ **ALWAYS document all detected errors and add to error list**
- ✅ **ALWAYS iterate until no errors detected (if errors → fix and redeploy)**
- ❌ **NEVER skip redeployment or tests after bug fixes**
- ✅ **ALWAYS use correct ports (5555x) as defined in docker-compose.yml**
- ❌ **NEVER use incorrect ports (557x)**
- ✅ **ALWAYS use MCP browser tools for UI testing when needed**
- ✅ **ALWAYS maintain clean URL/route separation in frontend**

**These rules are now MANDATORY for all future development.**
