# Licensing Roadmap - Database Schema Documentation
**Version:** 1.0  
**Date:** December 22, 2024  
**Purpose:** Schema documentation for Atlas Compliance Hub module integration

---

## Overview
The Licensing Roadmap uses a **JSON file-based data structure** organized in the `/data` directory. This schema is designed to be modular and can integrate with the Partner Portal as part of the Atlas Compliance Hub.

---

## Directory Structure
```
data/
├── license_holders/          # Individual license holder profiles
│   ├── bhambrick.json
│   └── jsmith.json
├── company/                  # Company-wide coverage data
│   └── coverage.json
├── state_details/            # State-specific licensing requirements (50 files)
│   ├── CA.json
│   ├── TX.json
│   └── ...
├── base_data/                # Reference data
│   └── all_states.json
└── training_roadmaps/        # Career progression paths
    └── master_plumber_southwest.json
```

---

## Entity Schemas

### 1. License Holder (`license_holders/{user_id}.json`)

**Purpose:** Individual employee/contractor license portfolio
```json
{
  "user_id": "string (unique identifier)",
  "name": "string (full legal name)",
  "role": "string (job title/role)",
  "total_licenses": "integer (count of active licenses)",
  "total_certificates": "integer (count of certificates)",
  "licenses": [
    {
      "license_id": "string (unique: STATE-###)",
      "jurisdiction": "string (full state name)",
      "jurisdiction_abbr": "string (2-letter state code)",
      "jurisdiction_type": "string (state|county|city)",
      "license_type": "string (Plumbing Contractor|Master Plumber|etc)",
      "status": "string (licensed|in_progress|expired|not_licensed)",
      "license_number": "string (state-issued number)",
      "issued_on": "date (YYYY-MM-DD)",
      "expires_on": "date (YYYY-MM-DD)",
      "designated_role": "string (master_of_record|qualifier|other)",
      "estimated_costs": {
        "application_fee": "float",
        "test_fee": "float",
        "trade_book_fee": "float",
        "business_law_book_fee": "float",
        "activation_fee": "float",
        "prep_course_fee": "float",
        "travel_fee": "float",
        "shipping_fee": "float"
      },
      "recurring": {
        "renewal_fee": "float",
        "continuing_ed_fee": "float",
        "renewal_period_years": "integer"
      },
      "planning": {
        "est_study_hours": "integer",
        "test_duration_hours": "float"
      },
      "board_name": "string (regulatory agency name)",
      "board_phone": "string (contact phone)",
      "board_url": "string|null (website URL)",
      "actual_costs": [
        {
          "date": "date (YYYY-MM-DD)",
          "amount": "float",
          "category": "string (application|renewal|test|etc)",
          "description": "string",
          "receipt_url": "string|null"
        }
      ]
    }
  ]
}
```

**Key Relationships:**
- `user_id` → Links to authentication system
- `jurisdiction_abbr` → Links to `state_details/{abbr}.json`
- `designated_role` → Indicates master of record responsibility

---

### 2. Company Coverage (`company/coverage.json`)

**Purpose:** Company-wide licensing status and market expansion tracking
```json
{
  "company_name": "string (organization name)",
  "total_license_holders": "integer (count of employees)",
  "total_states_covered": "integer (count of licensed states)",
  "total_states_in_progress": "integer (count of pending states)",
  "covered_states": [
    "string (2-letter state code)"
  ],
  "in_progress_states": [
    "string (2-letter state code)"
  ],
  "target_states": [
    "string (2-letter state code)"
  ],
  "state_revenues": {
    "TX": "float (annual revenue in state)",
    "CA": "float"
  },
  "license_holders": [
    "string (user_id references)"
  ]
}
```

**Key Relationships:**
- `license_holders[]` → Array of `user_id` references
- `covered_states[]` → Array of state codes
- Used for Director Dashboard and company-wide analytics

---

### 3. State Details (`state_details/{STATE}.json`)

