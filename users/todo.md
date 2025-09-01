## Core API Endpoints for Access Control

### 1. **User Management**

* `POST /api/users/`
  Create a new user (by Sys Admin only)

* `GET /api/users/`
  List users (Sys Admin: all users; others: filtered by department/permissions)

* `GET /api/users/{id}/`
  Get user details

* `PUT /api/users/{id}/`
  Update user info (Sys Admin or user themselves, depending on permissions)

* `DELETE /api/users/{id}/`
  Delete a user (Sys Admin only)

---

### 2. **Role Management**

* `POST /api/roles/`
  Create role (Sys Admin only)

* `GET /api/roles/`
  List all roles

* `GET /api/roles/{id}/`
  Role details

* `PUT /api/roles/{id}/`
  Update role info (Sys Admin only)

* `DELETE /api/roles/{id}/`
  Delete role (Sys Admin only)

---

### 3. **Permission Management**

* `GET /api/permissions/`
  List all permissions (view only; create/update not typical)

---

### 4. **User-Roles Assignment**

* `POST /api/user_roles/`
  Assign role to user (Sys Admin only)

* `DELETE /api/user_roles/{id}/`
  Remove role from user (Sys Admin only)

* `GET /api/user_roles/?user_id={user_id}`
  List roles assigned to a user

---

### 5. **Role-Permissions Assignment**

* `POST /api/role_permissions/`
  Assign permission to a role (Sys Admin only)

* `DELETE /api/role_permissions/{id}/`
  Remove permission from role (Sys Admin only)

* `GET /api/role_permissions/?role_id={role_id}`
  List permissions of a role

---

### 6. **Department Management**

* `POST /api/departments/`
  Create a department (Sys Admin only)

* `GET /api/departments/`
  List all departments

* `GET /api/departments/{id}/`
  Department details

* `PUT /api/departments/{id}/`
  Update department info (Sys Admin only)

* `DELETE /api/departments/{id}/`
  Delete department (Sys Admin only)

---

### 7. **User-Departments Assignment**

* `POST /api/user_departments/`
  Assign user to department (Sys Admin only)

* `DELETE /api/user_departments/{id}/`
  Remove user from department (Sys Admin only)

* `GET /api/user_departments/?user_id={user_id}`
  List departments assigned to user

---

## Additional Functionalities Based on Your Description

### Permission checks should cover:

* **Sys Admin:** Has all permissions (no restriction)
* **Other Users:** Permissions depend on assigned roles & their permissions

### Role Examples You Mentioned

* Department Manager
* Team Lead
* Business Manager
* Branch Manager
* Director
* Senior Director
* VP
* etc.

Each role will have a specific set of permissions mapped.

---

## Minimal Permissions to Cover Your Use Cases

| Permission Name          | Description                     | Example Endpoint Use Case          |
| ------------------------ | ------------------------------- | ---------------------------------- |
| view\_partners           | View partner data               | `GET /api/partners/`               |
| add\_partners            | Add partners                    | `POST /api/partners/`              |
| edit\_partners           | Edit partners                   | `PUT /api/partners/{id}/`          |
| delete\_partners         | Delete partners                 | `DELETE /api/partners/{id}/`       |
| manage\_mous             | Manage MOUs                     | `POST/PUT/DELETE /api/mous/`       |
| view\_analysis           | View analysis reports           | `GET /api/analysis/`               |
| manage\_users            | Create/update/delete users      | `POST/PUT/DELETE /api/users/`      |
| access\_all\_departments | Access data of all departments  | Restrict user data filtering       |
| access\_own\_departments | Access only own department data | Restrict user data filtering       |
| approve\_partners        | Approve partner applications    | `POST /api/partners/{id}/approve/` |
| export\_data             | Export partner/analysis data    | `GET /api/partners/export/`        |

---

## How to Enforce This?

* When a user calls an API endpoint, your backend checks:

  * Is user active?
  * Does user have any roles?
  * Do any of these roles have required permission for this endpoint/action?
  * Does department-level access restriction apply?

* For example:

  * A Team Lead with `view_partners` and `access_own_departments` can only see partners within their departments.
  * A Sys Admin bypasses all checks.

