# 🏗️ Licensing Roadmap

A comprehensive professional license tracking and management system for Repipe Specialists' compliance department.

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://licensing-roadmap.onrender.com)
[![Database](https://img.shields.io/badge/database-PostgreSQL-blue)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)

**Live Application:** [https://licensing-roadmap.onrender.com](https://licensing-roadmap.onrender.com)

---

## 📋 Overview

The Licensing Roadmap is an internal compliance tool that tracks professional plumbing licenses across all 50 U.S. states. It serves as the comprehensive license management module within the larger Atlas Compliance Hub system.

### Key Features

✅ **License Management**
- Track 37+ active licenses across multiple states
- Monitor expiration dates and renewal requirements
- Manage license status (licensed, in_progress, target)
- Store detailed board information and requirements

✅ **Cost Analytics**
- Track actual costs per license
- Budget planning with estimated costs
- Variance analysis (budget vs actual)
- Year-over-year cost breakdowns
- Export reports to PDF

✅ **Interactive Mapping**
- Four view modes: License Status, Expiration Tracker, Leadership View, Training Roadmap
- Mapbox-powered interactive U.S. map
- Visual status indicators by state
- Click states for detailed information

✅ **Director Dashboard**
- Company-wide license statistics
- Team member overview
- Cost analytics across all license holders
- Active states management

✅ **State Encyclopedia**
- Comprehensive licensing requirements by state
- CSLB (California) fully documented
- Application processes and timelines
- Examination requirements
- Insurance and bonding information

✅ **Bio Data Management**
- Professional work history tracking
- Reference management
- Notable project documentation
- Application-ready data export

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.12
- Flask 3.0 (Web Framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Gunicorn (WSGI Server)

**Frontend:**
- HTML5 / CSS3 / JavaScript
- Bootstrap 5
- Mapbox GL JS
- Chart.js

**Infrastructure:**
- Render (Cloud Hosting)
- PostgreSQL Database (Shared with Partner Portal)
- Git (Version Control)

### Database Architecture

The application uses a **shared PostgreSQL database** with the Partner Portal:
- **Licensing Roadmap Tables:** Prefixed with `rs_*` (Repipe Specialists)
- **Partner Portal Tables:** Prefixed with `shop_*`

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete schema documentation.

**Tables:**
1. `rs_license_holders` - Employee license holder information
2. `rs_licenses` - Individual license records (37 licenses)
3. `rs_license_costs` - Actual expense tracking
4. `rs_license_budgets` - Estimated cost planning
5. `rs_company_coverage` - RS active states (9 states)
6. `rs_bio_data` - Professional biographical data (JSONB)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Git

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/bhambrick326/Licensing-Roadmap.git
cd Licensing-Roadmap

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo 'DATABASE_URL=postgresql://user:password@host:port/database' > .env

# Run database migrations (if needed)
python migrate_json_to_db.py

# Start the development server
python app.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

The application is deployed on Render with automatic deployments from the `main` branch.

**Deployment Steps:**
1. Push to GitHub `main` branch
2. Render automatically builds and deploys
3. Environment variables configured in Render dashboard
4. Database connection uses shared PostgreSQL instance

---

## 🔐 Authentication

The application uses a PIN-based authentication system with two user types:

**Manager Access:**
- PIN: `100001`
- Full system access
- Can manage all license holders
- Director dashboard access
- Admin features enabled

**License Holder Access:**
- PIN: `200001` (John Smith)
- PIN: `200002` (Benjamin Hambrick)
- View own licenses and costs
- Update personal information
- Limited to own data

---

## 📊 Core Features

### 1. License Management
- **View Licenses:** Browse all licenses with filtering and search
- **Add License:** Create new license entries with full metadata
- **Edit License:** Update status, expiration dates, board info
- **Delete License:** Remove outdated or incorrect entries
- **Bulk Import:** Excel-based batch updates

### 2. Cost Tracking
- **Add Costs:** Record actual expenses by category
- **Delete Costs:** Remove incorrect entries
- **Cost Analytics:** View spending by year, category, license
- **Budget vs Actual:** Track variance against estimates
- **PDF Export:** Generate professional cost reports

### 3. State Encyclopedia
- **Licensing Requirements:** Detailed info per state
- **Board Information:** Contact details and URLs
- **Application Process:** Step-by-step guidance
- **Exam Details:** Test requirements and prep resources
- **Admin Editing:** Update state information as regulations change

### 4. Company Coverage
- **Active States:** Track where RS is licensed
- **Status Management:** Move states between target/in_progress/licensed
- **Geographic View:** Visual map of coverage
- **Expansion Planning:** Identify next target states

---

## 🗂️ Project Structure
```
Licensing-Roadmap/
├── app.py                          # Main Flask application
├── models.py                       # SQLAlchemy ORM models
├── db_write_functions.py           # Database write operations (600+ lines)
├── db_functions_replacement.py     # Database read operations
├── requirements.txt                # Python dependencies
├── start_flask.sh                  # Local development script
├── .env                           # Environment variables (gitignored)
│
├── migrations/                     # Database migrations
│   ├── 001_create_rs_tables.sql   # Main schema creation
│   └── 002_create_rs_bio_data.sql # Bio data table
│
├── static/                         # Static assets
│   ├── css/
│   │   └── main.css               # Main stylesheet
│   └── js/
│       ├── main.js                # Core JavaScript
│       └── mapbox-map.js          # Map functionality
│
├── templates/                      # Jinja2 templates
│   ├── base.html                  # Base template
│   ├── landing.html               # Landing page
│   ├── home.html                  # Dashboard
│   ├── manage_licenses.html       # License list
│   ├── cost_details.html          # Cost tracking
│   ├── cost_analytics.html        # Analytics dashboard
│   ├── director_dashboard.html    # Leadership view
│   └── ... (20+ more templates)
│
├── data/                           # Reference data (JSON)
│   ├── license_holders/           # Legacy JSON files
│   ├── state_details/             # State encyclopedia
│   └── company/                   # Company coverage
│
└── docs/
    ├── README.md                  # This file
    └── DATABASE_SCHEMA.md         # Database documentation
```

---

## 📈 Development Timeline

### Phase 1: Initial Development (2024)
- ✅ JSON-based license tracking
- ✅ Mapbox map integration
- ✅ Cost tracking system
- ✅ State encyclopedia
- ✅ Director dashboard

### Phase 2: Database Migration (January 2026)
- ✅ PostgreSQL schema design
- ✅ SQLAlchemy ORM implementation
- ✅ Data migration from JSON
- ✅ All CRUD operations converted
- ✅ Production deployment

### Phase 3: Current (January 2026)
- ✅ 37 licenses in database
- ✅ Full cost analytics
- ✅ Bio data management
- ✅ Company coverage tracking
- ✅ **100% database integration complete**

### Phase 4: Future Enhancements
- [ ] Training roadmap system
- [ ] Automated renewal reminders
- [ ] Document management
- [ ] Compliance reporting
- [ ] Mobile app

---

## 🔧 Key Technologies

### Backend
- **Flask:** Lightweight Python web framework
- **SQLAlchemy:** Powerful ORM for database operations
- **PostgreSQL:** Enterprise-grade relational database
- **Gunicorn:** Production WSGI server

### Frontend
- **Bootstrap 5:** Responsive UI framework
- **Mapbox GL JS:** Interactive mapping
- **Chart.js:** Data visualization
- **Vanilla JavaScript:** No heavy frameworks

### Deployment
- **Render:** Modern cloud platform
- **Git:** Version control
- **GitHub:** Code repository

---

## 📝 API Documentation

### Database Functions

**Read Operations:**
```python
load_license_holder_data(account)  # Load all data for a license holder
load_company_data()                # Load company coverage data
```

**License Operations:**
```python
add_license_to_db(account, license_data)
update_license_in_db(account, license_id, license_data)
delete_license_from_db(account, license_id)
```

**Cost Operations:**
```python
add_cost_to_db(account, license_id, cost_data)
delete_cost_from_db(account, license_id, cost_index)
update_estimated_costs_in_db(account, license_id, costs)
```

**Team Management:**
```python
create_new_holder(user_id, name, role, pin)
update_holder_metadata(account, updates_dict)
set_next_target_state(account, target_state)
```

**Bio Data:**
```python
add_work_history(account, work_entry)
add_reference(account, reference)
add_job_project(account, job_project)
update_bio_personal_info(account, personal_info)
```

**Company Coverage:**
```python
add_company_coverage_state(state_code, state_name, status)
move_company_coverage_state(state_code, new_status)
remove_company_coverage_state(state_code)
```

---

## 🧪 Testing

### Manual Testing Checklist

**License Management:**
- [ ] Add new license
- [ ] Edit existing license
- [ ] Delete license
- [ ] View license details

**Cost Tracking:**
- [ ] Add cost entry
- [ ] Delete cost entry
- [ ] View cost analytics
- [ ] Export PDF report

**Map Interaction:**
- [ ] Switch between view modes
- [ ] Click states for details
- [ ] Verify data accuracy

**Authentication:**
- [ ] Manager login (100001)
- [ ] License holder login (200002)
- [ ] Logout functionality

---

## 📄 License

Proprietary - Internal use only for Repipe Specialists

---

## 👥 Contributors

**Benjamin Hambrick**
- Primary Developer
- License Manager
- Master of Record (37 licenses)

---

## 📞 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/bhambrick326/Licensing-Roadmap/issues)
- Email: benjamin@repipespecialists.com

---

## 🎯 Roadmap

### Q1 2026
- [x] Complete database migration
- [x] Deploy to production
- [ ] Mobile responsive improvements
- [ ] Automated email reminders

### Q2 2026
- [ ] Training roadmap module
- [ ] Document upload system
- [ ] Advanced analytics dashboard
- [ ] API for Partner Portal integration

### Q3 2026
- [ ] Mobile app (iOS/Android)
- [ ] Automated compliance checks
- [ ] State-by-state requirement updates
- [ ] Integration with accounting system

---

## 🏆 Achievements

- ✅ **100% Database Migration** (January 2026)
- ✅ **37 Licenses Tracked** across 20+ states
- ✅ **Production Ready** and deployed
- ✅ **Zero Downtime** migration
- ✅ **Full CRUD Operations** on PostgreSQL
- ✅ **600+ Lines** of database functions
- ✅ **Cost Analytics** with PDF export

---

## 🙏 Acknowledgments

Built with determination, late nights, and an absolute refusal to give up! 🔥

Special thanks to Claude (Anthropic) for guidance through the epic database migration session.

---

**Last Updated:** January 8, 2026  
**Version:** 2.0.0 (Database-backed)  
**Status:** Production Ready 🚀
