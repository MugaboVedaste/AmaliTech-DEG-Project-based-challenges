# Pulse-Check API (Watchdog Sentinel)

## Overview
Pulse-Check API is a backend monitoring system built with **Django** and **Django REST Framework** that implements a **Dead Man's Switch** mechanism. It continuously monitors remote devices by expecting periodic heartbeat requests. If a device fails to send a heartbeat before its configured timeout expires, the system automatically marks the device as **DOWN** and generates an alert.

The project was developed as a solution to the **CritMon Servers Inc. Backend Engineering Challenge**, demonstrating Computer Science fundamentals, stateful timer management, REST API development, authentication, and modular backend architecture.

---

# Business Problem
CritMon monitors remote infrastructure such as:

- Solar farms
- Weather stations
- IoT devices
- Other unmanned equipment

These devices periodically send heartbeat ("I'm alive") messages. If a heartbeat is not received within the expected timeout period, the system assumes the device has failed and immediately triggers an alert.

This eliminates the need for manual log inspection and allows engineers to respond more quickly to failures.

---

# Architecture
The application is organized into four Django apps following separation of concerns.

## Users
Responsible for authentication and user management.

Features:

- Email-based authentication
- JWT login
- User registration
- Device ownership

Each authenticated user only manages their own monitors and alerts.

---

## Monitors
Responsible for device monitoring.

Features:

- Register monitors
- Receive heartbeats
- Pause monitoring
- Resume monitoring
- Update timeout
- Track monitor status
- Manage timer lifecycle

Each monitor stores:

- Device ID
- Timeout
- Alert email
- Status
- Last heartbeat
- Owner

Possible monitor states:

- ACTIVE
- PAUSED
- DOWN

---

## Alerts
Responsible for recording monitoring failures.

Each alert stores:

- Related monitor
- Alert type
- Alert message
- Resolution status
- Creation timestamp

Alerts remain stored for historical tracking.

---

## Dashboard / Statistics
Provides a monitoring overview.

Includes:

- Total monitors
- Active monitors
- Paused monitors
- Down monitors
- Total alerts
- Unresolved alerts

---

# System Architecture Diagram

```
                        Remote Device
                               │
                     Heartbeat Request
                               │
                               ▼
                    Django REST Framework API
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
      Users App          Monitors App         Alerts App
(Authentication)      (Business Logic)     (Alert Storage)
                               │
                               ▼
                       Timer Service
                               │
                     Timer Expired?
                    ┌──────────┴──────────┐
                    │                     │
                   No                    Yes
                    │                     │
                    ▼                     ▼
             Reset Countdown       Create Alert
                    │                     │
                    └─────────────┬───────┘
                                  ▼
                           Statistics API
                                  │
                                  ▼
                              Dashboard
```

---

# Database Design

```
User
│
├── id
├── email
└── password
      │
      │ 1
      ▼
Monitor
├── device_id
├── timeout
├── alert_email
├── status
├── last_heartbeat
└── owner
      │
      │ 1
      ▼
Alert
├── alert_type
├── message
├── is_resolved
└── created_at
```

---

# Monitor Lifecycle

```
Register Monitor
        │
        ▼
 Start Countdown Timer
        │
        ▼
Heartbeat Received?
   │             │
 Yes             No
   │             │
   ▼             ▼
Reset Timer   Timer Expires
   │             │
   ▼             ▼
 ACTIVE      Status = DOWN
                  │
                  ▼
          Create Alert Record
                  │
                  ▼
        Log Alert to Console
                  │
                  ▼
      Available Through Alerts API
```

---

# Features

## Challenge Requirements

- JWT Authentication
- Register monitors
- Stateful countdown timers
- Heartbeat endpoint
- Automatic timer reset
- Automatic failure detection
- Automatic alert generation
- Console alert logging
- Pause monitoring
- Resume monitoring

---

## Additional Features (Developer's Choice)
To make the system more robust and user-friendly, the following features were added:

- Email-based user authentication
- Multi-user device ownership
- Persistent alert history
- Dynamic timeout updates
- Statistics API
- Dashboard for monitoring overview
- Alert resolution support

These additions improve usability, security, and maintainability while preserving the original challenge requirements.

---

# REST API Endpoints

> All endpoints require JWT Bearer Authentication except `/users/register/` and `/users/login/`.

## Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/register/` | Register a new user |
| POST | `/users/login/` | Authenticate user and obtain JWT tokens |
---

