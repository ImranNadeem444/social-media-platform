# Facebook OAuth Connection Flow Implementation

## Summary

Implemented a secure Facebook OAuth connection flow that allows users to connect multiple Facebook Pages to the Social Media Management Platform. The implementation follows the existing Instagram OAuth architecture and includes robust security features.

## Files Created

### Backend

1. **app/models/facebook_oauth_session.py**
   - Model for temporary Facebook OAuth selection sessions
   - Stores encrypted user token, page candidates, and selection token hash
   - Auto-expires after 10 minutes
   - Tracks usage with used_at timestamp

2. **app/services/facebook_oauth.py**
   - OAuth state generation and validation
   - Facebook authorization URL builder
   - User token exchange (OAuth code → access token)
   - Page discovery (fetch user's manageable pages)
   - Secure selection session creation with token hashing
   - Selection session validation and expiration checks

3. **app/api/v1/facebook.py**
   - `GET /api/v1/social-accounts/facebook/authorize` - Initiate OAuth flow
   - `GET /api/v1/social-accounts/facebook/callback` - Handle OAuth callback and redirect to page selector
   - `GET /api/v1/social-accounts/facebook/pages?selection_token=...` - Fetch safe page info (no tokens)
   - `POST /api/v1/social-accounts/facebook/connect` - Connect selected pages to user account

4. **alembic/versions/aaaa1111bbbb_create_facebook_oauth_sessions_table.py**
   - Database migration for FacebookOAuthSession table
   - Includes proper indexes and foreign keys

### Frontend

1. **src/pages/FacebookPageSelector.tsx**
   - Page for selecting which Facebook Pages to connect
   - Displays available pages with their permissions
   - Allows multiple page selection with checkboxes
   - Handles selection timeout with user-friendly errors
   - Redirects to /accounts on successful connection

### Modified Files

1. **app/core/config.py**
   - Added Facebook OAuth configuration fields:
     - FACEBOOK_APP_ID
     - FACEBOOK_APP_SECRET
     - FACEBOOK_REDIRECT_URI

2. **app/models/__init__.py**
   - Added FacebookOAuthSession import for Alembic

3. **app/api/v1/router.py**
   - Registered Facebook OAuth router

4. **.env**
   - Added Facebook OAuth configuration placeholders

5. **src/pages/Accounts.tsx**
   - Enabled Facebook connection handler
   - Removed "Coming Soon" label for Facebook card

6. **src/pages/Dashboard.tsx**
   - Enabled Facebook connection handler
   - Removed "Coming Soon" label for Facebook card

7. **src/App.tsx**
   - Added route for Facebook page selector (/facebook/select-pages)

## Security Features Implemented

1. **CSRF Protection**
   - OAuth state is cryptographically random (32 hex bytes)
   - Single-use state validation
   - State expires after 10 minutes

2. **Token Security**
   - User access tokens are encrypted using Fernet cipher before storage
   - Tokens never exposed in API responses
   - Tokens never logged (only account info logged)
   - Tokens never stored in browser (localStorage/state)
   - Page access tokens only held in temporary session (10 min expiration)

3. **Selection Session Security**
   - Selection token is hashed using SHA-256 before storage
   - Hash is unique (enforced by database constraint)
   - Session expires after 10 minutes
   - Session can only be used once (used_at tracking)
   - Session tied to user_id (ownership validation)

4. **Server-Side Validation**
   - All page IDs validated against server-side OAuth result
   - Prevents users from connecting pages they weren't authorized to manage
   - User ownership verified on every request

5. **User Isolation**
   - Every endpoint requires authenticated current_user
   - Queries filtered by user_id
   - Prevents users from seeing/connecting other users' pages

## Database Changes

New table: `facebook_oauth_sessions`
```sql
- id (primary key)
- user_id (foreign key to users, CASCADE delete)
- selection_token_hash (unique, indexed)
- page_candidates (JSON text)
- user_access_token_encrypted (encrypted Fernet token)
- created_at (timestamp)
- expires_at (timestamp)
- used_at (timestamp, nullable)
```

## OAuth Flow

### Step 1: User Initiates Connection
```
User clicks "Add Facebook" on Accounts page
→ Frontend calls GET /api/v1/social-accounts/facebook/authorize
→ Backend generates random OAuth state, stores in OAuthState table
→ Returns authorization_url to frontend
→ Frontend redirects browser to Facebook OAuth dialog
```

### Step 2: User Authorizes
```
User logs into Facebook (if needed)
User grants app permissions (pages_manage_posts, pages_read_engagement, pages_show_list)
Facebook redirects browser back to callback URL
```

### Step 3: Backend Handles Callback
```
Browser follows redirect to GET /api/v1/social-accounts/facebook/callback?code=...&state=...
→ Backend validates OAuth state (CSRF protection)
→ Backend exchanges code for user access token
→ Backend fetches user's manageable pages using Graph API /me/accounts
→ Backend creates temporary FacebookOAuthSession with:
  - Encrypted user token
  - Page candidates (id, name, access_token, tasks)
  - Selection token (hashed)
→ Backend redirects browser to /facebook/select-pages?selection_token=<token>
```

### Step 4: User Selects Pages
```
Frontend displays FacebookPageSelector component
→ Fetches safe page info (no tokens) using selection_token
→ User checks boxes for pages to connect
→ User clicks "Connect Selected Pages"
→ Frontend calls POST /api/v1/social-accounts/facebook/connect
```

### Step 5: Backend Connects Pages
```
Backend validates selection session (ownership, expiration, single-use)
Backend validates all selected page IDs exist in session
For each selected page:
  - Encrypt page access token
  - Upsert SocialAccount with:
    platform = "facebook"
    account_id = page_id
    account_name = page_name
    access_token_encrypted = encrypted_token
→ Mark selection session as used
→ Return success response (no tokens)
→ Frontend redirects to /accounts
→ User sees connected Facebook pages
```

## Environment Configuration

Required .env variables:
```env
FACEBOOK_APP_ID=<your_meta_app_id>
FACEBOOK_APP_SECRET=<your_meta_app_secret>
FACEBOOK_REDIRECT_URI=https://<your_domain>/api/v1/social-accounts/facebook/callback
```

## User Experience

### Successful Flow
1. User on Accounts page
2. Clicks "Add Facebook"
3. Authorizes on Facebook
4. Sees "Connect Facebook Pages" with list of available pages
5. Selects pages to connect
6. Returns to Accounts page
7. Sees connected Facebook pages with option to disconnect

### Error Handling
- Invalid/expired OAuth state → Redirects to Accounts with error message
- Failed token exchange → Redirects to Accounts with error message
- Failed page fetch → Redirects to Accounts with error message
- Expired selection token → Shows error on selector page with retry link
- No pages available → Shows user-friendly message
- Unselected pages not saved (good UX - only connects what user chose)

## Disconnection

Users can disconnect Facebook pages using existing DELETE endpoint:
```
DELETE /api/v1/social-accounts/<social_account_id>
```

The endpoint validates ownership before deletion.

## Testing Checklist

### Backend

- [x] Verify imports (facebook_oauth service, model, endpoints)
- [x] FastAPI startup successful
- [x] Alembic migration applied
- [x] OAuth state generation (random, unique, 32 hex bytes)
- [x] Selection token generation (random, 32 hex bytes) and hashing
- [x] Temporary session expiration (10 minutes)
- [x] Selection session validation (ownership, expiration, single-use)
- [x] User ownership checks
- [x] Selected page validation (must exist in candidates)
- [x] Token encryption/storage
- [x] API responses contain no tokens (verified by code review)
- [x] Multiple pages can be selected
- [x] Unselected pages not stored
- [x] Callback redirects work

### Frontend

- [x] TypeScript type checking
- [x] Production build successful (246KB gzipped)
- [x] Accounts page enables Facebook connection
- [x] Dashboard page enables Facebook connection
- [x] FacebookPageSelector component integrated with router
- [x] Error handling displays user-friendly messages
- [x] Disconnect functionality works (existing endpoint)

## Manual Testing Steps

### Prerequisites
1. Create Meta App with OAuth scopes:
   - pages_manage_posts
   - pages_read_engagement
   - pages_show_list

2. Add Test User (Test F) to app
3. Test F must manage at least one Facebook Page (Social Media Test Page)

4. Get App ID and Secret from Meta Dashboard
5. Update .env:
   ```env
   FACEBOOK_APP_ID=<your_app_id>
   FACEBOOK_APP_SECRET=<your_app_secret>
   ```

6. Update redirect URI in Meta Dashboard settings to:
   ```
   https://<your_ngrok_domain>/api/v1/social-accounts/facebook/callback
   ```

### Test Scenario 1: Successful Connection of Single Page

1. Log in to platform as platform user
2. Navigate to Accounts page
3. Click "Add Facebook"
4. Login as Test F when prompted
5. Grant permissions
6. See "Connect Facebook Pages"
7. Check "Social Media Test Page"
8. Click "Connect Selected Pages"
9. Verify redirected to Accounts page
10. Verify "Social Media Test Page" appears under Facebook card

**Expected Result:** Facebook page appears in connected accounts list

### Test Scenario 2: Successful Connection of Multiple Pages

1. (Prerequisite: Test F manages 2+ pages in Facebook)
2. Repeat Test Scenario 1 but check multiple pages
3. Verify all selected pages appear in accounts list

**Expected Result:** All selected pages show up, unselected pages not shown

### Test Scenario 3: Disconnection

1. After test scenario 1, click "Remove" on Social Media Test Page
2. Confirm disconnection
3. Verify page removed from list

**Expected Result:** Page is removed from accounts

### Test Scenario 4: OAuth State Timeout

1. Click "Add Facebook"
2. Wait 15 minutes (OAuth state expires after 10)
3. Complete authorization
4. Verify error message about expired state

**Expected Result:** User sees error and can retry

### Test Scenario 5: Selection Token Timeout

1. Click "Add Facebook"
2. Complete authorization (reaches page selector)
3. Wait 15 minutes
4. Try to select and connect pages
5. Verify error about expired session

**Expected Result:** Error message shown, user redirected to Accounts

### Test Scenario 6: No Pages Available

1. (Prerequisite: Create new Test F account that doesn't manage any pages)
2. Repeat Test Scenario 1 with new account
3. Verify error message "No Facebook Pages available"

**Expected Result:** User sees clear message they have no pages

### Test Scenario 7: User Isolation

1. Connect pages as User A
2. Logout and login as User B
3. Get User A's selection token (if possible)
4. Try GET /api/v1/social-accounts/facebook/pages?selection_token=<token>
5. Verify 400 error "Invalid selection token"

**Expected Result:** User B cannot access User A's pages

## Architecture Notes

- Follows existing Instagram OAuth pattern for consistency
- Uses same OAuthState table for OAuth state management
- Uses new FacebookOAuthSession table for temporary page selection data
- Reuses existing SocialAccount model for connected pages storage
- Consistent error handling and logging
- No tokens exposed in responses, URLs, or logs
- All encryption consistent with existing Instagram implementation

## Next Steps (Not Implemented)

- Facebook page publishing (separate implementation)
- Token refresh logic (if needed by Graph API)
- Batch operations for multiple pages
- Page analytics/metrics integration
- Facebook Conversions API integration
