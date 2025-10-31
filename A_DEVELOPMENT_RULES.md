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
- ❌ **NEVER** bypass pre-commit checks

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

### 8. **DEVELOPMENT WORKFLOW**
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

**These rules are now MANDATORY for all future development.**