## Monitors
| Method | Endpoint | Description |
|---|---|---|
| POST | `/monitors/` | Register a monitor |
| GET | `/monitors/list/` | List all user monitors |
| POST | `/monitors/{device_id}/heartbeat/` | Reset countdown timer |
| POST | `/monitors/{device_id}/pause/` | Pause monitoring |
| POST | `/monitors/{device_id}/resume/` | Resume monitoring |
| PATCH | `/monitors/{device_id}/timeout/` | Update timeout duration |
---

## Alerts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/alerts/` | List all alerts |
| GET | `/alerts/{device_id}/` | List alerts for a specific device |
| PATCH | `/alerts/resolve/{alert_id}/` | Mark an alert as resolved |
---

## Statistics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats/` | Retrieve monitoring statistics |
---

# API Usage with Postman

This section provides a guide on how to test the Pulse-Check API endpoints using Postman.

## 1. Base URL
Assume your API is running locally on port 8000.
**Base URL:** `http://localhost:8000/api/`

## 2. Authentication Flow

All endpoints (except `/users/register/` and `/users/login/`) require JWT Bearer Authentication.

### Step 1: Register a User (if you haven't already)
- **Endpoint:** `POST http://localhost:8000/api/users/register/`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
  ```json
  {
      "email": "test@example.com",
      "password": "your_strong_password"
  }
  ```
- **Expected Response:** `201 Created` with user details.

### Step 2: Obtain JWT Tokens (Login)
- **Endpoint:** `POST http://localhost:8000/api/users/login/`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
  ```json
  {
      "email": "test@example.com",
      "password": "your_strong_password"
  }
  ```
- **Expected Response:** `200 OK` with `access` and `refresh` tokens.
  ```json
  {
      "refresh": "eyJ...",
      "access": "eyJ..."
  }
  ```
  **Save the `access` token.** You will use this for subsequent authenticated requests.

## 3. Setting up Authentication in Postman

1.  In your Postman request, go to the `Authorization` tab.
2.  Select `Type: Bearer Token`.
3.  Paste the `access` token obtained from the login step into the `Token` field.

## 4. Example Requests

### Example 1: Register a Monitor
- **Endpoint:** `POST http://localhost:8000/api/monitors/`
- **Headers:**
    - `Content-Type: application/json`
    - `Authorization: Bearer <your_access_token>`
- **Body (raw JSON):**
  ```json
  {
      "device_id": "device-123",
      "timeout": 60,
      "alert_email": "admin@critmon.com"
  }
  ```
- **Expected Response:** `201 Created` with monitor details.

### Example 2: Send a Heartbeat
- **Endpoint:** `POST http://localhost:8000/api/monitors/device-123/heartbeat/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None (or empty JSON `{}`)
- **Expected Response:** `200 OK` with a confirmation message.

### Example 3: List all Monitors
- **Endpoint:** `GET http://localhost:8000/api/monitors/list/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with a list of monitors.

### Example 4: List Alerts for a Specific Device
- **Endpoint:** `GET http://localhost:8000/api/alerts/device-123/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with a list of alerts for `device-123`.

This guide should help you effectively test the API using Postman.

---

# Setup Instructions
Clone the repository:

```
git clone https://github.com//Pulse-Check-API.git
cd Pulse-Check-API
```
Create and activate a virtual environment:

**Windows**

```
python -m venv venv
venv\Scripts\activate
```
**Linux/macOS**

```
python3 -m venv venv
source venv/bin/activate
```
Install dependencies:

```
pip install -r requirements.txt
```
Apply migrations:

```
python manage.py migrate
```
Create a superuser (optional):

```
python manage.py createsuperuser
```
Run the development server:

```
python manage.py runserver
```

---

# Design Principles
The project follows modern backend engineering practices:

- Modular Django applications
- Separation of concerns
- RESTful API design
- JWT authentication
- Service-layer business logic
- Meaningful Git commit history
- Clean project organization
- Reusable components

---

# Future Improvements
Possible production enhancements include:

- Redis-backed timers
- Celery background workers
- PostgreSQL database
- Docker deployment
- Email notifications
- Webhook integrations
- Device groups
- Role-based permissions
- Monitoring analytics
- Prometheus metrics
- Health check endpoint

---

# Conclusion
Pulse-Check API fulfills all core requirements of the CritMon Servers Inc. challenge by implementing a stateful Dead Man's Switch monitoring system. In addition, it extends the solution with authentication, multi-user support, persistent alert management, dashboard statistics, dynamic timeout updates, and a clean modular architecture, resulting in a scalable and maintainable backend application.
