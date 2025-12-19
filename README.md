# 🔧 Licensing Roadmap - Professional License Management System

A comprehensive web application for tracking professional plumbing licenses across multiple U.S. states, managing costs, and maintaining detailed professional bio information for license applications.

**Built by a licensed plumber for plumbers** - solving real compliance and licensing challenges.

---

## 🎯 Core Features

### **Multi-Account License Tracking**
- Track licenses for multiple team members (Benjamin, John, etc.)
- Team Overview (Director) mode for aggregated view
- Individual license holder views
- Easy account switching with persistent context

### **Interactive Map Visualization**
- **4 Map Views:**
  1. **License Status** - Visual overview of all licenses (licensed, in progress, overdue)
  2. **Expiration Tracker** - Color-coded by days until expiration
  3. **Leadership View** - Team-wide coverage map
  4. **Training Roadmap** - Recommended licensing paths
- Powered by Mapbox GL JS with custom styling
- Click states for detailed information
- Real-time status updates

### **Comprehensive License Management**
- Full CRUD operations (Create, Read, Update, Delete)
- Track multiple licenses per jurisdiction (e.g., VA Master Plumber + VA Backflow)
- Support for state, city, county, and certification licenses
- License details:
  - Status tracking (licensed, in progress, not licensed, overdue)
  - License numbers and issue/expiration dates
  - Board contact information
  - Renewal tracking
  - Master of Record / Designated Employee designation
  - Next target state for each license holder

### **💰 Cost Tracking System**
Track every dollar spent on licensing - from initial costs to recurring renewals.

**Cost Categories:**
- Application Fees
- Test Fees  
- Trade Books & Business/Law Books
- License Activation Fees
- Prep Course Fees
- Travel & Shipping
- Renewal Fees
- Continuing Education

**Features:**
- **Estimated vs. Actual Tracking** - Budget planning and variance analysis
- **Line-Item Expense Tracking** - Individual expenses with dates, vendors, notes
- **Cost Analytics Dashboard** - Total spend by state, by category, by license holder
- **Annual Recurring Projections** - Forecast renewal costs
- **CSV Export** - Export data in spreadsheet format

### **📝 Professional Bio Builder**
**The game-changer:** Build your professional profile ONCE, use it for EVERY application.

#### **👤 Personal Information**
- Full legal name (first, middle, last, suffix, other names)
- Date of birth, place of birth, SSN (last 4)
- Physical description (height, weight, eye/hair color)
- Driver's license (number, state, expiration)
- Multiple contact methods (cell, home, work, emails)
- Current address with county, years at address, own/rent
- Previous addresses (5-year history)
- Citizenship status
- Emergency contact

#### **💼 Work History**
Comprehensive employment records with:
- Company information (name, address, phone)
- Position details (title, employment type, dates, duration)
- Supervisor contact info (name, title, phone, email)
- Permission to contact preferences
- Detailed job responsibilities
- Reason for leaving
- Starting/ending wages
- Work type checkboxes (residential, commercial, industrial, service, new construction, remodel)
- Total hours worked
- Copy-to-clipboard formatted output

#### **🔧 Plumbing Experience**
- Total years in trade
- Hour breakdowns (residential, commercial, industrial, service/repair, new construction)
- Systems experience (water supply, DWV, gas, medical gas, backflow, fire sprinkler)
- Experience narrative
- Auto-calculating total hours

**🏗️ Job Projects Library** *(Solves the "Hawaii Problem")*
- Add individual jobs/projects with full details:
  - Project name, location, completion date
  - Job type (residential/commercial/industrial/service)
  - Project value and hours
  - Client/GC contact information
  - Scope of work (summary + detailed description)
  - Systems worked on
  - Your role, permits, crew size
  - Special notes, reference availability
- **Filter by date range** - "Last 4 years" for applications that ask
- **Filter by job type** - Show only residential or commercial
- **Copy filtered list** - Formatted text ready to paste into applications
- Eliminates hours of rewriting the same job descriptions

#### **🎓 Education**
- High school (name, address, city, state, graduation year, diploma/GED)
- Apprenticeship programs (program name, sponsor, dates, hours, instructors, credentials)
- Trade/technical schools (school name, program, dates, credentials)
- College/university (if applicable)

#### **👥 Professional References**
- 3-5 professional references with:
  - Full name, title, company
  - Relationship to you, years known
  - Complete contact info (phone, email, best time to call)
  - Company address
  - Permission to contact (anytime vs. notify first)
  - Reference letter status
  - Personal notes
- Warning when you have fewer than 3 references
- Copy-to-clipboard formatted output

