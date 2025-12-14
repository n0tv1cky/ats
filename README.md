# uCube.ai Application Tracking System (ATS) - Design Document

## 1. Executive Summary

This document outlines the architecture for an Application Tracking System (ATS) that manages candidate recruitment workflows from resume upload through multiple interview rounds. The system features AI-powered resume parsing, automated interview scheduling, and comprehensive candidate profile management.

## 2. System Overview

### 2.1 Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: Next.js with JavaScript
- **Database**: PostgreSQL
- **Storage**: Google Drive Storage (for resume files)
- **AI/ML**: OpenAI API (gpt-4o-mini) - Phase 2
- **Authentication**: OAuth 2.0 with JWT
- **Email Service**: SendGrid / AWS SES
- **Calendar Integration**: Google Calendar API

### 2.2 Key Features

- Batch resume upload and processing
- AI-powered resume parsing and data extraction
- Multi-stage interview workflow management
- Automated interview scheduling with Google Workspace integration
- Candidate search and filtering
- Objective rating system
- Rejection tracking and management
- Automatic backup to Google Drive

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────┐
│   Next.js   │
│   Frontend  │
└──────┬──────┘
       │
       │ REST API
       │
┌──────▼─────────────────────────────┐
│         Python Backend             │
│  ┌──────────────────────────────┐  │
│  │   API Layer (FastAPI)        │  │
│  └──────────┬───────────────────┘  │
│             │                      │
│  ┌──────────▼───────────────────┐  │
│  │   Business Logic Layer       │  │
│  │  - Resume Processing         │  │
│  │  - AI Integration            │  │
│  │  - Interview Management      │  │
│  │  - Notification Service      │  │
│  └──────────┬───────────────────┘  │
│             │                      │
│  ┌──────────▼───────────────────┐  │
│  │   Data Access Layer          │  │
│  └──────────┬───────────────────┘  │
└─────────────┼──────────────────────┘
              │
     ┌────────┴────────┐
     │                 │
┌────▼─────┐    ┌─────▼──────┐
│PostgreSQL│    │ Google Drive│
│ Database │    │ Storage    │
└──────────┘    └────────────┘

