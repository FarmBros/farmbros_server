# User Management API Documentation

## Overview

The User Management API provides endpoints for user registration, authentication, and profile management in the FarmBros system. It supports both traditional password-based authentication and Google OAuth signup.

**Base URL:** `/users`

## Authentication

### Authentication Methods

1. **Password-based Authentication** - Traditional username/email and password
2. **Google OAuth** - Sign up/login with Google account
3. **Hybrid** - Users can add both methods to their account

### Token Usage

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Data Model

### User Object

```json
{
  "id": 1,
  "uuid": "user-uuid-1234-5678-90ab-cdef",
  "username": "john_farmer",
  "email": "john@example.com",
  "role": "user",
  "google_id": null,
  "login_type": "PASSWORD",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "bio": "Organic farmer specializing in vegetables",
  "avatar_url": "https://example.com/avatars/john.jpg",
  "phone_number": "+1234567890",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-11-15T10:30:00+00:00",
  "updated_at": "2024-11-15T10:30:00+00:00",
  "last_login": "2024-11-15T15:20:00+00:00",
  "email_verified_at": null,
  "timezone": "UTC",
  "language": "en",
  "theme": "light"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Internal database ID (read-only) |
| `uuid` | String | External unique identifier (UUID format) |
| `username` | String | Unique username (required) |
| `email` | String | Unique email address (required) |
| `role` | String | User role: "user" or "admin" (default: "user") |
| `google_id` | String | Google OAuth ID (if using Google auth) |
| `login_type` | Enum | "PASSWORD", "GOOGLE_AUTH", or "BOTH" |
| `first_name` | String | User's first name |
| `last_name` | String | User's last name |
| `full_name` | String | Auto-generated full name |
| `bio` | Text | User biography/description |
| `avatar_url` | String | Profile picture URL |
| `phone_number` | String | Contact phone number |
| `is_active` | Boolean | Account active status (default: true) |
| `is_verified` | Boolean | Email verification status (default: false) |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `last_login` | DateTime | Last successful login timestamp |
| `email_verified_at` | DateTime | Email verification completion time |
| `timezone` | String | User's timezone (default: "UTC") |
| `language` | String | Preferred language (default: "en") |
| `theme` | String | UI theme preference: "light" or "dark" |

### Roles

- **user** - Standard user with access to their own farms and data
- **admin** - Administrator with access to admin-only endpoints (crop management, statistics, etc.)

### Login Types

- **PASSWORD** - Traditional password-based authentication
- **GOOGLE_AUTH** - Google OAuth authentication only
- **BOTH** - Both password and Google auth enabled

---

## API Endpoints

### 1. Create User (Sign Up)

Create a new user account with password authentication.

**Endpoint:** `POST /users/create`
**Auth Required:** No
**Request Body:**

```json
{
  "username": "john_farmer",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "bio": "Organic farmer",
  "timezone": "America/New_York",
  "language": "en"
}
```

**Required Fields:**
- `username` - Unique username (alphanumeric and underscores)
- `email` - Valid, unique email address
- `password` - Strong password (min 8 characters recommended)

**Optional Fields:**
- `first_name` - First name
- `last_name` - Last name
- `phone_number` - Contact number
- `bio` - User biography
- `timezone` - Timezone identifier (default: "UTC")
- `language` - Language code (default: "en")

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "user-uuid-1234-5678-90ab-cdef",
    "username": "john_farmer",
    "email": "john@example.com",
    "role": "user",
    "login_type": "PASSWORD",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-11-15T10:30:00+00:00"
  },
  "error": null
}
```

**Error Responses:**

```json
{
  "status": "error",
  "data": null,
  "error": "Username already exists"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "Email already registered"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "username, email, and password are required"
}
```

**Notes:**
- Password is hashed using Werkzeug's generate_password_hash
- `full_name` is auto-generated from first_name and last_name
- `login_type` is automatically set to "PASSWORD"
- New users have role "user" by default

---

### 2. Login

Authenticate a user and receive a JWT token.

**Endpoint:** `POST /users/login`
**Auth Required:** No
**Request Body:**

```json
{
  "username": "john_farmer",
  "password": "SecurePassword123!"
}
```