#### **📋 Background & Military**
- Criminal history disclosure and explanations
- Disciplinary action history
- Military service details (branch, dates, rank, discharge type)

**All sections include "Copy to Clipboard" functionality** - format once, paste into any application!

### **👥 Team Management**
- Add/edit license holders
- Set "Next Target State" for each team member
- Track total licenses and certificates per holder
- Quick navigation to individual license views

---

## 🛠️ Technical Stack

### **Backend**
- **Python 3.12**
- **Flask 3.0** - Web framework
- **JSON-based data storage** - Simple file-based persistence (PostgreSQL migration planned)

### **Frontend**
- **Bootstrap 5.3** - Responsive UI framework
- **Mapbox GL JS** - Interactive mapping
- **Vanilla JavaScript** - Dynamic interactions, filtering, copy-to-clipboard
- **NetSuite-inspired design** - Compact, professional, minimal scrolling

### **Styling**
- Custom CSS with copper accent colors (#d97706, #b45309)
- Technical typography (DM Sans, JetBrains Mono)
- Compact form layouts (0.5rem padding, 0.875rem fonts)
- Professional color palette for plumbing industry

---

## 📁 Project Structure
```
/workspaces/Licensing-Roadmap/
├── app.py                          # Flask application with all routes
├── templates/
│   ├── base.html                   # Base layout with sidebar navigation
│   ├── home.html                   # Dashboard with urgent items, stats
│   ├── licensing_roadmap.html      # Interactive map with 4 views
│   ├── manage_licenses.html        # License table with CRUD operations
│   ├── edit_license.html           # Edit individual license
│   ├── add_license.html            # Add new license form
│   ├── cost_details.html           # Cost tracking per license
│   ├── cost_analytics.html         # Cost analytics dashboard
│   ├── bio_builder.html            # Professional bio builder (8 sections)
│   ├── manage_team.html            # Team management
│   ├── edit_holder.html            # Edit license holder info
│   ├── settings.html               # App settings
│   └── login.html                  # Password protection
├── static/
│   ├── css/
│   │   └── main.css                # ~3000+ lines of custom styling
│   └── js/
│       ├── main.js                 # Offcanvas, search, interactions
│       └── mapbox-map.js           # Map initialization, view switching
├── data/
│   ├── license_holders/
│   │   ├── bhambrick.json          # Benjamin's licenses & bio
│   │   └── jsmith.json             # John's licenses & bio
│   ├── training_roadmaps/
│   │   └── master_plumber_southwest.json
│   ├── company/
│   │   └── coverage.json
│   ├── bio_templates/
│   │   └── default_bio.json        # Bio structure template
│   └── backups/                    # Automatic backups of data migrations
└── README.md
```

---

## 💾 Data Structure

### **License Holder Profile**
```json
{
  "user_id": "bhambrick",
  "name": "Benjamin Hambrick",
  "role": "Master Plumber",
  "total_licenses": 29,
  "total_certificates": 42,
  "next_target_state": "AZ",
  "licenses": [
    {
      "license_id": "TX-001",
      "jurisdiction": "Texas",
      "jurisdiction_abbr": "TX",
      "jurisdiction_type": "state",
      "license_type": "Master Plumber",
      "license_number": "MP-123456",
      "status": "licensed",
      "issued_on": "2020-03-15",
      "expires_on": "2026-03-15",
      "designated_role": "master_of_record",
      
      "estimated_costs": {
        "application_fee": 225.00,
        "test_fee": 0.00,
        "trade_book_fee": 126.73,
        "renewal_fee": 300.00
      },
      
      "actual_costs": [
        {
          "date": "2020-02-10",
          "category": "application_fee",
          "amount": 225.00,
          "vendor": "Texas State Board",
          "notes": "Initial application"
        }
      ],
      
      "recurring": {
        "renewal_fee": 300.00,
        "continuing_ed_fee": 100.00,
        "renewal_period_years": 1
      },
      
      "board_name": "Texas State Board of Plumbing Examiners",
      "board_phone": "(512) 555-0100",
      "board_url": "https://www.tsbpe.texas.gov"
    }
  ],
  
  "bio": {
    "personal_info": { ... },
    "work_history": [ ... ],
    "plumbing_experience": {
      "total_years": 12,
      "residential_hours": 8000,
      "commercial_hours": 6000,
      "job_projects": [
        {
          "project_name": "24-unit apartment building",
          "location": "Houston, TX",
          "completion_date": "2023-06-15",
          "job_type": "commercial",
          "project_value": 145000,
          "scope_summary": "Complete rough-in and finish plumbing...",
          "your_role": "Lead Plumber"
        }
      ]
    },
    "education": { ... },
    "references": [ ... ],
    "background": { ... },
    "military": { ... }
  }
}
```

---

## �� Installation & Setup

### **Prerequisites**
- Python 3.12+
- pip package manager
- Git

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd Licensing-Roadmap

# Install dependencies
pip install flask --break-system-packages

# Set environment variables (optional - uses defaults if not set)
export MAPBOX_ACCESS_TOKEN="your_mapbox_token"

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`

### **Default Login**
- **Password:** `TeamLicense2024` (change in `app.py` line ~15)

---

## 🎨 Design Philosophy

### **NetSuite-Inspired Efficiency**
- Compact layouts - maximum information, minimal scrolling
- Professional color scheme (copper accents on neutral grays)
- Consistent spacing and typography
- Quick actions always visible
- Reduced padding/margins throughout (25-40% smaller than Bootstrap defaults)

### **Copy-to-Clipboard First**
Every section of the bio builder includes formatted text outputs that can be copied directly into applications. No more retyping the same information 50 times.

### **Mobile-Responsive**
All pages adapt to tablet and mobile screens (though desktop is optimal for detailed work).

---

## 🗺️ Map Views Explained

### **License Status View**
- **Green** - Licensed and current
- **Blue** - Application in progress  
- **Red** - Overdue for renewal
- **Gray** - Not licensed in this state

### **Expiration Tracker View**
- **Green** - >90 days until expiration
- **Yellow** - 30-90 days (due soon)
- **Orange** - <30 days (urgent)
- **Red** - Overdue
- **Gray** - No license

### **Leadership View** (Director Mode)
Shows aggregated team coverage - tracks who's licensed where across all team members.

### **Training Roadmap View**
Recommended licensing paths based on your role and experience level.

---

## 🔮 Future Enhancements

### **Phase 1: Production Deployment**
- [ ] Migrate to PostgreSQL database
- [ ] Deploy to Render with production configs
- [ ] Email/SMS renewal notifications
- [ ] Document upload (PDFs, receipts, certificates)

### **Phase 2: Advanced Features**
- [ ] CSV import/export for bulk data
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Advanced analytics (cost trends, ROI per state)
- [ ] Mobile app (iOS/Android)
- [ ] Reference letter storage and templates

### **Phase 3: SaaS Conversion** (Long-term)
- [ ] Multi-company support
- [ ] Role-based permissions (admin, manager, license holder)
- [ ] Email-based user accounts
- [ ] Subscription billing
- [ ] API for third-party integrations

---

## 🎯 Use Cases

### **Individual License Holder**
- Track all your licenses in one place
- Set renewal reminders
- Build professional bio once, use everywhere
- Filter job history by date for specific applications
- Track how much you've spent on licensing

### **Department Manager**
- See team-wide license coverage
- Track costs across all team members
- Assign "next target states" to employees
- Monitor upcoming expirations
- Generate compliance reports

### **Business Owner**
- Know who's your Master of Record in each state
- Budget for licensing costs
- Plan expansion based on current coverage
- Track employee certifications

---

## 🏆 Key Innovations

### **The "Hawaii Solution"**
Hawaii requires "List all jobs completed in the last 4 years with detailed descriptions." Before this app, you'd spend hours rewriting job descriptions from memory.

**Now:**
1. Build your job library once (add jobs as you complete them)
2. When Hawaii asks, filter to "Last 4 Years"
3. Click "Copy Filtered Jobs"
4. Paste into application
5. Done in 30 seconds instead of 3 hours

### **Bio Builder vs. Traditional Method**
**Traditional:** Retype name, address, work history, references for every application (15-30 min per app × 20 states = 5-10 hours)

**With Bio Builder:** Fill out comprehensive profile once (1 hour), then copy/paste sections into each application (2-3 min per app × 20 states = 40 min-1 hour)

**Time savings: 4-9 hours** across 20 state applications

---

## 📊 Current Stats (Example Data)
- **8 licenses** tracked (TX, CA, FL, WA, NV, AZ, NY, CO)
- **3 statuses** (licensed, in progress, not licensed)
- **29 total licenses** and **42 certificates** across team
- **$15,000+** in licensing costs tracked
- **8 comprehensive bio sections** covering every application question

---

## 🤝 Contributing

This is currently a private internal tool. Future open-source release TBD.

---

## 📝 License

Proprietary - Internal use only

---

## 👨‍🔧 About

Built by Benjamin Hambrick, Master Plumber, to solve real licensing compliance challenges in the plumbing industry. 

**"Stop filling out the same forms 50 times. Build it once, use it forever."**

---

## 📞 Support

For questions or issues, contact the development team.

---

**Last Updated:** December 2024
**Version:** 2.0 - Bio Builder Release