```

## 4. Database Schema

### 4.1 Core Tables

### users

- id (PK)
- email (unique, indexed)
- username
- role (admin, interviewer, hr)
- oauth_provider
- oauth_id
- is_active (boolean, default: true)
- deleted_at (nullable timestamp, soft delete)
- created_at
- updated_at

**Indexes:**

- email (unique index)
- oauth_provider + oauth_id (composite unique index)
- is_active

### candidates

- id (PK)
- name
- email (indexed)
- phone_number
- location
- years_of_experience
- current_salary
- expected_salary
- resume_url
- status (eligible, rejected, hired, indexed)
- source (linkedin, naukri, referral)
- objective_rating (float, nullable)
- remarks (text, nullable)
- uploaded_by (FK -> users.id)
- upload_date (indexed)
- deleted_at (nullable timestamp, soft delete)
- created_at
- updated_at

**Indexes:**

- email (index)
- status (index)
- upload_date (index)
- uploaded_by (index)
- created_at (index for sorting)

### resume_buckets

- id (PK)
- name (AI, Full Stack, DevOps, Sales, Operations, HR, etc.)
- description
- created_at

### candidate_buckets

- candidate_id (FK -> candidates.id)
- bucket_id (FK -> resume_buckets.id)
- created_at

**Indexes:**

- candidate_id + bucket_id (composite unique index)
- candidate_id (index)
- bucket_id (index)

### interview_rounds

- id (PK)
- candidate_id (FK -> candidates.id, indexed)
- round_number (0, 1, 2, 3, 4)
  - 0: Resume Screening (no interview)
  - 1: Phone Screen
  - 2: Technical
  - 3: Task Based
  - 4: Behavioural
- round_name (Phone Screen, Technical, Task Based, Behavioural)
- status (scheduled, completed, cancelled, indexed)
- scheduled_date (indexed)
- duration (integer, minutes)
- interviewer_id (FK -> users.id)
- meeting_link
- meeting_notes_url (Google Drive)
- calendar_event_id (string, nullable, for Google Calendar sync)
- calendar_synced_at (timestamp, nullable)
- calendar_deleted_externally (boolean, default: false)
- current_ctc
- expected_ctc
- notice_period
- deleted_at (nullable timestamp, soft delete)
- created_at
- updated_at

**Indexes:**

- candidate_id (index)
- candidate_id + round_number (composite unique index)
- scheduled_date (index)
- status (index)
- interviewer_id (index)
- calendar_event_id (index)

### interview_feedback

- id (PK)
- interview_round_id (FK -> interview_rounds.id)
- interviewer_id (FK -> users.id)
- technical_proficiency_score (0-100, 40% weight)
- attitude_score (0-100, 20% weight)
- code_cleanliness_score (0-100, 20% weight)
- communication_score (0-100, 20% weight)
- overall_rating (calculated)
- feedback_text
- decision (eligible, rejected)
- created_at
- updated_at

### rejections

- id (PK)
- candidate_id (FK -> candidates.id)
- rejected_by (FK -> users.id)
- rejection_date
- rejection_reason
- stage (resume_screening, interview_round)
- round_number (if applicable)
- notes
- created_at

### reapplication_alerts

- id (PK)
- candidate_id (FK -> candidates.id)
- original_rejection_id (FK -> rejections.id)
- reapplication_date
- notified (boolean)
- created_at

### search_logs

- id (PK)
- user_id (FK -> users.id)
- search_query
- search_filters (JSON)
- results_count
- created_at

**Indexes:**

- user_id (index)
- created_at (index)

### skills

- id (PK)
- name (unique)
- category (technical, soft, language, framework, tool, etc.)
- created_at
- updated_at

**Indexes:**

- name (unique index)
- category (index)

### candidate_skills

- id (PK)
- candidate_id (FK -> candidates.id)
- skill_id (FK -> skills.id)
- proficiency_level (beginner, intermediate, advanced, expert, nullable)
- created_at

**Indexes:**

- candidate_id + skill_id (composite unique index)
- candidate_id (index)
- skill_id (index)

### notifications

- id (PK)
- user_id (FK -> users.id)
- type (interview_scheduled, feedback_submitted, calendar_event_deleted, rejection_notice, etc.)
- title (string)
- message (text)
- related_resource_type (candidate, interview, etc., nullable)
- related_resource_id (integer, nullable)
- read (boolean, default: false)
- created_at
- read_at (timestamp, nullable)

**Indexes:**

- user_id (index)
- user_id + read (composite index)
- created_at (index)
- type (index)

### candidate_notes

- id (PK)
- candidate_id (FK -> candidates.id)
- user_id (FK -> users.id)
- note (text)
- is_internal (boolean, default: true)
- deleted_at (nullable timestamp, soft delete)
- created_at
- updated_at

**Indexes:**

- candidate_id (index)
- user_id (index)
- created_at (index)

### audit_logs

- id (PK)
- user_id (FK -> users.id, nullable)
- action (create, update, delete, view, login, logout)
- resource_type (candidate, interview, feedback, user, etc.)
- resource_id (integer, nullable)
- changes (JSON, nullable - stores before/after values)
- ip_address (string, nullable)
- user_agent (string, nullable)
- created_at

**Indexes:**

- user_id (index)
- resource_type + resource_id (composite index)
- action (index)
- created_at (index)

### refresh_tokens

- id (PK)
- user_id (FK -> users.id)
- token (string, unique, indexed)
- expires_at (timestamp)
- revoked (boolean, default: false)
- revoked_at (timestamp, nullable)
- ip_address (string, nullable)
- user_agent (string, nullable)
- created_at

**Indexes:**

- token (unique index)
- user_id (index)
- expires_at (index)
- user_id + revoked (composite index)

## 5. Project Structure

### 5.1 Root Directory Structure

```
.
├── services/
│   ├── backend/
│   │   ├── src/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api/              # API endpoints
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py
│   │   │       │   ├── candidates.py
│   │   │       │   ├── resumes.py
│   │   │       │   ├── interviews.py
│   │   │       │   ├── feedback.py
│   │   │       │   └── search.py
│   │   │       ├── core/             # Core business logic
│   │   │       │   ├── __init__.py
│   │   │       │   ├── security.py   # Authentication & authorization
│   │   │       │   ├── resume_parser.py
│   │   │       │   ├── ai_service.py # AI integration (Phase 2)
│   │   │       │   ├── interview_manager.py
│   │   │       │   └── notification_service.py
│   │   │       ├── services/         # External service integrations
│   │   │       │   ├── __init__.py
│   │   │       │   ├── google_workspace.py
│   │   │       │   ├── email_service.py
│   │   │       │   ├── storage_service.py
│   │   │       │   └── backup_service.py
│   │   │       ├── models/           # SQLAlchemy models
│   │   │       │   ├── __init__.py
│   │   │       │   ├── user.py
│   │   │       │   ├── candidate.py
│   │   │       │   ├── interview.py
│   │   │       │   ├── feedback.py
│   │   │       │   └── rejection.py
│   │   │       ├── schemas/          # Pydantic schemas
│   │   │       │   ├── __init__.py
│   │   │       │   ├── user.py
│   │   │       │   ├── candidate.py
│   │   │       │   ├── interview.py
│   │   │       │   └── feedback.py
│   │   │       ├── db/               # Database
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py
│   │   │       │   ├── session.py
│   │   │       │   └── migrations/   # Alembic migrations
│   │   │       ├── config.py         # Configuration management
│   │   │       ├── dependencies.py   # Dependency injection
│   │   │       └── utils/            # Utility functions
│   │   │           ├── __init__.py
│   │   │           ├── validators.py
│   │   │           └── helpers.py
│   │   └── main.py                   # FastAPI application entry point
│   │
│   └── frontend/
│       ├── public/
│       │   └── assets/
│       ├── src/
│       │   ├── app/                  # Next.js 13+ app directory
│       │   │   ├── layout.js
│       │   │   ├── page.js           # Dashboard
│       │   │   ├── auth/
│       │   │   │   └── page.js       # OAuth sign-in
│       │   │   ├── candidates/
│       │   │   │   ├── page.js        # Candidate list
│       │   │   │   ├── [id]/
│       │   │   │   │   └── page.js   # Candidate profile
│       │   │   │   └── upload/
│       │   │   │       └── page.js    # Batch upload
│       │   │   ├── interviews/
│       │   │   │   ├── page.js       # Interview schedule
│       │   │   │   └── [id]/
│       │   │   │       └── page.js   # Interview details
│       │   │   └── search/
│       │   │       └── page.js       # Advanced search
│       │   │
│       │   ├── components/           # Reusable components
│       │   │   ├── layout/
│       │   │   │   ├── Header.js
│       │   │   │   ├── Sidebar.js
│       │   │   │   └── Footer.js
│       │   │   ├── candidates/
│       │   │   │   ├── CandidateCard.js
│       │   │   │   ├── CandidateProfile.js
│       │   │   │   ├── ResumeUploader.js
│       │   │   │   └── CandidateSearch.js
│       │   │   ├── interviews/
│       │   │   │   ├── InterviewCard.js
│       │   │   │   ├── InterviewScheduler.js
│       │   │   │   ├── FeedbackForm.js
│       │   │   │   └── RoundTimeline.js
│       │   │   └── common/
│       │   │       ├── Button.js
│       │   │       ├── Input.js
│       │   │       ├── Modal.js
│       │   │       └── LoadingSpinner.js
│       │   │
│       │   ├── lib/                  # Utility libraries
│       │   │   ├── api.js            # API client
│       │   │   ├── auth.js           # Authentication helpers
│       │   │   └── utils.js          # Helper functions
│       │   │
│       │   ├── hooks/                # Custom React hooks
│       │   │   ├── useAuth.js
│       │   │   ├── useCandidates.js
│       │   │   └── useInterviews.js
│       │   │
│       │   ├── context/              # React Context
│       │   │   ├── AuthContext.js
│       │   │   └── ThemeContext.js
│       │   │
│       │   └── styles/               # Global styles
│       │       └── globals.css
│       │
│       ├── package.json
│       ├── next.config.js
│       └── README.md
│
├── docker-compose.prod.yaml          # Production Docker Compose
├── docker-compose.dev.yaml           # Development Docker Compose
├── env_files/                        # Environment configuration files
│   ├── .env.dev                      # Development environment variables
│   └── .env.prod                     # Production environment variables
├── docs/                             # Documentation
├── tests/                            # Integration and E2E tests
├── output/                           # Build outputs and generated files
├── scripts/                          # Utility scripts
├── Makefile                          # Build and deployment commands
└── README.md                         # Project documentation

