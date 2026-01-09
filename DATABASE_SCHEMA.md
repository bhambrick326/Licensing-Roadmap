# Licensing Roadmap - Database Schema

## Overview
The Licensing Roadmap application uses PostgreSQL for all license and user data. The database is shared with the Partner Portal application, with tables prefixed by `rs_*` (Repipe Specialists) to distinguish from Partner Portal tables (prefixed with `shop_*`).

## Database Connection
- **Host:** dpg-d4s9vjmr433s73dqeleg-a.oregon-postgres.render.com
- **Database:** repipe_portal
- **User:** repipe_admin
- **Region:** Oregon (US West)

## Schema Design

### Table Relationships
```
rs_license_holders (1) ──> (many) rs_licenses
                                     │
                                     ├──> (1) rs_license_budgets
                                     └──> (many) rs_license_costs

rs_license_holders (1) ──> (1) rs_bio_data

rs_company_coverage (independent)
```

---

## Tables

### 1. `rs_license_holders`
**Purpose:** Store information about RS employees who hold professional licenses

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| employee_id | VARCHAR(50) | NOT NULL | Unique employee identifier (e.g., 'bhambrick') |
| full_name | VARCHAR(255) | NOT NULL | Full legal name |
| role | VARCHAR(100) | NULL | Job title/role |
| pin | VARCHAR(10) | NULL | Authentication PIN |
| total_licenses | INTEGER | NULL | Count of active licenses |
| total_certificates | INTEGER | NULL | Count of certificates |
| next_target_state | VARCHAR(2) | NULL | Next state to pursue licensing in |
| status | VARCHAR(20) | NULL | Account status (active, locked, etc.) |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique constraint on `employee_id`
- Unique constraint on `pin`

**Current Data:** 3 license holders (Benjamin Hambrick, John Smith, Jay Teresi)

---

### 2. `rs_licenses`
**Purpose:** Store individual professional licenses held by employees

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| holder_id | INTEGER | NOT NULL | Foreign key to rs_license_holders |
| license_id | VARCHAR(50) | NOT NULL | Unique license identifier (e.g., 'TX-001') |
| jurisdiction | VARCHAR(255) | NOT NULL | Full state/jurisdiction name |
| jurisdiction_abbr | VARCHAR(10) | NOT NULL | State abbreviation |
| jurisdiction_type | VARCHAR(50) | NULL | Type (state, county, city) |
| license_type | VARCHAR(255) | NULL | License classification |
| license_number | VARCHAR(100) | NULL | Official license number |
| status | VARCHAR(50) | NULL | Current status (licensed, in_progress, etc.) |
| issued_on | DATE | NULL | Issue date |
| expires_on | DATE | NULL | Expiration date |
| board_name | VARCHAR(255) | NULL | Licensing board name |
| board_phone | VARCHAR(50) | NULL | Board contact phone |
| board_email | VARCHAR(255) | NULL | Board contact email |
| board_url | TEXT | NULL | Board website URL |
| designated_role | VARCHAR(255) | NULL | Role designation on license |
| renewal_period_years | INTEGER | NULL | Years between renewals |
| renewal_fee | DECIMAL(10,2) | NULL | Cost to renew |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `holder_id` references `rs_license_holders(id)` ON DELETE CASCADE
- Unique constraint on `(holder_id, license_id)`
- Index on `holder_id` for faster queries
- Index on `jurisdiction_abbr` for state-based filtering

**Current Data:** 37 licenses across multiple states

---

### 3. `rs_license_costs`
**Purpose:** Track actual expenses incurred for each license

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| license_id | INTEGER | NOT NULL | Foreign key to rs_licenses |
| date | DATE | NULL | Date of expense |
| category | VARCHAR(100) | NULL | Cost category (application_fee, test_fee, etc.) |
| amount | DECIMAL(10,2) | NULL | Expense amount |
| vendor | VARCHAR(255) | NULL | Vendor/payee name |
| notes | TEXT | NULL | Additional notes |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `license_id` references `rs_licenses(id)` ON DELETE CASCADE
- Index on `license_id` for faster queries
- Index on `date` for time-based analytics

**Current Data:** 1 cost entry

---

### 4. `rs_license_budgets`
**Purpose:** Store estimated/budgeted costs for each license

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| license_id | INTEGER | NOT NULL | Foreign key to rs_licenses (one-to-one) |
| application_fee | DECIMAL(10,2) | NULL | Estimated application cost |
| test_fee | DECIMAL(10,2) | NULL | Estimated exam cost |
| trade_book_fee | DECIMAL(10,2) | NULL | Trade exam book cost |
| business_law_book_fee | DECIMAL(10,2) | NULL | Business law book cost |
| activation_fee | DECIMAL(10,2) | NULL | License activation cost |
| prep_course_fee | DECIMAL(10,2) | NULL | Prep course cost |
| travel_estimate | DECIMAL(10,2) | NULL | Travel expenses estimate |
| shipping_estimate | DECIMAL(10,2) | NULL | Shipping/materials estimate |
| renewal_fee | DECIMAL(10,2) | NULL | Renewal cost estimate |
| continuing_ed_fee | DECIMAL(10,2) | NULL | Continuing education cost |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `license_id` references `rs_licenses(id)` ON DELETE CASCADE
- Unique constraint on `license_id` (one budget per license)

