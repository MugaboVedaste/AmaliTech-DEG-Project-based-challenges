# Pulse-Check API ("Watchdog" Sentinel)

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
- JWT login (for the API)
- Session login (for the web Dashboard)
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
- Read/unread status
- Creation timestamp

Alerts remain stored for historical tracking, exposed via the JSON API (`/alerts/`) and through the Dashboard app (see [The Developer's Choice](#the-developers-choice-operations-dashboard)).

---

## Dashboard
The Developer's Choice feature — a server-rendered operations console for the monitoring data owned by the other three apps. See below for details.

---

# Architecture Diagrams

## System Architecture Diagram

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
                          Dashboard App
                    (overview, monitors, alerts)
```

## Sequence Diagram: Heartbeat & Failure Flow

```
Device                 Monitors API              Timer Service            Alerts
  │                         │                          │                    │
  │  POST /monitors/        │                          │                    │
  ├────────────────────────►│                          │                    │
  │                         │  start_timer(monitor)     │                    │
  │                         ├─────────────────────────►│                    │
  │        201 Created      │                          │                    │
  │◄────────────────────────┤                          │                    │
  │                         │                          │                    │
  │  POST .../heartbeat/    │                          │                    │
  ├────────────────────────►│                          │                    │
  │                         │  reset timer (cancel+restart)                 │
  │                         ├─────────────────────────►│                    │
  │        200 OK           │                          │                    │
  │◄────────────────────────┤                          │                    │
  │                         │                          │                    │
  │      (device goes silent — no heartbeat sent)       │                    │
  │                         │                          │  timeout elapses    │
  │                         │                          ├───────────────────►│
  │                         │                          │  status = DOWN     │
  │                         │                          │  create Alert      │
  │                         │                          │  console.log alert │
  │                         │                          │                    │
```

## Database Design

```
User (1)
│
├── id
├── email
└── password
      │
      │ 1───* (owner)
      ▼
Monitor (*)
├── device_id
├── timeout
├── alert_email
├── status
└── owner (FK → User)
      │
      │ 1───* (monitor)
      ▼
Alert (*)
├── alert_type
├── message
├── is_resolved
└── created_at
```

## Monitor Lifecycle (State Flowchart)

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
      Available Through Dashboard
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

## The Developer's Choice: Operations Dashboard

**Feature added:** a full server-rendered web Dashboard (`dashboard` app) — login page, fleet overview with live counts (total/active/paused/down monitors, unresolved alerts), a monitor list and detail view, forms to register/pause/resume a monitor and edit its timeout, and an alert history page.

**Why:** the challenge's core deliverable is a JSON API, but the actual end user of a monitoring tool is a support engineer, not a Postman window. Without a UI, checking "is anything down right now?" means hand-crafting authenticated requests. The Dashboard turns Pulse-Check into something an on-call engineer could realistically use during an incident — sign in, see fleet health at a glance, drill into a device, resolve or acknowledge alerts — while reusing the exact same `monitors`/`alerts` services and the same timer lifecycle as the JSON API, so there is only one source of truth for monitor state.

Supporting additions that make this useful in practice:

- Persistent alert history (alerts are never deleted, only marked resolved/read)
- Unread-alert badge count shown across the Dashboard
- Dynamic timeout updates from the monitor detail page

---

# REST API Endpoints

> Base URL: `http://localhost:8000/` (no `/api/` prefix — see [Setup Instructions](#setup-instructions)).
> All endpoints below require JWT Bearer Authentication except `/users/register/` and `/users/login/`.

## Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/register/` | Register a new user |
| POST | `/users/login/` | Authenticate user and obtain JWT tokens |

## Monitors
| Method | Endpoint | Description |
|---|---|---|
| POST | `/monitors/` | Register a monitor |
| GET | `/monitors/list/` | List all user monitors |
| POST | `/monitors/{device_id}/heartbeat/` | Reset countdown timer |
| POST | `/monitors/{device_id}/pause/` | Pause monitoring |
| POST | `/monitors/{device_id}/resume/` | Resume monitoring |
| PATCH | `/monitors/{device_id}/timeout/` | Update timeout duration |

## Alerts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/alerts/` | List all alerts for the authenticated user's monitors |
| GET | `/alerts/{device_id}/` | List alerts for a specific device |
| PATCH | `/alerts/resolve/{alert_id}/` | Mark an alert as resolved |

## Statistics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats/` | Fleet statistics for the authenticated user (monitor counts by status, total/unresolved alerts) |

## Web Dashboard (session-authenticated, HTML)
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/` | Login page |
| GET | `/logout/` | Log out |
| GET | `/dashboard/` | Fleet overview (counts + recent alerts) |
| GET | `/dashboard/monitors/` | List monitors |
| POST | `/dashboard/monitors/register/` | Register a monitor (form) |
| GET | `/dashboard/monitors/{device_id}/` | Monitor detail + its alerts |
| POST | `/dashboard/monitors/{device_id}/pause/` | Pause monitoring |
| POST | `/dashboard/monitors/{device_id}/resume/` | Resume monitoring |
| POST | `/dashboard/monitors/{device_id}/timeout/` | Update timeout |
| GET | `/dashboard/alerts/` | Alert history |

---

# API Usage with Postman

This section covers testing the JSON API endpoints using Postman.

## 1. Base URL
Assume your API is running locally on port 8000.
**Base URL:** `http://localhost:8000/`

## 2. Authentication Flow

All endpoints (except `/users/register/` and `/users/login/`) require JWT Bearer Authentication.

### Step 1: Register a User (if you haven't already)
- **Endpoint:** `POST http://localhost:8000/users/register/`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
  ```json
  {
      "email": "test@example.com",
      "password": "your_strong_password",
      "company_name": "CritMon Servers Inc."
  }
  ```
- **Expected Response:** `201 Created` with a confirmation message.

### Step 2: Obtain JWT Tokens (Login)
- **Endpoint:** `POST http://localhost:8000/users/login/`
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
- **Endpoint:** `POST http://localhost:8000/monitors/`
- **Headers:**
    - `Content-Type: application/json`
    - `Authorization: Bearer <your_access_token>`
- **Body (raw JSON):**
  ```json
  {
      "id": "device-123",
      "timeout": 60,
      "alert_email": "admin@critmon.com"
  }
  ```
  > Note the field is `id`, not `device_id` — it maps to the monitor's `device_id` internally.
- **Expected Response:** `201 Created` with monitor details.

### Example 2: Send a Heartbeat
- **Endpoint:** `POST http://localhost:8000/monitors/device-123/heartbeat/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None (or empty JSON `{}`)
- **Expected Response:** `200 OK` with a confirmation message.

### Example 3: List all Monitors
- **Endpoint:** `GET http://localhost:8000/monitors/list/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with a list of monitors.

### Example 4: Pause / Resume a Monitor
- **Endpoint:** `POST http://localhost:8000/monitors/device-123/pause/` (or `/resume/`)
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with the monitor's new status.

### Example 5: List Alerts for a Specific Device
- **Endpoint:** `GET http://localhost:8000/alerts/device-123/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with a list of alerts for `device-123`.

### Example 6: Resolve an Alert
- **Endpoint:** `PATCH http://localhost:8000/alerts/resolve/1/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with `{"message": "Alert resolved", "id": 1, "is_resolved": true}`.

### Example 7: Fleet Statistics
- **Endpoint:** `GET http://localhost:8000/stats/`
- **Headers:**
    - `Authorization: Bearer <your_access_token>`
- **Body:** None
- **Expected Response:** `200 OK` with monitor/alert counts for the authenticated user.

This guide should help you effectively test the API using Postman.

---

# Setup Instructions

Fork and clone the repository:

```
git clone https://github.com/<your-username>/AmaliTech-DEG-Project-based-challenges.git
cd AmaliTech-DEG-Project-based-challenges/backend/Pulse-Check
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
Create a superuser (optional, for `/admin/`):

```
python manage.py createsuperuser
```
Run the development server:

```
python manage.py runserver
```

The web Dashboard is at `http://localhost:8000/`; the JSON API is described above.

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
- Real email notifications (currently alerts are logged to console)
- Webhook integrations
- Device groups
- Role-based permissions
- Monitoring analytics
- Prometheus metrics
- Health check endpoint

---

# Conclusion
Pulse-Check API fulfills all core requirements of the CritMon Servers Inc. challenge by implementing a stateful Dead Man's Switch monitoring system: monitor registration, heartbeats, automatic failure detection and alerting, and pause/resume support. Its Developer's Choice addition, a full operations Dashboard, extends the solution beyond the JSON API into something a support engineer could actually use during an incident, while keeping monitor and alert state as the single source of truth shared by both the API and the UI.