---

## Summary

| Entity           | Minimum API endpoints                 |
| ---------------- | ------------------------------------- |
| Users            | CRUD (restricted to Sys Admin)        |
| Roles            | CRUD (Sys Admin)                      |
| Permissions      | Read only (manage via Roles)          |
| Departments      | CRUD (Sys Admin)                      |
| User-Roles       | Assign/Remove Roles (Sys Admin)       |
| Role-Permissions | Assign/Remove Permissions (Sys Admin) |
| User-Departments | Assign/Remove Departments (Sys Admin) |

---



Got it — let’s **optimize and focus the Access Control API design** specifically for your Strategic Partnership Monitoring System to make it robust, clear, and maintainable.

---

# Optimized Access Control API Design

---

## Key Principles

* **Separation of Concerns:**
  Keep management of Users, Roles, Permissions, and Departments modular.

* **Minimal Endpoints with Flexibility:**
  Use filtering and nested endpoints for efficient data management.

* **Permission & Role Granularity:**
  Support hierarchical and fine-grained access control.

* **Auditability:**
  Track changes on assignments (who assigned what, when).

---

## Core Entities & Relationships

| Entity              | Responsibility                           |
| ------------------- | ---------------------------------------- |
| **Users**           | System users (Sys Admin + regular users) |
| **Roles**           | Named sets of permissions                |
| **Permissions**     | Atomic allowed actions/rights            |
| **Departments**     | Organizational units                     |
| **UserRoles**       | Assign users to roles                    |
| **RolePermissions** | Assign permissions to roles              |
| **UserDepartments** | Assign users to departments              |

---

## Refined API Endpoints

### 1. Users

* `GET /api/users/`

  * List users - Done
  * Filters: `?department=`, `?role=`, `?is_active=`
  * Sys Admin sees all; others limited by `access_own_departments` or `access_all_departments`

* `POST /api/users/`

  * Create user (Sys Admin only)

* `GET /api/users/{id}/`

  * Get user detail

* `PATCH /api/users/{id}/`

  * Partial update (Sys Admin or self with permission)

* `DELETE /api/users/{id}/`

  * Delete user (Sys Admin only)

* `GET /api/users/{id}/roles/`

  * List roles assigned to user

* `POST /api/users/{id}/roles/`

  * Assign roles (Sys Admin only)

* `DELETE /api/users/{id}/roles/{role_id}/`

  * Remove role (Sys Admin only)

* `GET /api/users/{id}/departments/`

  * List departments assigned to user

* `POST /api/users/{id}/departments/`

  * Assign department (Sys Admin only)

* `DELETE /api/users/{id}/departments/{department_id}/`

  * Remove department (Sys Admin only)

---

### 2. Roles

* `GET /api/roles/`

  * List roles

* `POST /api/roles/`

  * Create role (Sys Admin only)

* `GET /api/roles/{id}/`

  * Role detail

* `PATCH /api/roles/{id}/`

  * Update role (Sys Admin only)

* `DELETE /api/roles/{id}/`

  * Delete role (Sys Admin only)

* `GET /api/roles/{id}/permissions/`

  * List permissions assigned to role

* `POST /api/roles/{id}/permissions/`

  * Assign permissions (Sys Admin only)

* `DELETE /api/roles/{id}/permissions/{permission_id}/`

  * Remove permission (Sys Admin only)

---

### 3. Permissions

* `GET /api/permissions/`

  * List all permissions

* `GET /api/permissions/{id}/`

  * Permission details

*(Permissions are typically static and managed by Sys Admin only through Roles)*

---

### 4. Departments

* `GET /api/departments/`

  * List departments

* `POST /api/departments/`

  * Create department (Sys Admin only)

* `GET /api/departments/{id}/`

  * Department details

* `PATCH /api/departments/{id}/`

  * Update (Sys Admin only)

* `DELETE /api/departments/{id}/`

  * Delete (Sys Admin only)

---

## Access Control Enforcement Strategy

