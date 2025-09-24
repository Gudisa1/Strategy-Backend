# **Partner Monitoring Dashboard – Extended TODO**

### **Goal**

Provide a **role-based partner monitoring dashboard**:

* **Low-level employees:** read-only, safe view to avoid collisions.
* **Managers / CEO:** detailed insights, including risk, status, MOUs, and project details.

---

## **1. Define Roles and Permissions**

* [ ] Roles to define:

  * `employee` → read-only, limited fields
  * `manager` / `ceo` → full access (read/write optional, mostly read)
  * `sys_admin` → full CRUD access (already exists)
* [ ] Update DRF permissions:

```python
class PartnerDashboardPermission(permissions.BasePermission):
    """
    Role-based access:
    - Employee: limited read-only
    - Manager/CEO: full read access
    - SysAdmin: everything
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if getattr(request.user, "is_sys_admin", False):
            return True
        if getattr(request.user, "role", None) in ["employee", "manager", "ceo"]:
            return view.action in ["list", "retrieve", "public_list"]
        return False
```

---

## **2. Create Role-Based Serializers**

### **A. Low-Level Employee View (Safe)**

* **Endpoint:** `/partners/public/`, `/projects/public/`
* **Fields:** Partner name, project name/type, departments
* **Exclude:** risk, status history, MOUs, financial data

```python
class EmployeePartnerSerializer(serializers.ModelSerializer):
    projects = serializers.StringRelatedField(many=True)  # only project names

    class Meta:
        model = Partner
        fields = ["id", "name", "projects"]
```

---

### **B. CEO / Manager View (Detailed)**

* **Endpoint:** `/partners/detail/`, `/projects/detail/`
* **Fields to include:**

  * Partner details: name, departments, risk level, status history
  * Projects: name, type, start/end, partners, budgets, MOUs
  * Documents: optional, based on access level
* **Serializer Example:**

```python
class ManagerPartnerSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)
    mous = MOUSerializer(many=True, read_only=True)
    risk_history = RiskLevelHistorySerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Partner
        fields = [
            "id", "name", "departments", "projects", 
            "mous", "risk_history", "status_history"
        ]
```

---

## **3. Endpoints / API**

* **Low-Level Employees:**

  * `/partners/public/` → list partners + projects (safe)
  * `/projects/public/` → list projects + partners (safe)
* **CEO / Managers:**

  * `/partners/detail/` → full partner info + MOUs, risks, status
  * `/projects/detail/` → project details + partners, departments, risk info
* **Filtering:**

  * By department, project type, start/end date, risk level (CEO)
  * Simple department/project filter (employee)

---

## **4. Frontend / Dashboard**

* **Low-Level View:**

  * Simple tables: partners → projects
  * Filters: department, project type
  * Highlights: active projects, departments responsible
* **CEO / Manager View:**

  * Tables + cards for partners
  * Show risk history, status history, MOUs
  * Search and filter by project type, risk, department, date
  * Optionally, export data to Excel or PDF

---

## **5. Swagger / API Documentation**

* [ ] Document separate endpoints for **public** vs **detailed** views:

  * `/partners/public/` → safe, employee
  * `/partners/detail/` → detailed, manager/CEO
* [ ] Make it clear which roles can access which endpoints.

---

## **6. Testing**

* [ ] Employee account:

  * Can view partner/project list (read-only)
  * Cannot see risk, MOUs, sensitive data
  * Cannot edit anything
* [ ] CEO / Manager account:

  * Can view all fields (partners, projects, risk, MOUs, status)
  * Can filter/search
  * Ensure sensitive info is protected for employees

---

## **7. Deployment**

* [ ] Add versioning: `v1/partners/public/` vs `v1/partners/detail/`
* [ ] Ensure permissions are enforced server-side
* [ ] Integrate into frontend dashboard with role-based visibility

---

✅ **Outcome:**

* Low-level employees: **safe visibility** to prevent collisions
* Managers / CEO: **full insights** for strategic decisions
* System remains secure and role-aware

