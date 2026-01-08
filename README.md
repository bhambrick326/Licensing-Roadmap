# 🔧 Licensing Roadmap - Professional License Management System

A comprehensive web application for tracking professional plumbing licenses across multiple U.S. states, managing costs with financial reporting, and maintaining detailed professional bio information for license applications.

**Built by a licensed plumber for plumbers** - solving real compliance and licensing challenges.

---

## 🎯 Core Features

### **Multi-Account License Tracking**
- Track licenses for multiple team members (Benjamin, John, etc.)
- Team Overview (Director) mode for aggregated view
- Individual license holder views
- Easy account switching with PIN-based authentication
- License goal assignment system (Director assigns next target state)

### **Interactive Map Visualization**
- **4 Map Views:**
  1. **License Status** - Visual overview of all licenses (licensed, in progress, overdue)
  2. **Expiration Tracker** - Color-coded by days until expiration
  3. **Leadership View** - 5-tier market presence analysis:
     - 🟢 Dark Green: Active Markets (licensed + in company coverage)
     - 🔵 Light Blue: Licensed but not active market
     - 🟡 Amber: In Progress
     - 🟣 Purple: Target expansion states
     - ⚪ Gray: Not licensed
  4. **Training Roadmap** - Recommended licensing paths
- Powered by Mapbox GL JS with custom styling
- Click states for detailed information
- Real-time status updates

### **💰 Advanced Cost Tracking & Analytics**
**NEW: Professional financial reporting system for senior leadership**

#### **Cost Tracking Per License**
- **Line-Item Expense Tracking:**
  - Date, category, amount, vendor, notes
  - Delete individual cost entries
  - Native date picker (type or calendar)
  - Auto-calculating totals
  
- **Cost Categories:**
  - Application Fees, Test Fees
  - Trade Books & Business/Law Books
  - License Activation Fees
  - Prep Course Fees
  - Travel & Shipping
  - Renewal Fees, Continuing Education

- **Budget vs Actual:**
  - Estimated costs (planning tool)
  - Actual costs (what was really spent)
  - Variance analysis
  - Budget hidden from license holders (director only)

#### **Cost Analytics Dashboard** 
**Director-level financial reporting:**
- **Executive Summary:**
  - Total Spent (company-wide)
  - Annual Recurring Costs
  - Total Licenses tracked
  
- **Year-by-Year Analysis:**
  - Horizontal scrollable year pills
  - Spending per year with license counts
  - Trends over time
  
- **Expandable License Details:**
  - Click any license to see cost breakdown
  - Individual expenses by category
  - Budget vs. actual per license
  
- **Category Spending Visualization:**
  - Visual breakdown by expense type
  - Percentage of total spend

#### **Dual Export System**
1. **📊 Excel/CSV Export:**
   - Complete data dump
   - All licenses, years, categories
   - Spreadsheet-ready format

2. **📄 Professional PDF Report:**
   - Executive summary with introduction
   - Budget methodology explanation
   - Year-by-year spending tables
   - Category analysis with percentages
   - Detailed license costs (Budget/Actual/Variance)
   - Portrait layout, professional styling
   - Ready for senior leadership review

**Budget Methodology:**
- Budgets based on historical data from actual license acquisition costs
- Serve as planning benchmarks for estimating new license expenses
- Variance analysis shows which licenses cost more/less than expected

### **📋 Active States Management**
**Track company market presence and expansion strategy:**
- **3-Column Layout:**
  - Licensed States (we have coverage)
  - In Progress (applications pending)
  - Target States (future expansion)
- Expandable state cards showing license holders
- Company coverage sync
- Fits on one screen (minimal scrolling)

### **🎯 License Goal Assignment**
**Director assigns next license targets for each team member:**
- Set goal via Team Members → View Licenses → Set Goal
- Goal appears on license holder's dashboard
- Auto-hides when holder achieves license
- Tracks individual development paths
- Stored in holder profile

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
  - Cost tracking per license

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
- Add/edit/delete license holders
- Lock/unlock accounts (preserves data)
- Set "Next Target State" for each team member
- Track total licenses and certificates per holder
- Auto-generated PINs for new accounts
- Quick navigation to individual license views

---

## ��️ Technical Stack

### **Backend**
- **Python 3.12**
- **Flask 3.0** - Web framework
- **JSON-based data storage** - Simple file-based persistence
- **ReportLab** - PDF generation for financial reports

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
- Industrial aesthetic with warm metallics