| Feature                     | Implementation Notes                                                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Sys Admin Full Access**   | Bypass all checks for users with `sys_admin` role or a special flag.                                                           |
| **Role-Based Access**       | Check if user has role with required permission for the API action.                                                            |
| **Department-Based Access** | Filter data by user’s assigned departments, unless user has `access_all_departments` permission.                               |
| **Hierarchical Roles**      | Implement role precedence or composite roles if needed (e.g., Director > Branch Manager).                                      |
| **Permission Checks**       | Use custom DRF permissions classes to enforce checks per endpoint/action.                                                      |
| **Audit Logging**           | Track all changes to assignments (user-role, role-permission, user-department) with timestamps and user performing the change. |

---

## Example Permissions List (based on your description)

| Permission Code         | Description                      |
| ----------------------- | -------------------------------- |
| `partner_view`          | View partners                    |
| `partner_add`           | Add partners                     |,
| `partner_edit`          | Edit partners                    |
| `partner_delete`        | Delete partners                  |
| `mou_manage`            | Add/Edit/Delete MOUs             |
| `analysis_view`         | View analysis reports            |
| `user_manage`           | Manage system users              |
| `department_access_all` | Access all departments           |
| `department_access_own` | Access own assigned departments  |
| `partner_approve`       | Approve partners                 |
| `data_export`           | Export partner and analysis data |

---

## Suggested Improvements

* **Role Hierarchy:** Add `parent_role_id` on roles table to support inheritance or simpler role escalation.

* **Dynamic Permissions:** Support permission groups or tags to simplify assigning large permission sets.

* **API Pagination & Filtering:** For `GET` endpoints with lists, add pagination, filtering by name, role, department, etc.

* **Batch Operations:** Support bulk assign/unassign roles and permissions for efficiency.

---

## Summary: Minimum API Surface for Access Control

| Entity        | Actions                                        |
| ------------- | ---------------------------------------------- |
| Users         | CRUD, assign/unassign roles and departments    |
| Roles         | CRUD, assign/unassign permissions              |
| Permissions   | Read only                                      |
| Departments   | CRUD, assign/unassign users                    |
| Access checks | Role + Permission + Department-based filtering |

---

If you'd like, I can also provide **example Django REST Framework permission classes, serializers, or views** to implement this architecture — just say the word!


<!-- 
name: CI/CD Docker Deploy

on:
  push:
    branches:
      - main

jobs:
  build_and_push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_ACCESS_TOKEN }}
          registry: docker.io

      - name: Build Django image
        run: docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/strategybackend-web:latest -f Dockerfile .

      - name: Push Django image
        run: docker push ${{ secrets.DOCKERHUB_USERNAME }}/strategybackend-web:latest

  deploy:
    runs-on: ubuntu-latest
    needs: build_and_push
    steps:
      - name: Install SSH
        run: sudo apt-get update && sudo apt-get install -y openssh-client

      - name: Setup SSH agent
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.EC2_SSH_PRIVATE_KEY }}

      - name: Deploy on EC2
        run: |
          ssh -o StrictHostKeyChecking=no ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} "
            if [ ! -d ~/strategybackend ]; then
              git clone https://x-access-token:${{ secrets.PERSONAL_ACCESS_TOKEN }}@github.com/Gudisa1/Strategy-Backend.git ~/strategybackend \
                --branch main --single-branch --quiet --depth 1

            fi
            cd ~/strategybackend &&
            git pull https://x-access-token:${{ secrets.PERSONAL_ACCESS_TOKEN }}@github.com/Gudisa1/Strategy-Backend.git main &&

            # Write env file
            cat > .env <<EOL
            SECRET_KEY=${{ secrets.SECRET_KEY }}
            DEBUG=${{ secrets.DEBUG }}
            POSTGRES_DB=${{ secrets.POSTGRES_DB }}
            POSTGRES_USER=${{ secrets.POSTGRES_USER }}
            POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}
            DB_HOST=${{ secrets.DB_HOST }}
            DB_PORT=${{ secrets.DB_PORT }}
            ALLOWED_HOSTS=${{ secrets.ALLOWED_HOSTS }}
            EOL

            docker compose -f docker-compose.prod.yml down
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d --build
          " -->
