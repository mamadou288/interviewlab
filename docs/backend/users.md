# Users Module Documentation

## Overview

Email-based authentication module with JWT tokens. Foundation for all other modules, handling registration, login, token management, and permissions.

## Model

**User** (`backend/users/models.py`): Custom model extending `AbstractBaseUser`
- UUID primary key
- Email as USERNAME_FIELD (unique, required)
- Fields: `email`, `first_name`, `last_name`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, `last_login`
- Manager: `CustomUserManager` with `create_user()` and `create_superuser()`

## API Endpoints

Base path: `/api/auth/`

### POST `/api/auth/register`
Register new user. Returns user data + JWT tokens.

**Request**: `{email, password, password2, first_name?, last_name?}`  
**Response**: `{user: {...}, refresh: "...", access: "...", message: "..."}`

### POST `/api/auth/login`
Authenticate and receive JWT tokens.

**Request**: `{email, password}`  
**Response**: `{refresh: "...", access: "...", user: {...}}`

### POST `/api/auth/refresh`
Refresh access token.

**Request**: `{refresh: "..."}`  
**Response**: `{access: "..."}`

### POST `/api/auth/logout`
Logout and blacklist refresh token. Requires authentication.

**Headers**: `Authorization: Bearer <access_token>`  
**Request**: `{refresh: "..."}`  
**Response**: `{message: "Logged out successfully"}`

## Authentication

- **Tokens**: JWT (access: 1 hour, refresh: 7 days)
- **Rotation**: Enabled (refresh tokens rotate on use)
- **Blacklisting**: Enabled (logout blacklists tokens)
- **Claims**: `user_id` (UUID), `email`, `token_type`

## Permission Classes

**`IsOwnerOrReadOnly`**: Read for all authenticated users, write for owners only  
**`IsAuthenticatedOwner`**: Requires authentication + ownership (`obj.user == request.user`)

## Serializers

**`UserRegistrationSerializer`**: Validates password strength, confirms match, creates user  
**`UserSerializer`**: Serializes user data (id, email, first_name, last_name, date_joined, last_login)

## Configuration

- `AUTH_USER_MODEL = 'users.User'` in settings
- JWT config in `SIMPLE_JWT`
- Token blacklist app enabled

## Usage

```python
from users.models import User
from users.permissions import IsOwnerOrReadOnly

# Create user
user = User.objects.create_user(email='test@example.com', password='pass')

# Use in views
class MyView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```