---

## 📁 Project Structure
```
/workspaces/Licensing-Roadmap/
├── app.py                          # Flask application (~3000 lines)
├── templates/
│   ├── base.html                   # Base layout with sidebar navigation
│   ├── home.html                   # Dashboard with urgent items, stats
│   ├── licensing_roadmap.html      # Interactive map with 4 views
│   ├── manage_licenses.html        # License table with goal setting
│   ├── edit_license.html           # Edit individual license
│   ├── add_license.html            # Add new license form
│   ├── cost_details.html           # Cost tracking per license
│   ├── cost_analytics.html         # Financial analytics dashboard
│   ├── director_dashboard.html     # Team overview with expandable states
│   ├── active_states_manager.html  # 3-column market presence view
│   ├── bio_builder.html            # Professional bio builder (8 sections)
│   ├── manage_team.html            # Team account management
│   ├── edit_holder.html            # Edit license holder info
│   ├── settings.html               # App settings
│   ├── login.html                  # PIN authentication
│   └── landing.html                # Pre-login landing page
├── static/
│   ├── css/
│   │   └── main.css                # 3000+ lines of custom styling
│   └── js/
│       ├── main.js                 # Offcanvas, search, interactions
│       └── mapbox-map.js           # Map initialization, 5-color system
├── data/
│   ├── license_holders/
│   │   ├── bhambrick.json          # Benjamin's licenses, costs & bio
│   │   ├── jsmith.json             # John's licenses, costs & bio
│   │   └── director.json           # Director account data
│   ├── training_roadmaps/
│   │   └── master_plumber_southwest.json
│   ├── company/
│   │   └── coverage.json           # Company market presence
│   ├── bio_templates/
│   │   └── default_bio.json        # Bio structure template
│   └── backups/                    # Automatic backups
└── README.md
```

---

## 💾 Data Structure

### **License Holder Profile with Costs**
```json
{
  "user_id": "bhambrick",
  "name": "Benjamin Hambrick",
  "role": "Master Plumber",
  "total_licenses": 37,
  "total_certificates": 42,
  "next_target_state": "AK",
  "pin": "200002",
  "locked": false,
  
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
        },
        {
          "date": "2020-03-01",
          "category": "travel",
          "amount": 450.00,
          "vendor": "American Airlines",
          "notes": "Flight to Austin for test"
        }
      ],
      
      "cost_totals": {
        "initial_estimated": 351.73,
        "actual_spent": 675.00,
        "variance": -323.27,
        "recurring_cost": 300.00
      },
      
      "recurring": {
        "renewal_fee": 300.00,
        "continuing_ed_fee": 0.00,
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
      "job_projects": [ ... ]
    },
    "education": { ... },
    "references": [ ... ],
    "background": { ... },
    "military": { ... }
  }
}
```

---

## 🚀 Installation & Setup

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
pip install reportlab --break-system-packages
pip install pillow --break-system-packages

