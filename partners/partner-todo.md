
# 🗂 Partner Management Schema

## 1. **Partner**

Holds the **core partner directory entry**.

| Field                | Type             | Notes                                             |
| -------------------- | ---------------- | ------------------------------------------------- |
| id (PK)              | UUID             | Unique ID                                         |
| name                 | varchar(255)     | Partner’s legal name                              |
| type                 | enum/varchar(50) | NGO, Gov, Embassy, Corporate, etc.                |
| status               | varchar(50)      | e.g., *pending, approved, suspended, blacklisted* |
| risk\_level          | varchar(50)      | e.g., *low, medium, high, critical*               |
| created\_by\_id (FK) | User             | Who onboarded the partner                         |
| created\_at          | datetime         | Auto timestamp                                    |
| updated\_at          | datetime         | Auto timestamp                                    |

**Relationships**

* Partner ↔ Department (M\:N) → Responsible departments.
* Partner ↔ User (M:1) → Onboarding/responsible user.

---

## 2. **PartnerProfile**

Contains **KYC & Due Diligence** information (one-to-one with Partner).

| Field                | Type         | Notes                                                 |
| -------------------- | ------------ | ----------------------------------------------------- |
| id (PK)              | UUID         |                                                       |
| partner\_id (FK)     | Partner      | One-to-one                                            |
| registration\_number | varchar(100) | License/tax number                                    |
| tax\_number          | varchar(100) | VAT/Tax ID                                            |
| contact\_address     | text         |                                                       |
| contact\_phone       | varchar(20)  |                                                       |
| contact\_email       | varchar(100) |                                                       |
| ownership\_structure | text         | JSON/text for shareholders, board, staff              |
| bank\_details        | text         | Could be JSON for multiple accounts                   |
| organization\_type   | varchar(50)  | NGO, Gov, Embassy, Business, etc.                     |
| legal\_history       | text         | Litigation/legal issues                               |
| social\_background   | text         | Websites, projects, presence                          |
| financial\_stability | text         | Assessment/creditworthiness                           |
| reputation           | text         | Past project performance                              |
| esg\_policies        | text         | ESG & governance notes                                |
| documents            | JSON         | Uploaded files metadata (could be separate table too) |

---

## 3. **PartnerDocuments**

(If you want granular tracking of uploads)

| Field                 | Type        | Notes                               |
| --------------------- | ----------- | ----------------------------------- |
| id (PK)               | UUID        |                                     |
| partner\_id (FK)      | Partner     |                                     |
| file\_type            | varchar(50) | e.g., registration, tax, financials |
| file\_url             | text        | Path in S3/local storage            |
| uploaded\_by\_id (FK) | User        | Who uploaded                        |
| uploaded\_at          | datetime    |                                     |

---

## 4. **StatusHistory**

Tracks partner **status changes**.

| Field                | Type        | Notes          |
| -------------------- | ----------- | -------------- |
| id (PK)              | UUID        |                |
| partner\_id (FK)     | Partner     |                |
| old\_status          | varchar(50) |                |
| new\_status          | varchar(50) |                |
| changed\_by\_id (FK) | User        | Who changed it |
| changed\_at          | datetime    |                |

---

## 5. **RiskLevelHistory**

Tracks changes in **risk level**.

| Field                | Type        | Notes |
| -------------------- | ----------- | ----- |
| id (PK)              | UUID        |       |
| partner\_id (FK)     | Partner     |       |
| old\_risk            | varchar(50) |       |
| new\_risk            | varchar(50) |       |
| changed\_by\_id (FK) | User        |       |
| changed\_at          | datetime    |       |

---

## 6. **PartnerDepartments**

(Many-to-Many relationship table: Partner ↔ Department)

| Field               | Type       | Notes |
| ------------------- | ---------- | ----- |
| id (PK)             | UUID       |       |
| partner\_id (FK)    | Partner    |       |
| department\_id (FK) | Department |       |
| assigned\_at        | datetime   |       |

---

# 🔗 Relationship Overview

```
Partner ── (1:1) ── PartnerProfile
Partner ── (M:N) ── Department
Partner ── (1:M) ── PartnerDocuments
Partner ── (1:M) ── StatusHistory
Partner ── (1:M) ── RiskLevelHistory
Partner ── (M:1) ── User (created_by / responsible)
```

---
---

---

# ✅ Partner Management API – TODO

## 1. **Models & Migrations**

* [ ] Define `Partner` model.
* [ ] Define `PartnerProfile` (One-to-One with Partner).
* [ ] Define `PartnerDocuments` (uploads).
* [ ] Define `StatusHistory`.
* [ ] Define `RiskLevelHistory`.
* [ ] Define `PartnerDepartments` (M\:N link table).
* [ ] Run migrations & verify DB schema.

---

## 2. **Serializers**

* [ ] Create `PartnerSerializer` (basic partner info).
* [ ] Create `PartnerProfileSerializer` (KYC/due diligence).
* [ ] Create `PartnerDocumentsSerializer`.
* [ ] Create `StatusHistorySerializer`.
* [ ] Create `RiskLevelHistorySerializer`.
* [ ] Nested serializers for retrieving partner with profile/documents.

---

## 3. **Views / Endpoints**

(Use DRF ViewSets / APIViews with proper permissions)

* **Partner**

  * [ ] `POST /api/partners/` → Create new partner (requires authenticated user).
  * [ ] `GET /api/partners/` → List all partners (filters: type, status, risk\_level).
  * [ ] `GET /api/partners/{id}/` → Retrieve partner details.
  * [ ] `PUT/PATCH /api/partners/{id}/` → Update partner info.
  * [ ] `DELETE /api/partners/{id}/` → Soft-delete / deactivate partner.


  <!-- Done til this Point -->