**Purpose:** Comprehensive state licensing requirements encyclopedia
```json
{
  "state_code": "string (2-letter code)",
  "state_name": "string (full state name)",
  "board_name": "string (regulatory board name)",
  "board_website": "string (official URL)",
  "board_phone": "string (contact)",
  "board_address": "string (physical address)",
  "license_types": [
    {
      "type": "string (C-36 Plumbing|Master Plumber|etc)",
      "description": "string",
      "requirements": {
        "experience_years": "integer",
        "experience_description": "string",
        "education": "string|null",
        "exam_required": "boolean"
      }
    }
  ],
  "examination": {
    "provider": "string (PSI|Prometric|State Board)",
    "format": "string (computer-based|paper|practical)",
    "cost_estimate": "float",
    "books_required": "string",
    "test_details": {
      "law_business": {
        "questions": "integer",
        "duration_hours": "float",
        "passing_score": "string (72%)"
      },
      "trade_exam": {
        "questions": "integer",
        "duration_hours": "float",
        "passing_score": "string"
      }
    }
  },
  "application_process": [
    {
      "step": "integer",
      "description": "string (detailed step)"
    }
  ],
  "costs": {
    "application": "float",
    "exam": "float",
    "initial_license": "float",
    "renewal_biennial": "float",
    "continuing_education": "float"
  },
  "renewal": {
    "frequency": "string (biennial|annual)",
    "deadline": "string (description)",
    "continuing_education_hours": "integer"
  },
  "reciprocity": {
    "available": "boolean",
    "states_accepted": ["string"],
    "requirements": "string"
  },
  "common_pitfalls": [
    "string (warning/tip)"
  ],
  "helpful_resources": [
    {
      "title": "string",
      "url": "string",
      "description": "string"
    }
  ],
  "last_updated": "date (YYYY-MM-DD)"
}
```

**Key Relationships:**
- `state_code` → Referenced by `jurisdiction_abbr` in licenses
- Used for application guidance and requirement lookup

---

### 4. Base States (`base_data/all_states.json`)

**Purpose:** Reference data for all 50 US states
```json
{
  "AL": {
    "name": "Alabama",
    "status": "not_licensed"
  },
  "AK": {
    "name": "Alaska",
    "status": "not_licensed"
  }
}
```

**Key Relationships:**
- Used to populate map with all states
- Default status before licenses are added

---

### 5. Training Roadmaps (`training_roadmaps/{roadmap_id}.json`)

**Purpose:** Career progression and multi-state licensing strategies
```json
{
  "roadmap_id": "string (unique identifier)",
  "title": "string (roadmap name)",
  "description": "string",
  "target_role": "string (Master Plumber|etc)",
  "path": [
    {
      "step": "integer (sequence order)",
      "state": "string (state code)",
      "state_name": "string",
      "rationale": "string (why this state/order)",
      "priority": "string (critical|high|medium|low)",
      "estimated_timeline": "string (6 months|1 year)",
      "prerequisites": [
        "string (previous step requirement)"
      ]
    }
  ],
  "total_estimated_cost": "float",
  "total_estimated_timeline": "string",
  "created_date": "date (YYYY-MM-DD)"
}
```

**Key Relationships:**
- `state` → Links to state_details
- Used for strategic expansion planning

---

## Authentication & Access Control

### User Types
```json
{
  "user_type": "manager|license_holder",
  "user_id": "string (unique identifier)",
  "pin": "string (6-digit PIN)",
  "name": "string (full name)",
  "permissions": {
    "can_view_all_holders": "boolean",
    "can_edit_licenses": "boolean",
    "can_access_costs": "boolean",
    "can_manage_team": "boolean"
  }
}
```

**Current PINs:**
- Manager: `100001`
- License Holder (bhambrick): `200001`
- License Holder (jsmith): `200002`

---

## Data Flows & Calculations

### 1. Days Remaining Calculation
```python
def calculate_days_remaining(expires_on):
    if not expires_on:
        return None
    expiry = datetime.strptime(expires_on, '%Y-%m-%d')
    today = datetime.now()
    return (expiry - today).days
```

### 2. Status Classification
```python
def get_state_status_class(state_data):
    if state_data['status'] == 'licensed':
        days = calculate_days_remaining(state_data.get('expires_on'))
        if days < 0: return 'overdue'
        if days <= 30: return 'due-soon'
        return 'licensed'
    elif state_data['status'] == 'in_progress':
        return 'in_progress'
    else:
        return 'not_licensed'
```