# Set environment variables (optional)
export MAPBOX_ACCESS_TOKEN="your_mapbox_token"

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`

### **Default Login**
- **Director PIN:** `100001`
- **Benjamin PIN:** `200002`
- **John PIN:** `200001`

---

## 🎨 Design Philosophy

### **NetSuite-Inspired Efficiency**
- Compact layouts - maximum information, minimal scrolling
- Professional color scheme (copper accents on neutral grays)
- Consistent spacing and typography
- Quick actions always visible
- Reduced padding/margins throughout (25-40% smaller than Bootstrap defaults)
- Single-screen views wherever possible

### **Financial Reporting Standards**
- Executive-ready PDF reports
- Professional introduction and methodology explanations
- Budget vs. actual variance analysis
- Year-over-year trending
- Category-based spending analysis
- Export options for spreadsheet analysis

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
**5-tier market presence analysis:**
- 🟢 **Dark Green:** Active Markets (licensed AND in company coverage)
- 🔵 **Light Blue:** Licensed but not in active market coverage
- �� **Amber:** In Progress (applications pending)
- 🟣 **Purple:** Target expansion states
- ⚪ **Gray:** Not licensed

### **Training Roadmap View**
Recommended licensing paths based on your role and experience level.

---

## 💰 Cost Analytics Workflow

### **For License Holders:**
1. Go to "Manage Licenses"
2. Click "💰 Costs" for any license
3. Add actual expenses (date, category, amount, vendor, notes)
4. View cost summary (actual spent, recurring costs)
5. Budget section hidden (director only)

### **For Directors:**
1. Navigate to "Cost Analytics"
2. View executive summary (Total Spent, Annual Recurring)
3. Scroll through year-by-year spending
4. Click licenses to expand cost details
5. Review category spending breakdown
6. Export PDF report for senior leadership
7. Export Excel for detailed analysis

### **Understanding the Reports:**
- **Budget:** Estimated costs based on historical data (planning tool)
- **Actual:** What was really spent (financial truth)
- **Variance:** Actual - Budget (positive = over budget, negative = under budget)
- **Annual Recurring:** Normalized renewal costs per year

---

## 🔮 Future Enhancements

### **Phase 1: Near-Term**
- [ ] Fix delete cost button (JavaScript syntax issue)
- [ ] Complete cost data entry for all 37 Benjamin licenses
- [ ] Email/SMS renewal notifications
- [ ] Document upload (PDFs, receipts, certificates)
- [ ] Advanced filtering in Cost Analytics

### **Phase 2: Database Migration**
- [ ] Migrate to PostgreSQL
- [ ] Relational data model
- [ ] Better query performance
- [ ] Transaction history

### **Phase 3: Advanced Features**
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Multi-year budget forecasting
- [ ] ROI analysis per state
- [ ] Mobile app (iOS/Android)
- [ ] Reference letter templates

### **Phase 4: SaaS Conversion** (Long-term)
- [ ] Multi-company support
- [ ] Role-based permissions
- [ ] Email-based user accounts
- [ ] Subscription billing
- [ ] API for third-party integrations

---

## 🎯 Use Cases

### **Individual License Holder**
- Track all your licenses in one place
- Add expenses as they occur
- Set renewal reminders
- Build professional bio once, use everywhere
- Filter job history by date for specific applications
- See how much you've spent on licensing

### **Department Manager**
- See team-wide license coverage
- Track costs across all team members
- Assign "next target states" to employees
- Monitor upcoming expirations
- Generate financial reports
- Export data for senior leadership

### **Business Owner / CFO**
- Know licensing costs company-wide
- Budget for expansion into new states
- Year-over-year spending trends
- Category analysis (where is money going?)
- Variance analysis (over/under budget per license)
- Professional PDF reports for board meetings

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

### **Executive Financial Reporting**
**Before:** Spreadsheets, manual tracking, guessing at costs
**After:** One-click PDF reports ready for senior leadership with:
- Professional introduction
- Budget methodology explanation
- Year-over-year analysis
- Category breakdowns
- Variance analysis per license

### **Bio Builder Time Savings**
**Traditional:** Retype name, address, work history, references for every application (15-30 min per app × 20 states = 5-10 hours)

**With Bio Builder:** Fill out comprehensive profile once (1 hour), then copy/paste sections into each application (2-3 min per app × 20 states = 40 min-1 hour)

**Time savings: 4-9 hours** across 20 state applications

---

## 📊 Current Stats (Example Data)
- **37 licenses** tracked across 8 states
- **3 team members** (Director, Benjamin, John)
- **Comprehensive cost tracking** with line-item expenses
- **Year-by-year analysis** with expandable details
- **Professional PDF reports** for executive review
- **8 comprehensive bio sections** covering every application question
- **Job projects library** with date/type filtering

---

## ⚠️ Known Issues

### **Delete Cost Button**
- **Status:** Not working
- **Location:** Cost tracking page (templates/cost_details.html)
- **Issue:** JavaScript `fetch()` syntax error
- **Impact:** Cannot delete individual cost entries
- **Workaround:** Edit JSON files directly or wait for fix
- **Priority:** High - fix planned for next session

---

## 🤝 Contributing

This is currently a private internal tool. Future open-source release TBD.

---

## 📝 License

Proprietary - Internal use only

---

## 👨‍🔧 About

Built by Benjamin Hambrick, Master Plumber (37 active licenses across 8 states), to solve real licensing compliance and financial tracking challenges in the plumbing industry. 

**"Stop filling out the same forms 50 times. Track every licensing dollar. Build it once, use it forever."**

---

## 📞 Support

For questions or issues, contact the development team.

---

**Last Updated:** January 8, 2026
**Version:** 3.0 - Cost Analytics & Financial Reporting Release