* **Partner Profile**

  * [ ] `POST /api/partners/{id}/profile/` → Create profile (if not exists).
  * [ ] `GET /api/partners/{id}/profile/` → Retrieve profile.
  * [ ] `PUT/PATCH /api/partners/{id}/profile/` → Update profile.

* **Partner Documents**

  * [ ] `POST /api/partners/{id}/documents/` → Upload document.
  * [ ] `GET /api/partners/{id}/documents/` → List all docs.
  * [ ] `GET /api/documents/{doc_id}/` → Retrieve single doc metadata.
  * [ ] `DELETE /api/documents/{doc_id}/` → Delete document.

  <!-- DONE -->

* **Status History**

  * [ ] `POST /api/partners/{id}/status/` → Change status (auto log to history).
  * [ ] `GET /api/partners/{id}/status-history/` → View history of changes.

* **Risk Level History**

  * [ ] `POST /api/partners/{id}/risk/` → Change risk level.
  * [ ] `GET /api/partners/{id}/risk-history/` → View risk history.

* **Departments**

  * [ ] `POST /api/partners/{id}/departments/` → Assign partner to department(s).
  * [ ] `GET /api/partners/{id}/departments/` → List assigned departments.
  * [ ] `DELETE /api/partners/{id}/departments/{dep_id}/` → Unassign.

---

## 4. **Permissions & Access**

* [ ] Ensure **access control** integrates with your existing auth.
* [ ] Example rules:

  * Only Admins can approve/blacklist.
  * Normal staff can onboard but not delete.
  * Departments can only view partners assigned to them.

---

## 5. **Testing with Postman**

* [ ] Create a **Partner Collection** in Postman.
* [ ] Add **environment variables** (base\_url, auth\_token, partner\_id).
* [ ] Write test requests for:

  * ✅ Create Partner → store partner\_id.
  * ✅ Add Partner Profile.
  * ✅ Upload Partner Document.
  * ✅ Change Status & Check Status History.
  * ✅ Change Risk & Check Risk History.
  * ✅ Assign Department & Verify.
* [ ] Add **Postman tests** (JS assertions) for common cases:

  * Check 201 status on creation.
  * Check response body contains `id`.
  * Ensure status/risk history entries increase after change.
* [ ] Save Postman collection → export/share for QA.

---

## 6. **Next Steps**

Once Partner Management APIs are stable:

* Proceed to **Partnership Projects API** (linking partners to specific projects).
* Proceed to **MOUs API** (tracking agreements, validity, compliance).

---
---
---

# 📑 Project-Centric Design: Projects → Partnerships → MOUs

---

## 🔹 1. **Project Model (Foundation)**

Every collaboration starts with a **Project**.

* **Attributes**:

  * `name`
  * `description`
  * `start_date`
  * `end_date`
  * `status` (planned, active, completed, on hold)

This is the **root entity**. Everything else (partners, agreements) connects back to projects.

---

## 🔹 2. **Partnership Projects API**

Defines how **partners are connected to projects**.

* **Attributes**:

  * `project` (FK → Project ✅ foundation)
  * `partner` (FK → Partner)
  * `role` (lead, funder, contributor, etc.)
  * `contribution` (optional: financial, in-kind, hours, etc.)
  * `start_date`
  * `end_date`
  * `status` (active, completed, withdrawn)

* **Logic**:

  * Many-to-many (a project can have many partners, a partner can join many projects).
  * Timelines define involvement periods.
  * Status tracks participation stage.

* **Use Cases**:

  * Get all partners of a project.
  * See all projects a partner is involved in.
  * Filter partners by role (e.g., "find all funders").

---

## 🔹 3. **MOUs API**

Formal **legal agreements** with partners.

* Although an MOU is mainly **between the org and a partner**, it may also **govern a specific project**.

* **Attributes**:

  * `partner` (FK → Partner ✅ always linked to a partner)
  * `project` (optional FK → Project ✅ if MOU is tied to a specific project)
  * `title` / `subject`
  * `mou_file` (immutable, no edits/deletes)
  * `status` (Draft, Active, Expired, Terminated)
  * `start_date`
  * `end_date`
  * `created_at` (timestamp)

* **Rules**:

  * File immutability: once uploaded, cannot be edited/deleted.
  * Versioning: new MOU = new record.
  * Status automation: auto-expire when end\_date passes.
  * Always linked to a **partner**, optionally linked to a **project**.

* **Use Cases**:

  * See all MOUs of a partner.
  * Query active/expired agreements.
  * Trace which project(s) an MOU governs.

---

## 🔗 Relationships Recap

* **Project** (root)

  * ↔ **Partners** → via **Partnership Projects API**
  * ↔ **MOUs** → optional legal link (agreement covering this project)

* **Partner**

  * Can appear in multiple projects.
  * Can have multiple MOUs (across time/projects).

---



🔹 What we’ll need to build now:

Serializers

ProjectSerializer (basic project CRUD).

PartnershipProjectSerializer (linking partner + project + role).

Views / Endpoints

Projects:

GET /projects/ → list projects.

POST /projects/ → create a new project.

GET /projects/{id}/ → retrieve single project.

PUT/PATCH /projects/{id}/ → update project.

DELETE /projects/{id}/ → delete project.

PartnershipProjects:

GET /partnerships/ → list all partner-project links.

POST /partnerships/ → create a new link (add partner to project).

GET /partnerships/{id}/ → retrieve details.

PUT/PATCH /partnerships/{id}/ → update role, contribution, dates.

DELETE /partnerships/{id}/ → remove link.

Nested convenience endpoints (optional, but recommended)

GET /projects/{id}/partners/ → list partners in a project.

GET /partners/{id}/projects/ → list projects for a partner