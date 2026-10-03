# Amra — Tourism & Pilgrimage Management Platform

A full-stack tourism and pilgrimage management platform designed to connect **pilgrims, tourism companies, guides, finance teams, support staff, and platform administrators** through role-based workflows and centralized management.

The backend is built with **Django REST Framework** and provides JWT authentication, role-based access control, package and booking management, company onboarding, support tickets, notifications, and real-time communication using **Django Channels, WebSockets, and Redis**.

## 🌐 Live Applications

* **Pilgrim Portal:** https://omrah-pilgrim.vercel.app/
* **Company Portal:** https://omrah-company.vercel.app/
* **Admin Portal:** https://omrah-admin.vercel.app/

## ✨ Key Features

### 🔐 Authentication & Role-Based Access

* Custom user model with email-based authentication
* JWT authentication using SimpleJWT
* Role-based access control
* Separate workflows for:

  * Pilgrims
  * Tourism Company Owners
  * Guides
  * Finance Staff
  * Support Staff
  * Platform Administrators
* Protected REST API endpoints
* User status management

The backend configures Django REST Framework with JWT authentication as the default authentication mechanism and uses custom permissions and filtering throughout the API.

### 🏢 Tourism Company Management

Companies can be registered and managed through dedicated workflows including:

* Company profile management
* License information
* Contact and address details
* Company document uploads
* QR code and identification document storage
* Company status management
* Administrative review and approval workflows

Supported company states include `PENDING`, `WAITING_PAYMENT`, `ACTIVE`, and `REJECTED`.

### 🕌 Pilgrimage Package Management

Tourism companies can create and manage pilgrimage packages with:

* Package title and description
* Family, individual, and VIP package types
* Pricing
* Travel dates
* Duration
* Capacity management
* Assigned guides
* Hotel information
* Transportation
* Flights
* Meals
* Package status management

The system also calculates available seats dynamically based on confirmed bookings.

### 📋 Booking & Payment Tracking

Pilgrims can book available packages while the backend tracks:

* Number of seats
* Total price
* Paid amount
* Remaining amount
* Payment status
* Booking status
* Transaction number
* Rejection reasons

Booking states include `PENDING`, `CONFIRMED`, and `CANCELLED`, while payment tracking supports `UNPAID`, `PARTIAL`, and `PAID`.

### 💬 Real-Time Chat

The platform includes a real-time communication system powered by:

* Django Channels
* WebSockets
* Redis
* JWT-authenticated WebSocket connections
* Private and group chat rooms
* Room membership validation
* Message persistence
* Read/unread message tracking
* Online presence tracking
* Real-time room updates

The ASGI application combines chat and notification WebSocket routes and protects connections through JWT authentication middleware.

### 🔔 Notifications

The notification system supports user-specific notifications with:

* Real-time delivery
* Read/unread state
* Persistent notification records
* Chat and room update notifications

Notifications are stored per user and integrated with the WebSocket layer for real-time updates.

### 🎫 Support Ticketing

A dedicated ticketing system allows users to create and track support requests.

Supported ticket features include:

* Platform or company-related tickets
* Ticket subject and description
* Status tracking
* Company association
* Expiration handling

Ticket statuses include `OPEN`, `IN_PROGRESS`, and `CLOSED`.

---

## 🏗️ Architecture
<img width="2794" height="1204" alt="mermaid-diagram (1)" src="https://github.com/user-attachments/assets/badf0d19-5635-4a8e-96e8-c0379d38df6a" />


The project uses Django's ASGI stack for HTTP and WebSocket traffic. Django Channels is configured with Redis as the channel layer.

---

## 📁 Project Structure

```text
Amra/
├── Amra/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── users/
│   └── Authentication, users and pilgrim profiles
│
├── companies/
│   └── Company management and staff profiles
│
├── packages/
│   └── Pilgrimage package management
│
├── bookings/
│   └── Booking and payment tracking
│
├── notifications/
│   └── Notification system
│
├── chat/
│   └── Real-time chat and WebSocket consumers
│
├── tickets/
│   └── Support ticket management
│
├── platform_admin/
│   └── Platform-level administrative operations
│
├── media/
│   └── Uploaded media files
│
├── manage.py
├── requirements.txt
└── Amra.postman_collection.json
```

The repository currently separates the main business domains into Django applications, including users, companies, packages, bookings, chat, notifications, platform administration, and tickets.

---

## 🧩 Main Backend Modules

| Module           | Responsibility                                  |
| ---------------- | ----------------------------------------------- |
| `users`          | Authentication, user accounts, pilgrim profiles |
| `companies`      | Company registration, documents, company status |
| `packages`       | Pilgrimage package creation and management      |
| `bookings`       | Package reservations and payment tracking       |
| `chat`           | Real-time private/group communication           |
| `notifications`  | User notifications and room updates             |
| `tickets`        | Support ticket workflows                        |
| `platform_admin` | Platform-level administrative operations        |