```

## 6. Backend Architecture

### 6.1 Backend Directory Structure

The backend follows the structure under `services/backend/`:

- `main.py` is the FastAPI application entry point at the root of `services/backend/`
- All source code is organized under `src/v1/` for API version 1
- Future API versions can be added as `src/v2/`, `src/v3/`, etc.

### 6.2 Key Backend Components

### Resume Parser Service

```python
class ResumeParserService:
    - parse_resume(file_path) -> dict
    - extract_contact_info(text) -> dict
    - extract_experience(text) -> dict
    - extract_skills(text) -> list
    - categorize_bucket(skills, experience) -> str
    - predict_salary(experience, location, skills) -> float

```

### AI Service

```python
class AIService:
    - calculate_years_of_experience(resume_text) -> int
    - predict_current_salary(profile_data) -> float
    - rate_resume(resume_text, job_requirements) -> float
    - analyze_feedback(feedback_text) -> dict

```

### Interview Manager

```python
class InterviewManager:
    - schedule_interview(candidate_id, round, interviewer_id) -> Interview
    - create_calendar_event(interview_data) -> str
    - fetch_meeting_notes(drive_url) -> str
    - notify_participants(interview) -> bool
    - check_reapplication(candidate_email) -> bool

```

### Notification Service

```python
class NotificationService:
    - send_email(to, subject, body, attachments)
    - send_interview_invite(interview, candidate, interviewer)
    - send_rejection_notice(candidate, reason)
    - send_reapplication_alert(hr_team, candidate)

