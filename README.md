# 🔧 Licensing Roadmap

A professional multi-user licensing management system designed for plumbing professionals to track licenses, certifications, and compliance across all 50 U.S. states.

![License Management Dashboard](https://img.shields.io/badge/Status-Active%20Development-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)

---

## 🎯 Features

### **Multi-Account System**
- **Individual License Holders** - Personal license tracking and management
- **Director Dashboard** - Aggregated view across all team members
- **Account Switching** - Seamless switching between user profiles

### **Interactive Map Visualizations**
- 🗺️ **License Status View** - Current licensing state across all states
- ⏰ **Expiration Tracker** - Color-coded urgency based on renewal dates
- 👔 **Leadership Dashboard** - Team-wide coverage and compliance metrics
- 🎓 **Training Roadmap** - Step-by-step licensing paths for new hires

### **License Management**
- ✅ View all licenses in a professional table layout
- ✏️ Edit license details (dates, costs, status, board info)
- ➕ Add new licenses for any U.S. state
- 📊 Track renewal costs and expiration dates
- 🔔 Visual urgency indicators (due soon, overdue)

### **Professional UI/UX**
- NetSuite-inspired compact design
- Minimal scrolling, information-dense layouts
- Responsive design (desktop, tablet, mobile)
- Dark blue/copper professional color scheme
- Interactive Mapbox GL maps with smooth transitions

---

## 🚀 Tech Stack

**Backend:**
- Python 3.12
- Flask 3.0
- JSON file-based storage (PostgreSQL ready for production)

**Frontend:**
- Bootstrap 5.3
- Mapbox GL JS
- Custom CSS with professional styling
- Vanilla JavaScript (no heavy frameworks)

**Data Storage:**
- JSON files (development)
- Ready for PostgreSQL migration (production)

---

## 📁 Project Structure
```
Licensing-Roadmap/
├── app.py                          # Flask application
├── data/
│   ├── license_holders/            # Individual user license data
│   │   ├── bhambrick.json          # Benjamin Hambrick's licenses
│   │   └── jsmith.json             # John Smith's licenses
│   ├── training_roadmaps/          # Training paths for new hires
│   │   └── master_plumber_southwest.json
│   ├── company/                    # Company-wide data
│   │   └── coverage.json
│   └── states/                     # State-specific roadmap guides
│       └── tx.md
├── templates/
│   ├── base.html                   # Base template with sidebar
│   ├── licensing_roadmap.html      # Main map view
│   ├── manage_licenses.html        # License table (CRUD)
│   ├── edit_license.html           # Edit license form
│   ├── add_license.html            # Add new license form
│   └── settings.html               # App settings
├── static/
│   ├── css/
│   │   └── main.css                # ~2000 lines of custom styling
│   └── js/
│       ├── main.js                 # Core JavaScript
│       └── mapbox-map.js           # Map visualization logic
└── README.md
```

---

## 🎨 Design Philosophy

### **NetSuite-Inspired Efficiency**
- Compact layouts with minimal vertical scrolling
- Table-based data presentation for dense information
- Professional color palette (Navy blue, Copper accents)
- Information hierarchy through typography and spacing

### **User-Centric Features**
- **Brag Bar** - Quick stats showing total licenses/certificates
- **Context-Aware Sidebars** - Different content based on map view
- **Smart Color Coding** - Instant visual understanding of status
- **Minimal Clicks** - Common tasks accessible in 1-2 clicks

---

## 💾 Data Structure

### License Holder Profile
```json
{
  "user_id": "bhambrick",
  "name": "Benjamin Hambrick",
  "role": "Master Plumber",
  "total_licenses": 29,
  "total_certificates": 42,
  "states": {
    "TX": {
      "name": "Texas",
      "status": "licensed",
      "license_type": "Master Plumber",
      "license_number": "MP-123456",
      "issued_on": "2020-03-15",
      "expires_on": "2026-03-15",
      "renewal_cost": 450,
      "board_name": "Texas State Board of Plumbing Examiners",
      "board_phone": "(512) 555-0100",
      "board_url": "https://www.tsbpe.texas.gov"
    }
  }
}
```

### Training Roadmap
```json
{
  "roadmap_id": "master_plumber_southwest",
  "title": "Master Plumber - Southwest Region",
  "estimated_duration": "18-24 months",
  "total_cost_estimate": "$15,000",
  "path": [
    {
      "step": 1,
      "state": "TX",
      "license_type": "Journey Plumber",
      "priority": "critical",
      "estimated_timeline": "6 months",
      "cost_estimate": "$500"
    }
  ]
}
```

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.12+
- Mapbox Account (free tier works)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Licensing-Roadmap.git
cd Licensing-Roadmap
```

2. **Install dependencies**
```bash
pip install flask
```

3. **Set Mapbox Token**
Edit `app.py` and add your Mapbox token:
```python
MAPBOX_ACCESS_TOKEN = 'your_mapbox_token_here'
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

---

## 🗺️ Map Views Explained

### 1. License Status View (Default)
- **Green** - Licensed and active
- **Blue** - Application in progress
- **Orange** - Renewal due soon (< 90 days)
- **Red** - Overdue renewal
- **Gray** - Not licensed

### 2. Expiration Tracker
- **Dark Green** - 180+ days remaining
- **Lime** - 90-180 days remaining
- **Yellow** - 30-90 days remaining
- **Orange** - 0-30 days remaining
- **Red** - Overdue

### 3. Leadership Dashboard
- Shows aggregate coverage across all license holders
- Identifies coverage gaps
- Tracks team-wide expiration urgency

### 4. Training Roadmap
- Displays recommended licensing sequence
- Color-coded by step priority
- Shows timeline and cost estimates

---

## 📊 Current Capabilities

### ✅ Implemented
- [x] Multi-user account system
- [x] Four interactive map views
- [x] License CRUD operations
- [x] Expiration tracking with urgency
- [x] Training roadmap visualization
- [x] Professional NetSuite-style UI
- [x] Responsive design
- [x] State detail pages

### 🚧 In Development
- [ ] PostgreSQL database migration
- [ ] User authentication system
- [ ] Email/SMS renewal reminders
- [ ] Document upload (license PDFs)
- [ ] Export to CSV/PDF
- [ ] Cost analytics dashboard
- [ ] Calendar integration

---

## 🎓 Training Roadmap Feature

The training roadmap helps new hires understand the optimal path to obtain licenses:

**Example: Master Plumber - Southwest Region**
1. **Texas** - Foundation (6 months, $500)
2. **Arizona** - Market expansion (3 months, $400)
3. **Nevada** - Las Vegas coverage (4 months, $800)
4. **California** - West coast (6 months, $1,200)
5. **Colorado** - Denver market (3 months, $350)

**Total Investment:** 22 months, ~$3,250

---

## 👥 User Personas

### License Holder (Individual)
- View personal licenses
- Update expiration dates and costs
- Track renewal deadlines
- Add new states

### Director (Leadership)
- View all team members' licenses
- Identify coverage gaps
- Monitor team-wide expirations
- Generate compliance reports

### New Hire (Trainee)
- Follow recommended licensing path
- Understand prerequisites and timelines
- Track progress through training roadmap

---

## 🎨 Color Palette
```css
--primary-dark: #1a2634
--primary-blue: #2563eb
--accent-copper: #d97706
--accent-warm: #f59e0b

--status-licensed: #10b981
--status-progress: #3b82f6
--status-due-soon: #f59e0b
--status-overdue: #ef4444
```

---

## 🔐 Security Notes

**Current (Development):**
- No authentication
- JSON file storage
- Local development only

**Production TODO:**
- Implement user authentication (Flask-Login)
- Migrate to PostgreSQL
- Add role-based access control (RBAC)
- Environment variables for secrets
- HTTPS/SSL certificates

---

## 📈 Future Enhancements

### Phase 1 - Production Ready
- PostgreSQL database
- User authentication
- Deployment to Render/Heroku

### Phase 2 - Advanced Features
- Email/SMS notifications
- Document storage (AWS S3)
- Advanced analytics
- Bulk import/export

### Phase 3 - Enterprise
- Multi-tenant support
- API for integrations
- Mobile app (React Native)
- Advanced reporting

---

## 🤝 Contributing

This is currently a private project. Contact the maintainer for collaboration opportunities.

---

## 📄 License

Proprietary - All Rights Reserved

---

## 👨‍💻 Author

**Benjamin Hambrick**
- Master Plumber
- 29 State Licenses
- 42 Professional Certificates

---

## 🙏 Acknowledgments

- **Mapbox** - Interactive mapping platform
- **Bootstrap** - UI framework
- **Flask** - Python web framework
- **Claude (Anthropic)** - Development assistance

---

**Built with 🔧 by licensed professionals, for licensed professionals.**