### 3. Cost Aggregation
```python
def calculate_total_costs(license):
    estimated = sum(license['estimated_costs'].values())
    actual = sum(cost['amount'] for cost in license.get('actual_costs', []))
    return {'estimated': estimated, 'actual': actual}
```

---

## Integration Points for Atlas Compliance Hub

### Shared Entities
1. **Users/Employees** - Both modules need employee records
2. **Company Profile** - Shared organization data
3. **State Coverage** - Market presence tracking
4. **Cost Tracking** - Financial reporting across modules

### Proposed Unified Schema
```json
{
  "compliance_hub": {
    "modules": {
      "licensing_roadmap": {
        "license_holders": "...",
        "state_details": "...",
        "training_roadmaps": "..."
      },
      "partner_portal": {
        "partners": "...",
        "certifications": "...",
        "vendor_relationships": "..."
      }
    },
    "shared": {
      "company": {
        "org_id": "repipe_specialists",
        "name": "Repipe Specialists",
        "states_active": [],
        "employees": []
      },
      "users": {
        "user_id": "unique_id",
        "name": "string",
        "role": "string",
        "modules_access": ["licensing_roadmap", "partner_portal"],
        "permissions": {}
      }
    }
  }
}
```

### API Endpoints (Future)
When migrating to database:
- `GET /api/licenses?user_id={id}`
- `GET /api/states/{state_code}/requirements`
- `GET /api/company/coverage`
- `POST /api/licenses` - Add new license
- `PUT /api/licenses/{license_id}` - Update license
- `GET /api/costs/analytics`

---

## Migration Path to Relational Database

### Proposed SQL Schema
```sql
-- Users Table (Shared across modules)
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    user_type ENUM('manager', 'license_holder'),
    pin_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Licenses Table
CREATE TABLE licenses (
    license_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    jurisdiction_abbr CHAR(2),
    jurisdiction_name VARCHAR(100),
    license_type VARCHAR(100),
    status ENUM('licensed', 'in_progress', 'expired', 'not_licensed'),
    license_number VARCHAR(100),
    issued_on DATE,
    expires_on DATE,
    designated_role VARCHAR(50),
    board_name VARCHAR(255),
    board_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- License Costs Table
CREATE TABLE license_costs (
    cost_id INT AUTO_INCREMENT PRIMARY KEY,
    license_id VARCHAR(50) REFERENCES licenses(license_id),
    cost_type ENUM('estimated', 'actual'),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    date DATE,
    description TEXT,
    receipt_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- State Details Table
CREATE TABLE state_details (
    state_code CHAR(2) PRIMARY KEY,
    state_name VARCHAR(100),
    board_name VARCHAR(255),
    board_website VARCHAR(500),
    board_phone VARCHAR(50),
    board_address TEXT,
    content JSON,  -- Store full state requirements as JSON
    last_updated DATE
);

-- Company Coverage Table
CREATE TABLE company_coverage (
    coverage_id INT AUTO_INCREMENT PRIMARY KEY,
    state_code CHAR(2),
    status ENUM('covered', 'in_progress', 'target'),
    annual_revenue DECIMAL(15,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## File Naming Conventions

1. **License Holders:** `{user_id}.json` (lowercase, no spaces)
2. **State Details:** `{STATE_CODE}.json` (uppercase 2-letter code)
3. **Training Roadmaps:** `{descriptive_name}.json` (lowercase, underscores)
4. **Backup Files:** `{original_name}.backup` or `{original_name}.{date}.json`

---

## Version Control & Backups

- All data files tracked in Git
- Backup files excluded via `.gitignore`
- State: `templates/*.backup`, `data/*.backup`

---

## Notes for Partner Portal Integration

When integrating with Partner Portal, consider:

1. **Shared User Table** - Single source of truth for employees
2. **Unified Dashboard** - Combined compliance metrics
3. **Cross-Module Reporting** - Licensing + Partner certifications
4. **Shared State Data** - Both modules need state-specific info
5. **Common Cost Tracking** - Aggregate all compliance costs

---

## Contact & Maintenance

**Module Owner:** Benjamin Hambrick  
**Repository:** github.com/bhambrick326/Licensing-Roadmap  
**Last Schema Update:** December 22, 2024

---

*This schema documentation should be updated whenever data structures change.*