```

## 7. Frontend Architecture

### 7.1 Frontend Directory Structure

The frontend follows the structure under `services/frontend/` as shown in the root directory structure above.

### 7.2 Key Frontend Components

### Resume Upload Flow

- Multi-file drag-and-drop interface
- Bucket selection dropdown
- Progress indicator for batch processing
- Status updates via polling or page refresh

### Candidate Profile View

- Displays all extracted data
- Edit capability for corrections
- Resume preview/download
- Interview history timeline
- Status management (Eligible/Rejected)
- Notes and remarks section

### Interview Management

- Calendar view of scheduled interviews
- Scheduling form with Google Calendar integration
- Feedback form with weighted scoring
- Auto-population of candidate data
- Meeting notes attachment from Google Drive

### Search & Filter

- Advanced search by name, date, remarks, skills
- Filter by bucket, status, round
- Objective rating display
- Export functionality

## 8. API Endpoints

### 8.1 Health & Readiness

```
GET    /health                         # Health check endpoint
GET    /ready                          # Readiness check endpoint
```

**Response Format:**

```json
{
  "status": "healthy" | "unhealthy",
  "timestamp": "2025-11-12T10:00:00Z",
  "version": "1.0.0"
}
```

### 8.2 Authentication

```
POST   /api/v1/auth/login              # OAuth login
POST   /api/v1/auth/logout             # Logout
POST   /api/v1/auth/refresh            # Refresh access token
GET    /api/v1/auth/me                 # Get current user
```

**Authentication Details:**

- OAuth 2.0 flow with Google Workspace
- JWT access tokens (15 minutes expiration)
- JWT refresh tokens (7 days expiration, stored in database)
- Refresh tokens stored in `refresh_tokens` table for revocation
- HTTP-only cookies for refresh tokens (optional, can use Authorization header)
- Access tokens in Authorization header: `Bearer <token>`

**Token Structure:**

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin|hr|interviewer",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Role-Based Access Control (RBAC):**

**Admin:**

- Full access to all endpoints
- User management
- System configuration
- View all audit logs

**HR:**

- Upload resumes
- View all candidates
- Schedule interviews
- Reject candidates
- View all interviews
- Manage buckets
- View notifications

**Interviewer:**

- View assigned candidates
- Submit feedback for assigned interviews
- View own scheduled interviews
- View candidate profiles for assigned interviews
- Update interview status (completed, cancelled)

### 8.3 Candidates

```
POST   /api/v1/candidates/upload       # Batch upload resumes
GET    /api/v1/candidates              # List candidates (with filters, paginated)
GET    /api/v1/candidates/{id}         # Get candidate details
PUT    /api/v1/candidates/{id}         # Update candidate
DELETE /api/v1/candidates/{id}         # Soft delete candidate
POST   /api/v1/candidates/{id}/reject  # Reject candidate
GET    /api/v1/candidates/search       # Advanced search (paginated)
POST   /api/v1/candidates/{id}/notes   # Add note to candidate
GET    /api/v1/candidates/{id}/notes   # Get candidate notes
```

**Pagination Parameters (for list endpoints):**

- `page` (integer, default: 1, min: 1)
- `page_size` (integer, default: 20, min: 1, max: 100)
- `sort_by` (string, default: "created_at")
- `sort_order` (string, enum: "asc", "desc", default: "desc")

**Pagination Response:**

```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

**File Upload Limits:**

- Max file size: 10MB per resume
- Allowed file types: PDF, DOCX only
- Max batch size: 50 files per upload request
- File validation: MIME type and extension check

