# Role-Based System Implementation Plan

## Overview
Implementation of a comprehensive role-based system with data isolation between professors (INSTR-XXXXX) and students (STUD-XXXXX), including OAuth role selection and secure data separation.

## Implementation Status
- [ ] Phase 1: Database & Backend Foundation
- [ ] Phase 2: API Restructuring  
- [ ] Phase 3: OAuth & Registration Updates
- [ ] Phase 4: Frontend Restructuring
- [ ] Phase 5: Security & Testing

## Phase 1: Database & Backend Foundation

### 1.1 Database Migration
**File**: `backend/database/migrations/versions/XXXX_add_user_id_field.py`

**Changes**:
- Add `user_id` field to users table (VARCHAR, unique, indexed)
- Add role validation constraints
- Create indexes for role-based queries

**SQL Changes**:
```sql
ALTER TABLE users ADD COLUMN user_id VARCHAR(15) UNIQUE;
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_user_id ON users(user_id);
```

### 1.2 User Model Updates
**File**: `backend/database/models.py`

**New Functions**:
```python
def generate_user_id(role: str) -> str:
    """Generate role-based user ID: STUD-XXXXX or INSTR-XXXXX"""
    
def validate_user_role(role: str) -> bool:
    """Validate role is student or professor"""
```

**Model Changes**:
- Add `user_id` field to User model
- Update user creation to generate appropriate IDs
- Add role validation

### 1.3 Role-Based Authentication Middleware
**File**: `backend/middleware/role_auth.py` (NEW)

**Functions**:
```python
def require_role(required_role: str)
def require_professor()
def require_student()
def require_admin_or_professor()
```

### 1.4 Data Isolation Utilities
**File**: `backend/utilities/data_isolation.py` (NEW)

**Functions**:
```python
def filter_by_role(db_query, current_user, target_role=None)
def validate_data_access(user, resource_owner_id, allowed_roles)
def get_role_specific_data(user, data_type)
```

## Phase 2: API Restructuring

### 2.1 New API Structure
```
backend/api/
├── common/          # Shared endpoints
│   ├── auth.py      # Authentication endpoints
│   └── profile.py   # User profile management
├── professor/       # Professor-specific endpoints
│   ├── cohorts.py   # Cohort management
│   ├── scenarios.py # Scenario creation/management
│   ├── analytics.py # Teaching analytics
│   └── invitations.py # Student invitation system
├── student/         # Student-specific endpoints
│   ├── simulations.py # Simulation access
│   ├── progress.py  # Progress tracking
│   ├── assignments.py # Assignment access
│   └── notifications.py # Student notifications
└── admin/           # Admin-only endpoints
    └── system.py    # System management
```

### 2.2 Role-Based Endpoint Protection
**Implementation**: Add role middleware to all endpoints
**Security**: Ensure data isolation at API level
**Validation**: Role-based input validation

### 2.3 Professor Invitation System
**New Endpoints**:
```python
# Professor endpoints
@router.post("/professor/cohorts/{cohort_id}/invite")
async def invite_students_to_cohort(
    cohort_id: int,
    invitations: List[StudentInvitation],
    current_user: User = Depends(require_professor)
)

@router.get("/professor/invitations/sent")
async def get_sent_invitations(
    current_user: User = Depends(require_professor)
)

# Student endpoints
@router.get("/student/invitations")
async def get_pending_invitations(
    current_user: User = Depends(require_student)
)

@router.post("/student/invitations/{invitation_id}/respond")
async def respond_to_invitation(
    invitation_id: int,
    response: InvitationResponse,
    current_user: User = Depends(require_student)
)
```

### 2.4 Notification System
**Database Tables**:
- `cohort_invitations` - Store invitation details
- `notifications` - Store user notifications
- `email_queue` - Queue for email notifications

**Notification Types**:
- Cohort invitation received
- Invitation accepted/declined
- Assignment due soon
- Grade posted

## Phase 3: OAuth & Registration Updates

### 3.1 OAuth Flow Updates
**File**: `backend/api/oauth.py`

**Changes**:
- Add role selection step in OAuth callback
- Store role in OAuth state
- Generate appropriate user_id based on role

**New Endpoints**:
```python
@router.post("/google/select-role")
async def select_role_for_oauth(role_data: RoleSelectionRequest)

@router.get("/google/callback-with-role")
async def google_callback_with_role(role: str, ...)
```

### 3.2 Registration Updates
**File**: `backend/main.py`

**Changes**:
- Update `/users/register` to accept role
- Generate user_id based on role
- Add role validation

### 3.3 Schema Updates
**File**: `backend/database/schemas.py`

**New Schemas**:
```python
class RoleSelectionRequest(BaseModel):
    role: Literal["student", "professor"]
    state: str

class UserRegisterWithRole(BaseModel):
    # Existing fields +
    role: Literal["student", "professor"]
```

## Phase 4: Frontend Restructuring