**Alternative (login with email):**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Required Fields:**
- `username` OR `email` - User identifier
- `password` - User's password

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "uuid": "user-uuid-1234-5678-90ab-cdef",
      "username": "john_farmer",
      "email": "john@example.com",
      "role": "user",
      "full_name": "John Doe"
    }
  },
  "error": null
}
```

**Error Responses:**

```json
{
  "status": "error",
  "data": null,
  "error": "Invalid credentials"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "Account is locked. Try again later"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "Account is inactive"
}
```

**Security Features:**
- Failed login attempts are tracked
- Account locks after 5 failed attempts (30-minute lockout)
- Lockout duration: 1800 seconds (30 minutes)
- Last login timestamp is updated on successful login

**Token Usage:**
Store the `access_token` and include it in subsequent requests:
```javascript
headers: {
  'Authorization': `Bearer ${access_token}`
}
```

---

### 3. Google OAuth Signup

Create or login with a Google account.

**Endpoint:** `POST /users/google_signup`
**Auth Required:** No
**Request Body:**

```json
{
  "google_id": "google-user-id-from-oauth",
  "email": "john@gmail.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar_url": "https://lh3.googleusercontent.com/..."
}
```

**Required Fields:**
- `google_id` - Google user ID from OAuth response
- `email` - Email from Google account

**Optional Fields:**
- `first_name` - From Google profile
- `last_name` - From Google profile
- `avatar_url` - Google profile picture URL

**Success Response (New User):**

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "uuid": "user-uuid-1234-5678-90ab-cdef",
      "username": "john_gmail_com",
      "email": "john@gmail.com",
      "role": "user",
      "google_id": "google-user-id-from-oauth",
      "login_type": "GOOGLE_AUTH",
      "full_name": "John Doe",
      "avatar_url": "https://lh3.googleusercontent.com/..."
    },
    "is_new_user": true
  },
  "error": null
}
```

**Success Response (Existing User):**

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {...},
    "is_new_user": false
  },
  "error": null
}
```

**Notes:**
- If user with email already exists, links Google account (login_type becomes "BOTH")
- If new user, username is generated from email
- Auto-sets avatar_url from Google profile picture
- Returns JWT token immediately (auto-login)

---

### 4. Get Current User (Verify Token)

Verify authentication token and get current user data.

**Endpoint:** `POST /users/me`
**Auth Required:** Yes
**Request Body:** `{}` (empty object)

**Success Response:**

```json
{
  "id": 1,
  "uuid": "user-uuid-1234-5678-90ab-cdef",
  "username": "john_farmer",
  "email": "john@example.com",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  ...
}
```

**Error Response:**

```json
{
  "detail": "Invalid credentials"
}
```

**HTTP Status:** 401 Unauthorized

**Use Case:** Verify token on app startup, refresh user data

---

### 5. Verify Admin

Check if current user has admin role.

**Endpoint:** `POST /users/admin`
**Auth Required:** Yes (Admin role)
**Request Body:** `{}` (empty object)

**Success Response (Admin User):**

```json
{
  "id": 1,
  "uuid": "admin-uuid-1234-5678-90ab-cdef",
  "username": "admin_user",
  "email": "admin@example.com",
  "role": "admin",
  ...
}
```

**Error Response (Non-Admin):**

```json
{
  "detail": "Invalid credentials"
}
```

**HTTP Status:** 401 Unauthorized

**Use Case:** Protect admin-only features in frontend

---

## Security Features

### Password Security

- Passwords are hashed using Werkzeug's `generate_password_hash`
- Password strength validation recommended on frontend
- Passwords are never returned in API responses

### Account Lockout

- Failed login attempts are tracked per user
- Account locks after 5 failed attempts
- Lockout duration: 30 minutes (1800 seconds)
- Lockout is automatically lifted after duration
- Successful login resets failed attempt counter

### Email Verification

- Users can have unverified emails (`is_verified: false`)
- Verification token system available (not exposed in current endpoints)
- Email verification fields: `verification_token`, `email_verified_at`

### Password Reset

- Password reset token system available
- Token expiration: configurable (default 1 hour)
- Fields: `reset_token`, `reset_token_expires`
- (Password reset endpoints not yet implemented)

---

## Error Handling

### Common Error Messages

- `"username, email, and password are required"` - Missing required fields
- `"Username already exists"` - Username is taken
- `"Email already registered"` - Email is already in use
- `"Invalid credentials"` - Wrong username/password or unauthorized access
- `"Account is locked. Try again later"` - Too many failed login attempts
- `"Account is inactive"` - User account is deactivated
- `"User not found"` - User doesn't exist

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication failed or required
- `403 Forbidden` - Insufficient permissions
- `409 Conflict` - Duplicate username or email
- `500 Internal Server Error` - Server-side error

---

## Usage Examples

### Example 1: User Registration

```javascript
const response = await fetch('/users/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'john_farmer',
    email: 'john@example.com',
    password: 'SecurePassword123!',
    first_name: 'John',
    last_name: 'Doe',
    timezone: 'America/New_York'
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('User created:', result.data.uuid);
  // Redirect to login page
  window.location.href = '/login';
}
```

### Example 2: User Login

```javascript
const response = await fetch('/users/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'john_farmer',
    password: 'SecurePassword123!'
  })
});

