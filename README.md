# Internship Management Portal

Welcome to the Internship Management Portal project repository.

## Project Overview

The Internship Management Portal is a web-based application developed to manage the complete internship workflow at IIT Madras.

The system provides:

- Authentication and Authorization
- Profile Management
- Internship Application Management
- Role Based Access Control (RBAC)
- Workflow Tracking
- Document Management

---

## Technology Stack

### Backend
- Python
- Flask
- SQLAlchemy
- JWT Authentication

### Frontend
- React.js
- Vite
- Tailwind CSS

### Database
- MySQL
- SQLite (Testing)

---

## Project Structure

```text
internship-management-portal/
│
├── backend/       # Server-side source code and APIs
├── frontend/      # Client-side application and UI components
├── database/      # Database schemas, migrations, and seed data
├── docs/          # Project documentation and specifications
└── README.md      # Repository documentation
```

---

## Features

### Authentication Module
- Login
- Logout
- JWT Authentication
- Current User API

### Profile Module
- Create Profile
- View Profile
- Update Profile

### Application Module
- Create Application
- Submit Application
- Update Application
- Status Tracking

### RBAC Module
- Applicant
- Supervisor
- Chairman
- SuperAdmin

---

## Running Backend

```bash
cd backend
python app.py
```

---

## Running Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Running Tests

```bash
python -m unittest test_auth
python -m unittest tests.test_profile
python -m unittest tests.test_application
```