---

## 🔌 API Structure

The backend exposes RESTful endpoints through Django REST Framework.

Main route groups include:

```text
/health/
/admin/

/users/
/company/

/api/
/api/chat/
/api/ticket/

/user/
```

The API includes authentication, company management, packages, bookings, notifications, chat, support tickets, and administrative functionality.

---

## 🛠️ Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* SimpleJWT
* Django Channels
* Daphne
* Redis

### Database

* SQLite for the current development configuration
* PostgreSQL support through `psycopg2-binary`

### API & Communication

* RESTful APIs
* JWT Authentication
* WebSockets
* Redis Channel Layer
* CORS support
* Filtering, search, ordering, and pagination

### Development & Testing

* Postman API collection
* Git / GitHub

The current dependency set includes Django 5.2, Django REST Framework 3.16, Channels 4.3, Channels Redis 4.3, Daphne 4.2, Redis client support, JWT authentication, and PostgreSQL client support.

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hussein98912/Amra.git
cd Amra
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Redis

The real-time layer uses Redis through the `REDIS_URL` environment variable.

Example:

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

### 7. Run the development server

For standard Django development:

```bash
python manage.py runserver
```

For the ASGI/WebSocket stack:

```bash
daphne -b 0.0.0.0 -p 8000 Amra.asgi:application
```

The project exposes an ASGI application that serves both HTTP requests and WebSocket connections.

---

## 🔑 Environment Variables

At minimum, configure:

```env
SECRET_KEY=your-secret-key
REDIS_URL=redis://127.0.0.1:6379/0
```

For production deployments, secrets and infrastructure configuration should be supplied through environment variables rather than committed to the repository.

---

## 📮 API Testing

A Postman collection is included in the repository:

```text
Amra.postman_collection.json
```

It can be imported into Postman to test the available API workflows.

---

## 🔄 Core Business Flow

### Company Onboarding

```text
Company Registration
        ↓
Document Submission
        ↓
Administrative Review
        ↓
Approval / Rejection
        ↓
Company Activation
```

### Package & Booking Flow

```text
Company
   ↓
Create Package
   ↓
Package Review / Activation
   ↓
Pilgrim Browses Packages
   ↓
Booking Request
   ↓
Payment Tracking
   ↓
Booking Confirmation
```

### Support Flow

```text
User
  ↓
Create Ticket
  ↓
Support / Company
  ↓
In Progress
  ↓
Resolved / Closed
```

---

## 🔐 Security & Access Control

The backend is designed around authenticated access and role-aware workflows.

Key security mechanisms include:

* JWT authentication
* Protected API endpoints
* Custom user model
* Role-based permissions
* WebSocket authentication
* WebSocket room membership validation
* Django password hashing
* Controlled access to company and platform resources

The REST framework configuration defaults to authenticated access, while the chat WebSocket layer validates the authenticated user and room membership before allowing connections.

---

## 🚀 Deployment Notes

The backend is structured to support deployment using an ASGI server such as **Daphne** for HTTP and WebSocket traffic.

For a production deployment, the following should be configured appropriately:

* Production `SECRET_KEY`
* `DEBUG=False`
* Restricted `ALLOWED_HOSTS`
* Production database such as PostgreSQL
* Managed Redis instance
* Proper CORS configuration
* Secure media/static file handling
* HTTPS / WSS
* Environment-based configuration

The current repository configuration uses SQLite and enables development-oriented settings, so these values should be reviewed before treating the current configuration as production-ready.

---

## 📊 Current Backend Highlights

* Modular Django architecture
* Custom authentication system
* JWT-based API security
* Role-based access control
* RESTful API design
* Package and booking workflows
* Payment status tracking
* Document and media uploads
* Real-time WebSocket communication
* Redis-backed channel layer
* Real-time notifications
* Online presence tracking
* Support ticket management
* Postman API collection

---

## 📚 Project Purpose

Amra was developed as a complete backend-driven platform rather than a simple CRUD application.

The project focuses on:

* Designing modular backend architecture
* Building secure REST APIs
* Managing multi-role workflows
* Implementing real-time communication
* Handling booking and business logic
* Integrating Redis and WebSockets
* Structuring a system for multiple frontend clients

---

## 📌 Repository

**GitHub:**
https://github.com/hussein98912/Amra

**Live Applications:**

* https://omrah-pilgrim.vercel.app/
* https://omrah-company.vercel.app/
* https://omrah-admin.vercel.app/

---

## 👨‍💻 Author

**Hussein Salman**

Backend Developer | AI & Software Development

GitHub:
https://github.com/hussein98912