const result = await response.json();
if (result.status === 'success') {
  // Store token in localStorage or secure cookie
  localStorage.setItem('access_token', result.data.access_token);
  localStorage.setItem('user', JSON.stringify(result.data.user));

  // Redirect to dashboard
  window.location.href = '/dashboard';
} else {
  alert(result.error);
}
```

### Example 3: Google OAuth Integration

```javascript
// After Google OAuth callback
const googleUser = gapi.auth2.getAuthInstance().currentUser.get();
const profile = googleUser.getBasicProfile();

const response = await fetch('/users/google_signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    google_id: profile.getId(),
    email: profile.getEmail(),
    first_name: profile.getGivenName(),
    last_name: profile.getFamilyName(),
    avatar_url: profile.getImageUrl()
  })
});

const result = await response.json();
if (result.status === 'success') {
  localStorage.setItem('access_token', result.data.access_token);
  localStorage.setItem('user', JSON.stringify(result.data.user));

  if (result.data.is_new_user) {
    // Redirect to onboarding
    window.location.href = '/onboarding';
  } else {
    // Redirect to dashboard
    window.location.href = '/dashboard';
  }
}
```

### Example 4: Verify Authentication on App Load

```javascript
async function checkAuth() {
  const token = localStorage.getItem('access_token');

  if (!token) {
    // Not logged in
    window.location.href = '/login';
    return;
  }

  try {
    const response = await fetch('/users/me', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (response.status === 401) {
      // Token invalid or expired
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return;
    }

    const user = await response.json();
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  } catch (error) {
    console.error('Auth check failed:', error);
    window.location.href = '/login';
  }
}

// Call on app initialization
checkAuth();
```

### Example 5: Protected API Call

```javascript
async function makeAuthenticatedRequest(endpoint, data) {
  const token = localStorage.getItem('access_token');

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  if (response.status === 401) {
    // Token expired, redirect to login
    localStorage.removeItem('access_token');
    window.location.href = '/login';
    return;
  }

  return await response.json();
}

// Usage
const farms = await makeAuthenticatedRequest('/farms/get_user_farms', {});
```

### Example 6: Admin-Only Feature Protection

```javascript
async function checkAdminAccess() {
  const token = localStorage.getItem('access_token');

  try {
    const response = await fetch('/users/admin', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (response.status === 401) {
      // Not an admin
      alert('You do not have admin access');
      window.location.href = '/dashboard';
      return false;
    }

    return true;
  } catch (error) {
    console.error('Admin check failed:', error);
    return false;
  }
}

// Use before showing admin features
if (await checkAdminAccess()) {
  showAdminPanel();
}
```

---

## Notes for Frontend Development

1. **Token Storage:**
   - Store JWT token securely (localStorage or httpOnly cookies)
   - Never store passwords
   - Clear token on logout
   - Refresh user data periodically

2. **Authentication Flow:**
   - Check token validity on app load
   - Redirect to login if token is invalid/expired
   - Refresh token before expiration (if refresh tokens implemented)

3. **Form Validation:**
   - Validate email format before submission
   - Check username availability (implement endpoint if needed)
   - Enforce password strength requirements
   - Show real-time validation feedback

4. **Error Handling:**
   - Display user-friendly error messages
   - Handle account lockout gracefully (show countdown)
   - Provide password reset option on login failure

5. **Google OAuth:**
   - Use official Google Sign-In library
   - Handle OAuth errors gracefully
   - Support account linking (password + Google)

6. **Role-Based UI:**
   - Show/hide features based on user role
   - Verify admin status before showing admin features
   - Use `/users/admin` endpoint for verification

7. **Security Best Practices:**
   - Never log passwords or tokens
   - Use HTTPS in production
   - Implement CSRF protection
   - Set appropriate CORS headers
   - Implement rate limiting on login endpoint

8. **User Experience:**
   - Show loading states during authentication
   - Persist user session across page refreshes
   - Auto-logout on token expiration
   - Remember user preferences (theme, language, etc.)

9. **Account Management:**
   - Implement email verification flow
   - Add password reset functionality
   - Allow users to update profile information
   - Support account deletion (with confirmation)

10. **Testing:**
    - Test with invalid credentials
    - Test account lockout scenario
    - Test Google OAuth flow
    - Test token expiration handling