**Current Data:** 37 budget records (one per license)

---

### 5. `rs_company_coverage`
**Purpose:** Track which states RS operates in and their status

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| state_code | VARCHAR(2) | NOT NULL | State abbreviation |
| state_name | VARCHAR(100) | NULL | Full state name |
| status | VARCHAR(50) | NULL | Coverage status (licensed, in_progress, target) |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique constraint on `state_code`

**Current Data:** 9 states
- 7 licensed: TX, CA, FL, CO, WA, NV, AZ
- 1 in_progress: NM
- 1 target: NJ

---

### 6. `rs_bio_data`
**Purpose:** Store professional biographical data for license applications

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NOT NULL | Primary key |
| holder_id | INTEGER | NOT NULL | Foreign key to rs_license_holders (one-to-one) |
| personal_info | JSONB | NULL | Personal information (name, DOB, SSN, address, etc.) |
| work_history | JSONB | NULL | Array of work experience entries |
| professional_references | JSONB | NULL | Array of professional references |
| job_projects | JSONB | NULL | Array of notable plumbing projects |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `holder_id` references `rs_license_holders(id)` ON DELETE CASCADE
- Unique constraint on `holder_id` (one bio per holder)

**JSONB Structure:**

**personal_info:**
```json
{
  "full_legal_name": "Benjamin Hambrick",
  "middle_name": "Wayne",
  "date_of_birth": "1990-01-15",
  "ssn_last_4": "1234",
  "drivers_license": "TX123456789",
  "current_address": {
    "street": "123 Main St",
    "city": "Houston",
    "state": "TX",
    "zip": "77001"
  },
  "phone_cell": "555-1234",
  "email_primary": "benjamin@example.com"
}
```

**work_history:**
```json
[
  {
    "company": "Repipe Specialists",
    "position": "Master Plumber",
    "start_date": "2020-01-01",
    "end_date": null,
    "responsibilities": "License management, field operations"
  }
]
```

**professional_references:**
```json
[
  {
    "name": "John Doe",
    "title": "Master Plumber",
    "company": "ABC Plumbing",
    "phone": "555-5678",
    "email": "john@example.com",
    "relationship": "Former supervisor"
  }
]
```

**Current Data:** 0 bio records (not yet populated)

---

## Data Migration History

### Initial Migration (January 8, 2026)
- Migrated from JSON files to PostgreSQL
- Created all 6 tables with proper relationships
- Imported 37 existing licenses
- Imported 3 license holders
- Imported 9 company coverage states
- Imported all cost data and budgets

### Migration Tools
- `migrations/001_create_rs_tables.sql` - Main schema creation
- `migrations/002_create_rs_bio_data.sql` - Bio data table (fixed "references" reserved word)
- `migrate_json_to_db.py` - JSON to PostgreSQL data migration script
- `fix_coverage_migration.py` - Company coverage migration fix

---

## Data Access Patterns

### Read Operations
All read operations use SQLAlchemy ORM through `load_license_holder_data()` and `load_company_data()` functions, which return dict structures compatible with templates.

### Write Operations
All write operations use dedicated functions in `db_write_functions.py`:
- `add_license_to_db()` - Create new license
- `update_license_in_db()` - Update existing license
- `delete_license_from_db()` - Remove license
- `add_cost_to_db()` - Add cost entry
- `delete_cost_from_db()` - Remove cost entry
- `update_estimated_costs_in_db()` - Update budget
- `create_new_holder()` - Add license holder
- `update_holder_metadata()` - Update holder info
- And 10+ more specialized functions

---

## Performance Considerations

### Indexing Strategy
- Primary keys on all tables for fast lookups
- Foreign key indexes for efficient joins
- Unique constraints prevent duplicate data
- State abbreviation indexes for geographic queries

### Query Optimization
- CASCADE deletes maintain referential integrity
- JSONB columns for flexible bio data storage
- Timestamp columns track data changes
- Proper use of transactions in write operations

---

## Backup & Recovery

### Backup Strategy
- Database hosted on Render with automatic backups
- All data also version-controlled via Git commits
- JSON files retained in `data/` directory as reference

### Recovery Process
1. Database can be restored from Render backups
2. Data can be re-migrated from JSON if needed
3. Migration scripts are version-controlled

---

## Future Enhancements

### Planned Additions
- [ ] Revenue tracking column in `rs_company_coverage`
- [ ] Locked account tracking fields in `rs_license_holders`
- [ ] Training roadmap table for exam preparation
- [ ] State encyclopedia table for reference data
- [ ] Audit log table for compliance tracking

### Potential Optimizations
- [ ] Materialized views for analytics
- [ ] Full-text search on license data
- [ ] Database connection pooling
- [ ] Read replicas for reporting