### 4.1 New Frontend Structure
```
frontend/
├── app/
│   ├── (professor)/     # Professor-only routes
│   │   ├── dashboard/
│   │   ├── cohorts/
│   │   │   └── [id]/invite/ # Invite students page
│   │   ├── scenarios/
│   │   └── analytics/
│   ├── (student)/       # Student-only routes
│   │   ├── dashboard/
│   │   ├── simulations/
│   │   ├── assignments/
│   │   └── notifications/ # Notification center
│   ├── (auth)/          # Shared auth routes
│   │   ├── login/
│   │   ├── signup/
│   │   └── role-selection/
│   └── (admin)/         # Admin-only routes
├── components/
│   ├── professor/       # Professor-specific components
│   │   ├── InviteStudentsDialog.tsx
│   │   ├── SentInvitationsList.tsx
│   │   └── CohortManagement.tsx
│   ├── student/         # Student-specific components
│   │   ├── InvitationCard.tsx
│   │   ├── NotificationCenter.tsx
│   │   └── PendingInvitations.tsx
│   ├── common/          # Shared components
│   └── role-based/      # Role selection components
└── lib/
    ├── professor-api.ts # Professor API calls
    ├── student-api.ts   # Student API calls
    ├── admin-api.ts     # Admin API calls
    ├── notification-service.ts # Notification handling
    └── role-utils.ts    # Role utilities
```

### 4.2 Role Selection UI
**New Components**:
- `RoleSelectionDialog.tsx` - Role selection for OAuth
- `RoleBasedSignup.tsx` - Role selection for registration
- `RoleGuard.tsx` - Route protection component

### 4.3 API Integration Updates
**Files**: `frontend/lib/api.ts`, `frontend/lib/auth-context.tsx`

**Changes**:
- Separate API calls by role
- Update authentication context with role
- Add role-based routing logic

## Phase 5: Security & Testing

### 5.1 Security Measures
- Row-level security policies in database
- Role-based foreign key constraints
- Comprehensive input validation
- Rate limiting by role
- Audit logging for role-based operations

### 5.2 Testing Strategy
- Unit tests for role-based functions
- Integration tests for API endpoints
- End-to-end tests for OAuth flow
- Security tests for data isolation
- Cross-role access prevention tests

## Data Isolation Rules

### Professor Access
- ✅ Own scenarios and cohorts
- ✅ Student progress within their cohorts
- ✅ Analytics for their content
- ❌ Cannot access other professors' data
- ❌ Cannot access students outside their cohorts

### Student Access
- ✅ Own simulation progress
- ✅ Assigned scenarios and cohorts
- ❌ Cannot access other students' data
- ❌ Cannot access professor creation tools
- ❌ Cannot access system analytics

### Admin Access
- ✅ Full system access
- ✅ User management
- ✅ System analytics
- ✅ Override capabilities (with logging)

## ID Generation Rules

### Student IDs
- Format: `STUD-` + 9 alphanumeric characters
- Example: `STUD-A1B2C3D4E`
- Uniqueness: Global across all users

### Professor IDs
- Format: `INSTR-` + 9 alphanumeric characters
- Example: `INSTR-X9Y8Z7W6V`
- Uniqueness: Global across all users

## Key Files to Modify

### Backend Files
- `backend/database/models.py` - User model updates
- `backend/database/schemas.py` - Schema updates
- `backend/api/oauth.py` - OAuth role selection
- `backend/main.py` - Registration updates
- `backend/utilities/auth.py` - Role-based auth

### Frontend Files
- `frontend/app/signup/page.tsx` - Role selection UI
- `frontend/lib/auth-context.tsx` - Role context
- `frontend/lib/api.ts` - API updates
- `frontend/lib/google-oauth.ts` - OAuth integration

### New Files to Create
- `backend/middleware/role_auth.py` - Role middleware
- `backend/utilities/data_isolation.py` - Data isolation
- `backend/utilities/id_generator.py` - ID generation
- `backend/services/email_service.py` - Email notification service
- `backend/services/notification_service.py` - In-app notification service
- `backend/api/professor/invitations.py` - Professor invitation endpoints
- `backend/api/student/notifications.py` - Student notification endpoints
- `frontend/components/role-based/` - Role components
- `frontend/components/professor/InviteStudentsDialog.tsx` - Invitation UI
- `frontend/components/student/NotificationCenter.tsx` - Notification UI
- `frontend/lib/role-utils.ts` - Role utilities
- `frontend/lib/notification-service.ts` - Notification handling

## Implementation Order
1. Database migration and model updates
2. ID generation utilities
3. Role-based authentication middleware
4. OAuth role selection
5. Registration updates
6. Frontend role selection UI
7. API restructuring
8. Frontend restructuring
9. **Professor invitation system**
10. **Email and notification services**
11. **Student notification UI**
12. Security testing and validation

## Professor Invitation System Details

### Database Schema Additions
```sql
-- Cohort invitations table
CREATE TABLE cohort_invitations (
    id SERIAL PRIMARY KEY,
    cohort_id INTEGER REFERENCES cohorts(id) ON DELETE CASCADE,
    professor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_email VARCHAR(255) NOT NULL,
    student_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- NULL until accepted
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, accepted, declined, expired
    message TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- invitation, assignment, grade, etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB, -- Additional data like cohort_id, invitation_id, etc.
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email queue table
CREATE TABLE email_queue (
    id SERIAL PRIMARY KEY,
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    email_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    scheduled_at TIMESTAMP DEFAULT NOW(),
    sent_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);
```

### Email Templates
- **Invitation Email**: Welcome message with cohort details and signup link
- **Acceptance Confirmation**: Professor notification when student accepts
- **Assignment Reminder**: Due date notifications
- **Grade Posted**: Grade availability notification

### Notification Types
- `cohort_invitation` - New invitation received
- `invitation_accepted` - Student accepted invitation
- `invitation_declined` - Student declined invitation
- `assignment_due` - Assignment due soon
- `assignment_overdue` - Assignment overdue
- `grade_posted` - Grade available
- `cohort_update` - Cohort information updated

## Notes
- Maintain backward compatibility with existing users
- All existing users will need role assignment
- Gradual migration strategy for existing data
- Comprehensive testing before production deployment
