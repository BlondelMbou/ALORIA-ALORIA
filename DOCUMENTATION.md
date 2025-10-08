# ALORIA AGENCY - Immigration Case Management System

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Application Structure](#application-structure)
7. [API Documentation](#api-documentation)
8. [Immigration Workflows](#immigration-workflows)
9. [User Guide](#user-guide)
10. [Development Guide](#development-guide)

---

## 🎯 Overview

ALORIA AGENCY is a comprehensive immigration case management platform designed to streamline and automate the immigration process for Canada and France. The system provides transparency, efficiency, and real-time tracking for clients, employees, and managers.

### Key Benefits
- **Real-time tracking** of immigration case progress
- **Automated notifications** for status changes
- **Document checklist management** (no file storage)
- **Multi-role dashboards** for different user types
- **Polling-based messaging** system
- **Visitor registry** for office management
- **Research-backed workflows** from official immigration sources

---

## ✨ Features

### For Clients
- ✅ View personal case progress with visual timeline
- ✅ Track current step and required documents
- ✅ Message directly with assigned counselor
- ✅ Real-time status updates
- ✅ Transparent progress indicators

### For Employees (Immigration Counselors)
- ✅ Manage personal client portfolio
- ✅ Create new clients
- ✅ Update case progress and status
- ✅ View required documents for each step
- ✅ Direct messaging with clients
- ✅ Dashboard with performance metrics

### For Managers
- ✅ Complete overview of all cases and clients
- ✅ KPI dashboard with real-time statistics
- ✅ Employee management and performance tracking
- ✅ Client reassignment capabilities
- ✅ Visitor registry management
- ✅ Cases breakdown by country and status
- ✅ Access to all communications (supervisor mode)

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** MongoDB (Motor async driver)
- **Authentication:** JWT tokens with bcrypt password hashing
- **Security:** PassLib for password encryption

### Frontend
- **Framework:** React 19
- **Routing:** React Router DOM v7
- **UI Library:** Shadcn UI + Tailwind CSS
- **Icons:** Lucide React
- **Notifications:** Sonner
- **HTTP Client:** Axios

### Infrastructure
- **Backend Server:** Uvicorn (ASGI)
- **Frontend Server:** React development server
- **Process Manager:** Supervisor
- **Deployment:** Kubernetes-ready

---

## 🚀 Installation & Setup

### Prerequisites
```bash
- Python 3.11+
- Node.js 18+
- MongoDB 4.5+
- Yarn package manager
```

### Backend Setup
```bash
# Navigate to backend directory
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit /app/backend/.env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="aloria_agency"
CORS_ORIGINS="*"
SECRET_KEY="your-secure-secret-key"

# Start backend (using supervisor)
sudo supervisorctl restart backend
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd /app/frontend

# Install dependencies
yarn install

# Configure environment variables
# Edit /app/frontend/.env
REACT_APP_BACKEND_URL=https://your-domain.com
WDS_SOCKET_PORT=443

# Start frontend (using supervisor)
sudo supervisorctl restart frontend
```

### Database Setup
MongoDB will automatically create collections on first use. No manual setup required.

### Initial Admin Account
Register the first manager account through the registration page:
1. Navigate to `/login`
2. Click "Register" tab
3. Select "Manager" role
4. Complete registration

---

## 👥 User Roles & Permissions

### CLIENT
**Access Level:** Limited
- ✅ View personal case only
- ✅ Send messages to assigned counselor
- ✅ View document checklists
- ✅ Track progress
- ❌ Cannot modify case status
- ❌ Cannot see other clients

**Default Credentials:** Created automatically when a client is added through landing page or by employee

### EMPLOYEE (Immigration Counselor)
**Access Level:** Medium
- ✅ View and manage assigned clients
- ✅ Create new clients (auto-assigned to them)
- ✅ Update case progress and status
- ✅ Message with their clients
- ✅ View performance statistics
- ❌ Cannot see other employees' clients
- ❌ Cannot manage other employees

**Registration:** Self-register as Employee through login page

### MANAGER
**Access Level:** Full
- ✅ View all clients, cases, and employees
- ✅ Access to all dashboards and statistics
- ✅ Reassign clients between employees
- ✅ View all messages (supervisor mode)
- ✅ Manage visitor registry
- ✅ Generate reports and KPIs
- ✅ Toggle employee status (active/inactive)

**Registration:** Self-register as Manager through login page

---

## 📁 Application Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Global styles
│   │   ├── context/
│   │   │   └── AuthContext.js # Authentication context
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── LoginPage.js
│   │   │   ├── ManagerDashboard.js
│   │   │   ├── EmployeeDashboard.js
│   │   │   └── ClientDashboard.js
│   │   ├── components/ui/    # Shadcn UI components
│   │   └── utils/
│   │       └── api.js        # API helper functions
│   ├── package.json
│   └── .env
│
└── DOCUMENTATION.md          # This file
```

---

## 🔌 API Documentation

### Base URL
```
https://your-domain.com/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "phone": "+1 234 567 8900",
  "role": "EMPLOYEE" // or "MANAGER"
}

Response: {
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response: {
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}

Response: {
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "EMPLOYEE",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00"
}
```

### Client Management

#### Create Client
```http
POST /api/clients
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "client@example.com",
  "full_name": "Jane Smith",
  "phone": "+1 234 567 8900",
  "country": "Canada",
  "visa_type": "Work Permit",
  "message": "Optional message"
}
```

#### Get All Clients
```http
GET /api/clients
Authorization: Bearer {token}

// Returns clients based on role:
// - MANAGER: All clients
// - EMPLOYEE: Only assigned clients
// - CLIENT: Only own record
```

#### Get Client by ID
```http
GET /api/clients/{client_id}
Authorization: Bearer {token}
```

#### Reassign Client (Manager only)
```http
PATCH /api/clients/{client_id}/reassign?new_employee_id={employee_id}
Authorization: Bearer {token}
```

### Case Management

#### Get All Cases
```http
GET /api/cases
Authorization: Bearer {token}
```

#### Get Case by ID
```http
GET /api/cases/{case_id}
Authorization: Bearer {token}
```

#### Update Case
```http
PATCH /api/cases/{case_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "current_step_index": 3,
  "status": "In Progress",
  "notes": "Updated notes"
}
```

### Messaging

#### Send Message
```http
POST /api/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "receiver_id": "user_uuid",
  "client_id": "client_uuid",
  "message": "Message text"
}
```

#### Get Messages for Client
```http
GET /api/messages/client/{client_id}
Authorization: Bearer {token}
```

#### Get Unread Message Count
```http
GET /api/messages/unread
Authorization: Bearer {token}
```

### Dashboard

#### Get Dashboard Statistics (Manager only)
```http
GET /api/dashboard/stats
Authorization: Bearer {token}

Response: {
  "total_cases": 10,
  "active_cases": 5,
  "completed_cases": 3,
  "pending_cases": 2,
  "total_clients": 10,
  "total_employees": 3,
  "cases_by_country": {
    "Canada": 6,
    "France": 4
  },
  "cases_by_status": {
    "New": 2,
    "In Progress": 5,
    "Approved": 3
  }
}
```

### Visitor Management

#### Register Visitor
```http
POST /api/visitors
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Visitor Name",
  "company": "Company Name",
  "purpose": "Meeting purpose"
}
```

#### Get All Visitors
```http
GET /api/visitors
Authorization: Bearer {token}
```

#### Check Out Visitor
```http
PATCH /api/visitors/{visitor_id}/checkout
Authorization: Bearer {token}
```

### Employee Management

#### Get All Employees (Manager only)
```http
GET /api/employees
Authorization: Bearer {token}
```

#### Toggle Employee Status (Manager only)
```http
PATCH /api/employees/{employee_id}/toggle-status
Authorization: Bearer {token}
```

### Workflows

#### Get All Workflows
```http
GET /api/workflows
Authorization: Bearer {token}

// Returns workflows for Canada and France
```

---

## 🗺️ Immigration Workflows

### Canada

#### Work Permit
1. **Initial Consultation & Eligibility Check**
   - Documents: Valid passport, Educational credentials, Resume/CV, Job offer letter
   - Duration: 3-5 days

2. **Document Collection**
   - Documents: Job offer (LMIA), Educational credentials (ECA), Language test results, Proof of work experience, Police clearance
   - Duration: 2-4 weeks

3. **IRCC Account Creation**
   - Documents: Valid email, Security questions
   - Duration: 1 day

4. **Application Form Completion**
   - Documents: IMM 1295, IMM 5707, IMM 5645
   - Duration: 3-7 days

5. **Fee Payment**
   - Documents: Work permit fee (CAD $155), Biometrics fee (CAD $85), Payment receipt
   - Duration: 1 day

6. **Application Submission**
   - Documents: All forms, Supporting documents, Payment confirmation
   - Duration: 1 day

7. **Biometrics Appointment**
   - Documents: Biometrics instruction letter, Valid passport, Appointment confirmation
   - Duration: 1-3 weeks

8. **Application Processing**
   - Documents: Additional documents if requested, Medical exam if requested
   - Duration: 8-12 weeks

9. **Decision Received**
   - Documents: Port of Entry Letter, Visa (if required)
   - Duration: 1-2 days

10. **Work Permit Issued**
    - Documents: Work permit document, Confirmation of work authorization
    - Duration: Upon arrival

#### Study Permit
10 steps - from Initial Consultation to Study Permit Received

#### Permanent Residence (Express Entry)
10 steps - from Eligibility Assessment to PR Card Application

### France

#### Work Permit (Talent Permit)
1. **Initial Consultation**
2. **Employment Contract**
3. **Work Authorization**
4. **Document Preparation**
5. **France-Visas Application**
6. **Consulate Appointment**
7. **VLS-TS Visa Issuance**
8. **Entry to France**
9. **OFII Validation**
10. **Carte de Séjour**

#### Student Visa
10 steps - from Initial Consultation to Student Residence Permit

#### Family Reunification
10 steps - from Eligibility Check to Family Residence Permit Issued

---

## 📖 User Guide

### For New Clients

1. **Submit Application**
   - Visit the landing page
   - Fill out the application form
   - Select your destination country and visa type
   - Submit the form

2. **Receive Credentials**
   - Account is created automatically
   - Check email for login details (temp password: temp123)

3. **Login to Portal**
   - Visit `/login`
   - Use your email and temporary password
   - Change password on first login (recommended)

4. **Track Your Progress**
   - View your case timeline
   - Check current step and required documents
   - Message your counselor
   - Monitor status updates

### For Employees

1. **Register Account**
   - Visit `/login`
   - Click "Register"
   - Select "Employee" role
   - Complete registration

2. **Create Clients**
   - Navigate to "Create Client" tab
   - Fill in client details
   - Client is auto-assigned to you

3. **Manage Cases**
   - View all your assigned clients
   - Update case progress
   - Change status as needed
   - View required documents for each step

4. **Communicate**
   - Use messaging feature
   - Respond to client inquiries
   - Messages refresh every 10 seconds (polling)

### For Managers

1. **Register Account**
   - Visit `/login`
   - Click "Register"
   - Select "Manager" role
   - Complete registration

2. **Monitor Operations**
   - View KPI dashboard
   - Track cases by country and status
   - Monitor employee performance

3. **Manage Resources**
   - Reassign clients between employees
   - View all communications
   - Manage visitor registry

4. **Generate Insights**
   - Review cases breakdown
   - Track completion rates
   - Analyze workload distribution

---

## 💻 Development Guide

### Adding New Countries

1. **Research Official Sources**
   - Visit official immigration websites
   - Document visa types and processes

2. **Define Workflow**
   - Edit `/app/backend/server.py`
   - Add new workflow in `WORKFLOWS` dictionary
   - Follow existing structure

3. **Update Frontend**
   - Edit `/app/frontend/src/pages/LandingPage.js`
   - Add country to `countries` array and `visaTypes` object

### Customizing Workflows

```python
# In /app/backend/server.py
WORKFLOWS = {
    "Country Name": {
        "Visa Type": [
            {
                "title": "Step Title",
                "description": "Step description",
                "documents": ["Doc 1", "Doc 2"],
                "duration": "1-2 weeks"
            },
            # ... more steps
        ]
    }
}
```

### Testing APIs

```bash
# Test authentication
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@aloria.com","password":"manager123"}'

# Test protected endpoint
curl -X GET https://your-domain.com/api/clients \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database Schema

**Users Collection:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "password": "hashed_password",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "EMPLOYEE",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00"
}
```

**Clients Collection:**
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "assigned_employee_id": "employee_uuid",
  "country": "Canada",
  "visa_type": "Work Permit",
  "current_status": "In Progress",
  "current_step": 3,
  "progress_percentage": 30.0,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

**Cases Collection:**
```json
{
  "id": "uuid",
  "client_id": "client_uuid",
  "country": "Canada",
  "visa_type": "Work Permit",
  "workflow_steps": [...],
  "current_step_index": 3,
  "status": "In Progress",
  "notes": "Optional notes",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### Environment Variables

**Backend (.env):**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=aloria_agency
CORS_ORIGINS=*
SECRET_KEY=your-secret-key-here
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://your-domain.com
WDS_SOCKET_PORT=443
```

### Deployment Checklist

- [ ] Update SECRET_KEY in backend/.env
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up MongoDB with authentication
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up backup strategy for database
- [ ] Configure monitoring and logging
- [ ] Test all user flows
- [ ] Set up email notifications (future enhancement)

---

## 🔒 Security Features

1. **Authentication**
   - JWT token-based authentication
   - Bcrypt password hashing
   - 7-day token expiration

2. **Authorization**
   - Role-based access control (RBAC)
   - Endpoint-level permission checks
   - User-specific data filtering

3. **Data Protection**
   - CORS configuration
   - Password encryption
   - Secure token storage

4. **RGPD Compliance**
   - User data isolation
   - Audit trail with timestamps
   - Secure data transmission

---

## 🚀 Future Enhancements

- [ ] Email notifications for status changes
- [ ] Real-time messaging (WebSocket)
- [ ] File upload functionality
- [ ] Digital signature integration
- [ ] Multi-language support
- [ ] Mobile applications
- [ ] Payment integration
- [ ] Advanced reporting
- [ ] Germany and Belgium workflows
- [ ] AI-powered document analysis

---

## 📞 Support

For technical support or questions:
- Email: support@aloriaagency.com
- Documentation: This file
- Issues: Contact your system administrator

---

## 📄 License

© 2025 ALORIA AGENCY. All rights reserved.

---

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Developed with:** FastAPI + React + MongoDB