**Error Response Format:**

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "additional context"
    }
  }
}
```

**Common Error Codes:**

- `VALIDATION_ERROR`: Request validation failed
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict (e.g., duplicate email)
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `INVALID_FILE_TYPE`: File type not allowed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

### 8.4 Resumes

```
POST   /api/v1/resumes/parse           # Parse single resume
GET    /api/v1/resumes/{id}/download   # Download resume file (signed URL)
```

### 8.5 Interviews

```
POST   /api/v1/interviews              # Schedule interview
GET    /api/v1/interviews              # List interviews (paginated)
GET    /api/v1/interviews/{id}         # Get interview details
PUT    /api/v1/interviews/{id}         # Update interview
DELETE /api/v1/interviews/{id}         # Soft delete interview
POST   /api/v1/interviews/{id}/feedback # Submit feedback
GET    /api/v1/interviews/{id}/notes   # Fetch meeting notes
POST   /api/v1/interviews/sync-calendar # Sync calendar events (admin only)
```

### 8.6 Buckets

```
GET    /api/v1/buckets                 # List all buckets
POST   /api/v1/buckets                 # Create bucket (admin/HR only)
PUT    /api/v1/buckets/{id}            # Update bucket (admin/HR only)
DELETE /api/v1/buckets/{id}            # Delete bucket (admin only)
```

### 8.7 Skills

```
GET    /api/v1/skills                  # List all skills (paginated)
POST   /api/v1/skills                  # Create skill (admin/HR only)
GET    /api/v1/candidates/{id}/skills   # Get candidate skills
POST   /api/v1/candidates/{id}/skills  # Add skills to candidate
DELETE /api/v1/candidates/{id}/skills/{skill_id} # Remove skill from candidate
```

### 8.8 Notifications

```
GET    /api/v1/notifications           # Get user notifications (paginated)
GET    /api/v1/notifications/unread    # Get unread notifications count
PUT    /api/v1/notifications/{id}/read # Mark notification as read
PUT    /api/v1/notifications/read-all  # Mark all as read
DELETE /api/v1/notifications/{id}      # Delete notification
```

### 8.9 Audit Logs

```
GET    /api/v1/audit-logs              # Get audit logs (admin only, paginated)
GET    /api/v1/audit-logs/{resource_type}/{resource_id} # Get logs for resource
```

### 8.10 API Versioning

- Current version: `v1`
- Version specified in URL path: `/api/v1/...`
- Backward compatibility maintained for 6 months after new version release
- Deprecation warnings in response headers: `X-API-Deprecated: true`, `X-API-Sunset-Date: 2025-05-12`

### 8.11 Feedback

```
POST   /api/v1/feedback                # Submit interview feedback
GET    /api/v1/feedback/{interview_id} # Get feedback for interview
PUT    /api/v1/feedback/{id}           # Update feedback (before decision)
```

## 9. Key Workflows

### 9.1 Resume Upload & Processing Workflow

1. User signs in with OAuth
2. User selects bucket category and uploads multiple resumes
3. Backend stores files in Google Drive Storage
4. Manual data entry or basic parsing (Phase 2: AI-powered parsing with OpenAI gpt-4o-mini):
   - Extract name, phone, email, location, YOE (manual entry for now)
   - Skills extraction (manual entry for now)
   - Phase 2: Predict current salary based on profile data
   - Phase 2: Rate resume quality
   - Phase 2: Alert if candidate has applied before (reapplication detection)
5. Create candidate profile for each resume
6. Store in database with metadata
7. Send confirmation email to uploader
8. Backup profile to Google Drive
9. Create audit log entry for upload action

### 9.2 Interview Scheduling Workflow

1. Interviewer views eligible candidates
2. Clicks on candidate profile
3. Selects "Eligible" status
4. System determines next interview round:
   - Round 0: Resume Screening (no interview, just status change)
   - Round 1: Phone Screen (first interview)
   - Round 2: Technical (after Round 1 completion)
   - Round 3: Task Based (after Round 2 completion)
   - Round 4: Behavioural (after Round 3 completion)
5. System prompts for next interview round timing
6. Auto-populates scheduling form with:
   - Candidate details from profile
   - Interviewer remarks
   - Extracted data
   - Job Description link: https://drive.google.com/drive/folders/14NA-hhiIwQvIvxME0b49iq4NsU1Qp4Kv?usp=drive_link
7. Creates Google Calendar event
8. Attaches resume to calendar invite
9. Attaches Job Description link to calendar invite description
10. Fills meeting title with job description title
11. Invites interview-panel@ucube.ai and candidate
12. Stores interview record in database with `calendar_event_id`
13. Records `calendar_synced_at` timestamp

### 9.3 Feedback & Decision Workflow

1. After interview, interviewer submits feedback form
2. Scores entered for:
   - Technical Proficiency (40%)
   - Attitude (20%)
   - Code Cleanliness (20%)
   - Communication (20%)
3. System calculates overall rating
4. Interviewer marks as "Eligible" or "Rejected"
5. If Rejected:
   - Store in rejections table
   - Record date, timestamp, rejector, reason
   - Send notification to candidate
6. If Eligible:
   - Move to next round
   - Repeat scheduling workflow

### 9.4 Reapplication Alert Workflow

**Note: This feature is planned for Phase 2**

1. System monitors new candidate uploads
2. Checks email/phone against rejections table
3. If match found:
   - Alert HR team via notification
   - Display previous rejection details
   - Show previous interview history
   - Allow decision to proceed or auto-reject

## 10. Integration Requirements

### 10.1 Google Workspace Integration

- **Google Calendar API**: Create events, manage invites
  - Calendar sync runs every 2 hours (configurable via `CALENDAR_SYNC_INTERVAL` env var)
  - If calendar event is deleted externally, system detects it and:
    - Sets `calendar_deleted_externally = true` on interview_rounds record
    - Creates notification for HR/admin users
    - Stores event in audit_logs
  - No timezone handling required (use system default)
  - No calendar conflict detection
  - No recurring interview support
- **Google Drive API**: Store backups, fetch meeting notes
- **Google OAuth 2.0**: User authentication

### 10.2 AI/ML Services

**Note: AI features are planned for Phase 2**

- **OpenAI API**: gpt-4o-mini for resume parsing, text extraction
- **Future Features**:
  - Salary prediction based on experience, location, skills
  - Years of experience calculation
  - Resume rating and scoring
  - Skills extraction and categorization

### 10.3 Email Services

- **SendGrid/AWS SES**: Interview invites, rejection notices
- **Template Management**: Predefined email templates

## 11. Security Considerations

### 11.1 Data Protection

- HTTPS for all API communications
- OAuth 2.0 for authentication
- JWT tokens with expiration (15 min access, 7 day refresh)
- Role-based access control (RBAC)
- Soft deletes for data retention and recovery
- Audit logging for all data access and modifications

### 11.2 File Security

- Virus scanning on upload
- File type validation (PDF, DOCX only)
- Signed URLs for resume downloads
- Automatic file expiration in temporary storage

### 11.3 Privacy Compliance

- GDPR compliance for candidate data
- Data retention policies (configurable per data type)
- Right to be forgotten implementation (hard delete after soft delete)
- Comprehensive audit logs for data access and modifications
- Audit logs include: user, action, resource, IP address, user agent, timestamp

## 12. Performance Optimization

### 12.1 Backend

- Database indexing on frequently queried fields (see schema section for index details)
- Redis caching for search results (optional, Phase 2)
- Async processing for resume parsing (background tasks)
- Connection pooling for database (SQLAlchemy pool)
- Rate limiting on API endpoints (100 requests/minute per user)
- Pagination on all list endpoints

### 12.2 Frontend

- Next.js SSR for initial page load
- Image optimization with Next.js Image
- Code splitting and lazy loading
- Client-side caching with SWR/React Query
- Pagination for large datasets

### 12.3 Storage

- CDN for static assets
- Compressed file storage
- Lazy loading for resume previews

## 13. Monitoring & Logging

### 13.1 Application Monitoring

- Error tracking (Sentry)
- Performance monitoring (New Relic/DataDog)
- API request logging
- Database query performance tracking

### 13.2 Business Metrics

- Number of resumes processed
- Average time per interview round
- Conversion rates by bucket
- Interviewer feedback patterns
- Reapplication frequency

## 14. Deployment Strategy

### 14.1 Infrastructure

- **Backend**: AWS EC2/ECS or Google Cloud Run
- **Frontend**: Vercel or AWS Amplify
- **Database**: AWS RDS (PostgreSQL) or Google Cloud SQL
- **Storage**: AWS S3 or Google Cloud Storage
- **CDN**: CloudFront or Cloud CDN

### 14.2 CI/CD Pipeline

- GitHub Actions or GitLab CI
- Automated testing on PR
- Staging environment for QA
- Blue-green deployment for zero downtime

### 14.3 Environment Management

- Development, Staging, Production environments
- Environment-specific configuration files:
  - `.env.dev` in `./env_files/` directory
  - `.env.prod` in `./env_files/` directory
- Secrets management (AWS Secrets Manager / Google Secret Manager)
- Environment variables loaded from appropriate file based on `ENVIRONMENT` variable

**Required Environment Variables:**

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ats_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
OAUTH_GOOGLE_CLIENT_ID=your-client-id
OAUTH_GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# Google Workspace
GOOGLE_CALENDAR_ID=primary
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
CALENDAR_SYNC_INTERVAL=7200  # seconds (2 hours)
GOOGLE_SERVICE_ACCOUNT_KEY=path-to-service-account.json

# Storage
GOOGLE_DRIVE_STORAGE_ENABLED=true
RESUME_STORAGE_PATH=/resumes

# Email
EMAIL_SERVICE=sendgrid  # or ses
SENDGRID_API_KEY=your-api-key
AWS_SES_REGION=us-east-1

# OpenAI (Phase 2)
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini

# Application
ENVIRONMENT=development  # development, staging, production
API_VERSION=v1
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document
MAX_BATCH_SIZE=50

# Initial Admin User
ADMIN_EMAIL=admin@ucube.ai
ADMIN_PASSWORD=change-me-in-production
ADMIN_USERNAME=admin
```

