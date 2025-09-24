
# 📘 Strategy Backend API Documentation

## 1. Overview

This project is a **Django REST Framework (DRF)** backend that provides APIs for managing:

* Users, Roles, and Permissions
* Departments and User-Department assignments
* Partners, their profiles, documents, statuses, and risk levels
* Projects, Project-Partner relationships, and MOUs
* Authentication with **JWT tokens**

The API is self-documented using **Swagger UI** at:
👉 [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

---

## 2. Running the API

### 2.1 Start Server

```bash
python manage.py runserver
```

API base URL:

```
http://127.0.0.1:8000/api/
```

### 2.2 Swagger & API Docs

* Swagger UI → [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
* OpenAPI JSON → [http://127.0.0.1:8000/swagger/?format=openapi](http://127.0.0.1:8000/swagger/?format=openapi)

---

## 3. Authentication

The project uses **JWT Authentication**.

### Obtain Access/Refresh Tokens

```
POST /token/
```

Body:

```json
{
  "username": "admin",
  "password": "password123"
}
```

Response:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

Use in headers:

```
Authorization: Bearer <access_token>
```

### Refresh Token

```
POST /token/refresh/
```

---

## 4. Models

Swagger lists these models:

* **User**
* **Role**
* **Permission**
* **Department**
* **Partner**
* **PartnerProfile**
* **PartnerDocument**
* **StatusHistory**
* **RiskLevelHistory**
* **Project**
* **PartnershipProject (Project-Partner link)**
* **MOU**
* **TokenObtainPair** (auth)
* **TokenRefresh** (auth)

---

## 5. Endpoints

Below is a categorized list of endpoints (from Swagger):

### 🔑 Auth

* `POST /token/` – Obtain JWT token
* `POST /token/refresh/` – Refresh JWT

---

### 👤 Users & Admins

* `GET /users/` – List users
* `POST /users/` – Create user
* `GET /users/{id}/` – Retrieve user
* `PUT /users/{id}/` – Update user
* `PATCH /users/{id}/` – Partial update
* `DELETE /users/{id}/` – Delete user

Admin-specific:

* `GET /admin/` – List admins
* `POST /admin/` – Create admin
* `POST /admin/create_admin/` – Special admin creation
* `GET /admin/{id}/` – Retrieve admin
* `PUT /admin/{id}/` – Update admin
* `PATCH /admin/{id}/` – Partial update
* `DELETE /admin/{id}/` – Delete admin

---

### 🏢 Departments

* `GET /departments/` – List departments
* `POST /departments/` – Create department
* `GET /departments/{id}/` – Retrieve
* `PUT /departments/{id}/` – Update
* `PATCH /departments/{id}/` – Partial update
* `DELETE /departments/{id}/` – Delete

---

### 🧾 Roles & Permissions

Roles:

* `GET /roles/`
* `POST /roles/`
* `GET /roles/{id}/`
* `PUT /roles/{id}/`
* `PATCH /roles/{id}/`
* `DELETE /roles/{id}/`

Permissions:

* `GET /permissions/`
* `POST /permissions/`
* `GET /permissions/{id}/`
* `PUT /permissions/{id}/`
* `PATCH /permissions/{id}/`
* `DELETE /permissions/{id}/`

---

### 👥 User-Departments

* `GET /user_departments/` – List assignments
* `POST /user_departments/` – Assign
* `DELETE /user_departments/{id}/` – Remove assignment

---

### 🤝 Partners

* `GET /partners/` – List partners
* `POST /partners/` – Create
* `GET /partners/{id}/` – Retrieve
* `PUT /partners/{id}/` – Update
* `PATCH /partners/{id}/` – Partial update
* `DELETE /partners/{id}/` – Delete

#### Partner Extensions:

* `POST /partners/{id}/change_risk/` – Update risk level
* `GET /partners/{id}/risk_history/` – Risk history
* `POST /partners/{id}/status/` – Change status
* `GET /partners/{id}/status-history/` – Status history

#### Departments for Partners:

* `POST /partners/{id}/departments/` – Assign departments
* `DELETE /partners/{id}/departments/{dept_id}/` – Unassign
* `GET /partners/{id}/list_departments/` – List assigned

#### Partner Profiles:

* `GET /partners/{id}/profile/`
* `POST /partners/{id}/profile/`
* `PUT /partners/{id}/profile/`
* `PATCH /partners/{id}/profile/`

#### Partner Documents:

* `GET /partners/{partner_pk}/documents/`
* `POST /partners/{partner_pk}/documents/`
* `GET /partners/{partner_pk}/documents/{id}/`
* `PUT /partners/{partner_pk}/documents/{id}/`
* `PATCH /partners/{partner_pk}/documents/{id}/`
* `DELETE /partners/{partner_pk}/documents/{id}/`

---

### 📂 Projects & Partnerships

Projects:

* `GET /projects/`
* `POST /projects/`
* `GET /projects/{id}/`
* `PUT /projects/{id}/`
* `PATCH /projects/{id}/`
* `DELETE /projects/{id}/`
* `GET /projects/{id}/partners/` – List partners in project

Project-Partners:

* `GET /project-partners/`
* `POST /project-partners/`
* `GET /project-partners/{id}/`
* `PUT /project-partners/{id}/`
* `PATCH /project-partners/{id}/`
* `DELETE /project-partners/{id}/`
* `GET /project-partners/by-partner/{partner_id}/` – Projects of a partner
* `GET /project-partners/by-project/{project_id}/role/{role}/` – Partners by role

---

### 📜 MOUs

* `GET /mous/` – List
* `POST /mous/` – Create
* `GET /mous/{id}/` – Retrieve
* `PUT /mous/{id}/` – Update
* `PATCH /mous/{id}/` – Partial update
* `DELETE /mous/{id}/` – Delete

---

### 📑 Documents (generic, not partner-specific)

* `GET /documents/`
* `POST /documents/`
* `GET /documents/{id}/`
* `PUT /documents/{id}/`
* `PATCH /documents/{id}/`
* `DELETE /documents/{id}/`

---

## 6. Error Handling

* **401 Unauthorized** → Missing or invalid token
* **403 Forbidden** → Permission denied
* **404 Not Found** → Object doesn’t exist
* **409 Conflict** → Duplicate assignment (e.g., partner already linked to project)

---