### 14.4 Initial Setup

**Database Initialization:**

- Run Alembic migrations on first deployment
- Seed initial data:
  - Default buckets (AI, Full Stack, DevOps, Sales, Operations, HR)
  - Initial admin user (from environment variables)
  - Default skills (optional, can be added via API)

**Initial Admin User:**

- Created from environment variables: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME`
- Role: `admin`
- Must change password on first login (if password-based auth is used)
- Can be created via database migration or startup script

## 15. Data Validation Rules

### 15.1 Candidate Data Validation

- **Email**: Valid email format, unique per candidate
- **Phone Number**: International format supported (E.164 recommended)
- **Name**: Required, min 2 characters, max 100 characters
- **Years of Experience**: Integer, 0-50 range
- **Current Salary**: Numeric, positive, optional
- **Expected Salary**: Numeric, positive, optional
- **Status**: Enum (eligible, rejected, hired) - validated transitions
- **Source**: Enum (linkedin, naukri, referral, other)
- **Resume File**: PDF or DOCX, max 10MB, virus scanned

### 15.2 Interview Data Validation

- **Round Number**: Integer, 0-4, must be sequential (can't skip rounds)
- **Status**: Enum (scheduled, completed, cancelled)
- **Scheduled Date**: Future date for new interviews, required for scheduled status
- **Duration**: Integer, 15-480 minutes (15 min to 8 hours)
- **Interviewer ID**: Must be active user with interviewer or admin role
- **Status Transitions**:
  - `scheduled` → `completed` or `cancelled`
  - `cancelled` → `scheduled` (reschedule)
  - Cannot transition from `completed` to `scheduled` (create new round instead)

### 15.3 Feedback Data Validation

- **Scores**: Integer, 0-100 range for all score fields
- **Overall Rating**: Calculated automatically, cannot be set manually
- **Decision**: Enum (eligible, rejected) - required after interview completion
- **Feedback Text**: Optional, max 5000 characters
- **Weight Validation**:
  - Technical Proficiency: 40%
  - Attitude: 20%
  - Code Cleanliness: 20%
  - Communication: 20%
  - Total must equal 100%

### 15.4 User Data Validation

- **Email**: Valid email format, unique, required
- **Username**: Alphanumeric + underscore, 3-50 characters, unique
- **Role**: Enum (admin, interviewer, hr), required
- **OAuth Provider**: Required if OAuth authentication used
- **OAuth ID**: Required if OAuth authentication used, unique per provider

### 15.5 Status Transition Rules

**Candidate Status:**

- `eligible` → `rejected` (via rejection endpoint)
- `eligible` → `hired` (manual update)
- `rejected` → `eligible` (requires reapplication workflow - Phase 2)
- Cannot directly transition to `hired` from `rejected`

**Interview Status:**

- Must complete previous round before scheduling next round
- Cannot schedule round N+1 if round N is not completed
- Round 0 (Resume Screening) has no interview, just status change

## 16. Backup and Recovery Strategy

### 16.1 Database Backup

- **Frequency**:
  - Full backup: Daily at 2:00 AM UTC
  - Incremental backup: Every 6 hours
  - Transaction log backup: Every hour
- **Retention Policy**:
  - Daily backups: 30 days
  - Weekly backups: 12 weeks
  - Monthly backups: 12 months
- **Storage**:
  - Primary: Cloud storage (S3/GCS)
  - Secondary: Off-site backup location
- **Backup Format**: PostgreSQL dump (pg_dump)
- **Verification**: Automated restore test weekly

### 16.2 File Storage Backup

- **Resume Files**:
  - Synced to Google Drive daily
  - Retention: 7 years (compliance requirement)
  - Versioning: Keep all versions
- **Meeting Notes**:
  - Stored in Google Drive
  - Backup via Google Drive native backup
  - Retention: 3 years

### 16.3 Application Data Backup

- **Configuration**: Version controlled in Git
- **Environment Variables**: Stored in secrets manager
- **Database Migrations**: Version controlled in Git

### 16.4 Recovery Procedures

- **Point-in-Time Recovery**: Available for last 30 days
- **Full Restore**:
  1. Restore database from backup
  2. Verify data integrity
  3. Restore file storage if needed
  4. Update application configuration
  5. Run health checks
- **Disaster Recovery Time Objective (RTO)**: 4 hours
- **Disaster Recovery Point Objective (RPO)**: 1 hour (max data loss)

### 16.5 Backup Monitoring

- Automated backup verification
- Alert on backup failures
- Daily backup status report
- Monthly backup restore drill

## 17. Future Enhancements

### 17.1 Phase 2 Features

- **AI Integration**:
  - OpenAI gpt-4o-mini for resume parsing
  - Automated skills extraction
  - Salary prediction
  - Years of experience calculation
  - Resume rating and scoring
- **Reapplication Detection**:
  - Email/phone matching against rejections
  - Automatic alerts for HR team
  - Previous rejection history display
- Video interview integration
- AI-powered interview question generation
- Candidate self-service portal
- Mobile app for interviewers
- Advanced analytics dashboard
- Bulk email campaigns
- Integration with job boards

### 17.2 Phase 3 Features

- Machine learning for candidate matching
- Predictive analytics for hiring success
- Automated reference checking
- Skill assessment tests
- Collaborative hiring workflows
- Multi-language support

## 18. Audit Trail Implementation

### 18.1 Audit Logging

All significant actions are logged to the `audit_logs` table:

**Logged Actions:**

- User authentication (login, logout)
- Candidate creation, update, deletion
- Interview scheduling, update, cancellation
- Feedback submission
- Rejection actions
- User management (create, update, delete)
- Configuration changes
- File uploads and downloads

**Audit Log Fields:**

- `user_id`: User who performed the action (nullable for system actions)
- `action`: Type of action (create, update, delete, view, login, logout)
- `resource_type`: Type of resource affected (candidate, interview, feedback, user)
- `resource_id`: ID of the affected resource
- `changes`: JSON object with before/after values for updates
- `ip_address`: IP address of the request
- `user_agent`: User agent string from request
- `created_at`: Timestamp of the action

### 18.2 Audit Log Access

- Admin users can view all audit logs
- HR users can view audit logs for candidates and interviews
- Interviewers can view audit logs for their own actions
- Audit logs are immutable (no updates or deletes)
- Retention: 7 years (compliance requirement)

### 18.3 Audit Log Queries

- Search by user, action, resource type, date range
- Export audit logs for compliance reporting
- Real-time monitoring of sensitive actions (admin alerts)

## 19. Soft Delete Implementation

### 19.1 Soft Delete Strategy

All major entities support soft deletes using `deleted_at` timestamp field:

**Entities with Soft Delete:**

- `users`
- `candidates`
- `interview_rounds`
- `candidate_notes`

**Soft Delete Behavior:**

- Setting `deleted_at` marks record as deleted
- Deleted records are excluded from normal queries
- Deleted records can be restored by setting `deleted_at = NULL`
- Hard delete available for admin users (permanent removal)
- Soft deleted records retained for 7 years before hard delete

### 19.2 Query Behavior

- Default queries exclude soft-deleted records
- Include deleted records: Add `include_deleted=true` query parameter (admin only)
- Restore deleted record: PUT request with `deleted_at: null`
- Hard delete: DELETE request with `hard_delete=true` parameter (admin only)

## 20. Appendix

### 20.1 Technology Versions

- Python: 3.11+
- FastAPI: 0.104+
- Next.js: 14+
- React: 18+
- PostgreSQL: 15+
- Node.js: 18+

### 20.2 Key Dependencies

**Backend:**

- fastapi
- uvicorn
- sqlalchemy
- alembic
- pydantic
- python-jose[cryptography] (JWT)
- passlib[bcrypt]
- python-multipart
- boto3 (AWS, optional)
- google-cloud-storage
- google-api-python-client (Google Calendar/Drive)
- openai (Phase 2)
- python-docx
- PyPDF2
- alembic (database migrations)
- psycopg2-binary (PostgreSQL driver)
- python-dotenv (environment variables)

**Frontend:**

- next
- react
- react-dom
- axios
- swr or @tanstack/react-query
- tailwindcss
- react-dropzone
- react-big-calendar
- recharts (for analytics)
- date-fns

---

**Document Version**: 2.0

**Last Updated**: 12 November 2025

**Author**: Vikhyathraj Shetty K

**Changes in v2.0:**

- Clarified FastAPI as backend framework
- Added missing database schema components (skills, notifications, audit_logs, etc.)
- Removed encryption requirement for salary fields
- Removed WebSocket/real-time updates
- Added comprehensive API specifications (pagination, error handling, file limits)
- Added detailed authentication and authorization (JWT, RBAC)
- Added data validation rules
- Added backup and recovery strategy
- Updated interview round logic (0-4 rounds)
- Moved reapplication detection to Phase 2
- Added audit trail implementation details
- Added calendar integration specifics
- Moved AI features to Phase 2 (OpenAI gpt-4o-mini)
- Added soft delete implementation
- Added environment variable structure
- Added health/ready endpoints
- Added initial admin user setup
- Added Job Description Google Drive link
