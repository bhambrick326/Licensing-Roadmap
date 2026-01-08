"""
Licensing Roadmap Flask Application
A plumber-focused state licensing tracking system
"""

from flask import Flask, render_template, jsonify, abort, request, redirect, session, send_file
import json
import os
from datetime import datetime, timedelta
import markdown

# Simple password authentication
ACCESS_CODE = "TeamLicense2024"  # Change this to your team's password



app = Flask(__name__)


# Custom Jinja filter for currency formatting
@app.template_filter('format_currency')
def format_currency(value):
    """Format number as currency"""
    try:
        return f"${value:,.0f}"
    except:
        return "$0"


# ==================== USER CONFIGURATION ====================
# Simple user database with PINs
USERS = {
    '100001': {
        'pin': '100001',
        'user_type': 'manager',
        'name': 'Benjamin Hambrick',
        'email': 'ben@example.com',
        'user_id': 'director'
    },
    '200001': {
        'pin': '200001',
        'user_type': 'license_holder',
        'name': 'John Smith',
        'email': 'john@example.com',
        'user_id': 'jsmith'
    },
    '200002': {
        'pin': '200002',
        'user_type': 'license_holder',
        'name': 'Benjamin Hambrick',
        'email': 'ben.personal@example.com',
        'user_id': 'bhambrick'
    }
}


# ==================== HELPER FUNCTIONS ====================
def get_allowed_account():
    """Get the account the current user is allowed to view"""
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    
    # Managers always see director view (no account switching)
    if user_type == 'manager':
        return 'director'
    
    # License holders can ONLY see their own account
    else:
        return user_id

@app.route('/login', methods=['GET', 'POST'])
def login():
    """PIN-based login page"""
    # If already logged in, redirect to home
    if session.get('logged_in'):
        return redirect('/')
    
    if request.method == 'POST':
        pin = request.form.get('pin', '').strip()
        
        # Check if PIN exists in USERS
        if pin in USERS:
            user = USERS[pin]
            
            # For license holders, check if account is locked
            if user['user_type'] == 'license_holder':
                holder = load_license_holder_data(user['user_id'])
                if holder and holder.get('account_status') == 'locked':
                    return render_template('login.html', error='Account locked. Contact your manager.')
            
            session['logged_in'] = True
            session['pin'] = pin
            session['user_type'] = user['user_type']
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid PIN')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect('/landing')



@app.before_request
def require_login():
    """Require login for all routes except /login and landing page"""
    # Public routes
    public_routes = ['login', 'static', 'landing_page']
    
    # If not logged in and trying to access protected route
    if request.endpoint not in public_routes and not session.get('logged_in'):
        # Show landing page for root, redirect to login for other protected routes
        if request.path == '/':
            return redirect('/landing')
        else:
            return redirect('/login')


@app.context_processor
def inject_current_account():
    """Make current account available to all templates"""
    import os
    
    # Get account from session or URL parameter
    account = get_allowed_account()
    
    # Load current user for navigation
    if account == 'director':
        current_holder = {
            'user_id': 'director',
            'name': 'Team Overview',
            'role': 'Leadership View'
        }
        
        # Calculate team stats for brag bar
        team_total_licenses = 0
        team_total_states = set()
        team_total_holders = 0
        
        holders_dir = 'data/license_holders'
        if os.path.exists(holders_dir):
            for filename in os.listdir(holders_dir):
                if filename.endswith('.json') and filename != 'director.json':
                    filepath = os.path.join(holders_dir, filename)
                    with open(filepath, 'r') as f:
                        holder = json.load(f)
                        team_total_licenses += len(holder.get('licenses', []))
                        for lic in holder.get('licenses', []):
                            if lic.get('jurisdiction_abbr'):
                                team_total_states.add(lic['jurisdiction_abbr'])
                        team_total_holders += 1
        
        return dict(
            current_account=account, 
            holder=current_holder,
            team_total_licenses=team_total_licenses,
            team_total_states=len(team_total_states),
            team_total_holders=team_total_holders
        )
    else:
        current_holder = load_license_holder_data(account)
        if not current_holder:
            current_holder = {'user_id': 'bhambrick', 'name': 'User', 'role': 'License Holder', 'licenses': []}
    
    return dict(current_account=account, holder=current_holder)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
DUE_SOON_DAYS = 90  # Days before expiration to show "due soon"
DATA_DIR = os.path.join(app.root_path, 'data')
STATES_DIR = os.path.join(DATA_DIR, 'states')


def load_licensing_data():
    """Load the main licensing roadmap data from JSON"""
    json_path = os.path.join(DATA_DIR, 'licensing_roadmap.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"states": {}}


def load_license_holder_data(user_id='bhambrick'):
    """Load data for a specific license holder"""
    json_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_company_data():
    """Load company-wide coverage data"""
    json_path = os.path.join('data', 'company', 'coverage.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_training_roadmap(roadmap_id='master_plumber_southwest'):
    """Load a training roadmap"""
    json_path = os.path.join('data', 'training_roadmaps', f'{roadmap_id}.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None



def get_license_by_id(holder_data, license_id):
    """Get a specific license by ID"""
    for license in holder_data.get('licenses', []):
        if license['license_id'] == license_id:
            return license
    return None

def calculate_license_totals(license):
    """Calculate total costs for a license"""
    # Initial cost = sum of all estimated one-time costs
    estimated = license.get('estimated_costs', {})
    initial_cost = sum(v for v in estimated.values() if v is not None)
    
    # Actual cost = sum of all actual cost line items
    actual_costs = license.get('actual_costs', [])
    actual_total = sum(item.get('amount', 0) or 0 for item in actual_costs)
    
    # Recurring cost = renewal + CE per period (handle None values)
    recurring = license.get('recurring', {})
    renewal_fee = recurring.get('renewal_fee') or 0
    ce_fee = recurring.get('continuing_ed_fee') or 0
    recurring_cost = renewal_fee + ce_fee
    
    return {
        'initial_estimated': initial_cost,
        'actual_spent': actual_total,
        'recurring_cost': recurring_cost,
        'variance': initial_cost - actual_total
    }

def enhance_license_data(license):
    """Add calculated fields to license data"""
    enhanced = license.copy()
    
    # Calculate status class based on expiration
    enhanced['status_class'] = get_state_status_class(license)
    enhanced['badge_text'] = get_state_badge_text(license)
    enhanced['days_remaining'] = calculate_days_remaining(license.get('expires_on'))
    
    # Calculate cost totals
    totals = calculate_license_totals(license)
    enhanced['cost_totals'] = totals
    
    return enhanced


def calculate_days_remaining(expires_on):
    """Calculate days remaining until expiration"""
    if not expires_on:
        return None
    
    try:
        exp_date = datetime.fromisoformat(expires_on)
        today = datetime.now()
        delta = exp_date - today
        return delta.days
    except (ValueError, TypeError):
        return None


def get_state_status_class(state_data):
    """Determine CSS class for state based on status and expiration"""
    status = state_data.get('status', 'not_licensed')
    expires_on = state_data.get('expires_on')
    
    if status == 'licensed' and expires_on:
        days_remaining = calculate_days_remaining(expires_on)
        if days_remaining is not None:
            if days_remaining < 0:
                return 'overdue'
            elif days_remaining <= DUE_SOON_DAYS:
                return 'due-soon'
    
    return status


def get_state_badge_text(state_data):
    """Get human-readable badge text for state status"""
    status = state_data.get('status', 'not_licensed')
    expires_on = state_data.get('expires_on')
    
    if status == 'licensed' and expires_on:
        days_remaining = calculate_days_remaining(expires_on)
        if days_remaining is not None:
            if days_remaining < 0:
                return 'Overdue'
            elif days_remaining <= DUE_SOON_DAYS:
                return 'Renewal Due Soon'
    
    status_map = {
        'licensed': 'Licensed ✅',
        'in_progress': 'In Progress',
        'not_licensed': 'Not Licensed'
    }
    
    return status_map.get(status, 'Not Licensed')


def load_state_detail(state_abbr):
    """Load state detail content from markdown file"""
    md_path = os.path.join(STATES_DIR, f'{state_abbr.lower()}.md')
    
    try:
        with open(md_path, 'r') as f:
            content = f.read()
            html_content = markdown.markdown(content, extensions=['extra', 'nl2br'])
            return html_content
    except FileNotFoundError:
        return None



@app.route('/')
@app.route('/landing')
def landing_page():
    """Landing page for non-logged-in users"""
    # If already logged in, go to home
    if session.get('logged_in'):
        # Preserve current account or default to bhambrick
        account = request.args.get('account') or session.get('account', 'bhambrick')
        return redirect(f'/home?account={account}')
    
    return render_template('landing.html')

@app.route('/home')
def home():
    """Home dashboard"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    
    # Handle director view
    if account == 'director':
        import glob
        all_licenses = []
        all_holders = []
        
        holder_files = glob.glob('data/license_holders/*.json')
        for holder_file in holder_files:
            with open(holder_file, 'r') as f:
                holder = json.load(f)
                all_holders.append(holder)
                
                for license in holder.get('licenses', []):
                    enhanced = enhance_license_data(license)
                    enhanced['holder_name'] = holder['name']
                    all_licenses.append(enhanced)
        
        # Load company coverage data
        import os
        coverage = {}
        coverage_file = 'data/company/coverage.json'
        if os.path.exists(coverage_file):
            with open(coverage_file, 'r') as f:
                coverage = json.load(f)
        
        # Calculate stats for all license holders
        total_licenses = sum(h.get('total_licenses', 0) for h in all_holders)
        expiring_soon = 0
        annual_cost = 0
        active_states_detail = {}
        
        # Build detailed state info
        for license in all_licenses:
            abbr = license.get('jurisdiction_abbr')
            if abbr:
                if abbr not in active_states_detail:
                    active_states_detail[abbr] = {'holders': []}
                
                # Store holder info (name + user_id) to make links work
                holder_name = license.get('holder_name')
                holder_user_id = next((h.get('user_id') for h in all_holders if h.get('name') == holder_name), None)
                
                holder_info = {
                    'name': holder_name,
                    'user_id': holder_user_id
                }
                
                # Only add if not already in list
                if not any(h['name'] == holder_name for h in active_states_detail[abbr]['holders']):
                    active_states_detail[abbr]['holders'].append(holder_info)
            
            # Count expiring
            days = license.get('days_remaining')
            if days and days <= 60:
                expiring_soon += 1
            
            # Sum costs
            annual_cost += license.get('cost_totals', {}).get('recurring_cost', 0) / 2  # Assuming 2-year periods
        
        # Prepare team member cards with stats
        team_members = []
        for holder in all_holders:
            holder_licenses = holder.get('licenses', [])
            states_count = len(set(lic.get('jurisdiction_abbr') for lic in holder_licenses if lic.get('jurisdiction_abbr')))
            expiring_count = sum(1 for lic in holder_licenses 
                               if lic.get('expires_on') and calculate_days_remaining(lic.get('expires_on')) 
                               and calculate_days_remaining(lic.get('expires_on')) <= 60)
            
            team_members.append({
                'user_id': holder.get('user_id'),
                'name': holder.get('name'),
                'role': holder.get('role', 'License Holder'),
                'total_licenses': holder.get('total_licenses', 0),
                'states_count': states_count,
                'expiring_count': expiring_count
            })
        
        # Build urgent items with holder names
        urgent_items = []
        for license in all_licenses:
            days_remaining = license.get('days_remaining')
            if license.get('status') == 'overdue':
                urgent_items.append({
                    'holder_name': license.get('holder_name'),
                    'jurisdiction': license.get('jurisdiction'),
                    'issue': 'OVERDUE',
                    'urgency': 'danger',
                    'action': 'Renew Now',
                    'link': '#'
                })
            elif days_remaining and days_remaining <= 30:
                urgent_items.append({
                    'holder_name': license.get('holder_name'),
                    'jurisdiction': license.get('jurisdiction'),
                    'issue': f'Expires in {days_remaining} days',
                    'urgency': 'warning',
                    'action': 'Review',
                    'link': '#'
                })
        
        stats = {
            'total_licenses': total_licenses,
            'active_states': len(coverage.get('covered_states', [])),
            'expiring_soon': expiring_soon,
            'annual_cost': annual_cost
        }
        
        return render_template('director_dashboard.html',
                             stats=stats,
                             coverage=coverage,
                             active_states_detail=active_states_detail,
                             team_members=team_members,
                             urgent_items=urgent_items[:10])
    else:
        # Individual holder
        holder_data = load_license_holder_data(account)
        
        if not holder_data:
            return render_template('home.html', 
                                 holder={'name': 'User', 'role': 'License Holder'},
                                 stats={'licensed': 0, 'in_progress': 0, 'not_licensed': 0, 'total': 0}, 
                                 urgent_items=[], 
                                 recent_licenses=[],
                                 cost_summary={'total_estimated': 0, 'total_spent': 0, 'annual_recurring': 0})
        
        enhanced_licenses = []
        for license in holder_data.get('licenses', []):
            enhanced = enhance_license_data(license)
            enhanced_licenses.append(enhanced)
    
    enhanced_licenses = []
    total_estimated = 0
    total_actual = 0
    annual_recurring = 0
    urgent_items = []
    
    for license in holder_data.get('licenses', []):
        enhanced = enhance_license_data(license)
        enhanced_licenses.append(enhanced)
        
        total_estimated += enhanced['cost_totals']['initial_estimated']
        total_actual += enhanced['cost_totals']['actual_spent']
        
        period_years = enhanced.get('recurring', {}).get('renewal_period_years', 2)
        recurring_per_period = enhanced['cost_totals']['recurring_cost']
        annual_recurring += recurring_per_period / period_years if period_years > 0 else 0
        
        days_remaining = enhanced.get('days_remaining')
        
        if enhanced['status'] == 'overdue':
            urgent_items.append({
                'jurisdiction': enhanced['jurisdiction'],
                'issue': 'OVERDUE',
                'urgency': 'danger',
                'action': 'Renew immediately',
                'link': f"/settings/edit-license/{enhanced['license_id']}"
            })
        elif days_remaining is not None and days_remaining <= 30 and days_remaining > 0:
            urgent_items.append({
                'jurisdiction': enhanced['jurisdiction'],
                'issue': f'Expires in {days_remaining} days',
                'urgency': 'warning',
                'action': 'Plan renewal',
                'link': f"/settings/edit-license/{enhanced['license_id']}"
            })
        elif enhanced['status'] == 'in_progress':
            urgent_items.append({
                'jurisdiction': enhanced['jurisdiction'],
                'issue': 'Application Pending',
                'urgency': 'info',
                'action': 'Check status',
                'link': f"/settings/edit-license/{enhanced['license_id']}"
            })
    
    enhanced_licenses.sort(key=lambda x: x.get('expires_on') or '9999-12-31')
    
    stats = {
        'licensed': sum(1 for lic in enhanced_licenses if lic['status'] == 'licensed'),
        'in_progress': sum(1 for lic in enhanced_licenses if lic['status'] == 'in_progress'),
        'not_licensed': sum(1 for lic in enhanced_licenses if lic['status'] == 'not_licensed'),
        'total': len(enhanced_licenses)
    }
    
    cost_summary = {
        'total_estimated': total_estimated,
        'total_spent': total_actual,
        'annual_recurring': annual_recurring
    }
    
    return render_template('home.html',
                         holder=holder_data,
                         stats=stats,
                         urgent_items=urgent_items[:5],
                         recent_licenses=enhanced_licenses,
                         cost_summary=cost_summary)



@app.route('/licensing-roadmap')
def licensing_roadmap():
    """Main licensing roadmap with multi-account support"""
    # Get account from query parameter (default: bhambrick)
    # Get account from session or URL parameter
    account = get_allowed_account()
    
    # Handle director view differently
    if account == 'director':
        return render_director_view()
    
    # Load license holder data
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    states = holder_data.get("states", {})
    
    # Start with all 50 states (base data)
    import os
    base_states_path = 'data/base_data/all_states.json'
    if os.path.exists(base_states_path):
        with open(base_states_path, 'r') as f:
            enhanced_states = json.load(f)
            # Add default fields to each state
            for abbr, state_data in enhanced_states.items():
                state_data['state_abbr'] = abbr
                state_data['status_class'] = 'not_licensed'
                state_data['badge_text'] = 'Not Licensed'
                state_data['days_remaining'] = None
                state_data['board_name'] = f'{state_data["name"]} State Board'
                state_data['board_url'] = '#'
                state_data['summary'] = f'No license data available for {state_data["name"]} yet.'
    else:
        enhanced_states = {}
    
    # Overlay actual license data
    for license in holder_data.get('licenses', []):
        abbr = license.get('jurisdiction_abbr')
        if abbr and abbr in enhanced_states:
            # Overlay license data on top of base state
            enhanced_states[abbr].update({
                "status": license.get("status"),
                "status_class": get_state_status_class(license),
                "badge_text": get_state_badge_text(license),
                "days_remaining": calculate_days_remaining(license.get("expires_on")),
                "license_type": license.get("license_type"),
                "license_number": license.get("license_number"),
                "issued_on": license.get("issued_on"),
                "expires_on": license.get("expires_on"),
                "board_name": license.get("board_name", f'{enhanced_states[abbr]["name"]} State Board'),
                "board_phone": license.get("board_phone"),
                "board_url": license.get("board_url", "#"),
                "summary": f'Licensed as {license.get("license_type", "Plumber")}'
            })
    
    # Calculate stats
    licenses = holder_data.get('licenses', [])
    stats = {
        "licensed": sum(1 for lic in licenses if lic.get("status") == "licensed"),
        "in_progress": sum(1 for lic in licenses if lic.get("status") == "in_progress"),
        "not_licensed": sum(1 for lic in licenses if lic.get("status") == "not_licensed"),
        "due_soon": sum(1 for s in enhanced_states.values() if s.get("status_class") == "due-soon"),
        "overdue": sum(1 for s in enhanced_states.values() if s.get("status_class") == "overdue"),
        "total": len(licenses)
    }
    
    # Convert to JSON
    states_json = json.dumps(enhanced_states)
    
    # Load training roadmap
    training_roadmap = load_training_roadmap('master_plumber_southwest')
    training_roadmap_json = json.dumps(training_roadmap) if training_roadmap else '{}'
    
    return render_template("licensing_roadmap.html",
                         states=enhanced_states,
                         states_json=states_json,
                         stats=stats,
                         holder=holder_data,
                         training_roadmap=training_roadmap_json,
                         coverage_json=json.dumps({}))
def render_director_view():
    """Render the director/leadership aggregated view with company coverage"""
    import glob
    import os
    
    coverage = {}
    coverage_file = 'data/company/coverage.json'
    if os.path.exists(coverage_file):
        with open(coverage_file, 'r') as f:
            coverage = json.load(f)
    
    # Load all license holders
    all_states = {}
    all_holders = []
    
    holder_files = glob.glob('data/license_holders/*.json')
    
    for holder_file in holder_files:
        with open(holder_file, 'r') as f:
            holder = json.load(f)
            all_holders.append(holder)
            
            # Process each license
            for license in holder.get('licenses', []):
                abbr = license.get('jurisdiction_abbr')
                if not abbr:
                    continue
                    
                if abbr not in all_states:
                    # Initialize with first holder's data
                    all_states[abbr] = {
                        'name': license['jurisdiction'],
                        'status': license['status'],
                        'holders': [],
                        'holder_details': [],
                        'board_name': license.get('board_name'),
                        'board_url': license.get('board_url'),
                        'expires_on': license.get('expires_on'),
                        'company_status': 'not_active',  # Will be updated from coverage
                        'revenue': 0,
                        'license_type': license.get('license_type'),
                        'state_abbr': abbr
                    }
                else:
                    # Upgrade status if better coverage exists
                    if license['status'] == 'licensed' and all_states[abbr]['status'] != 'licensed':
                        all_states[abbr]['status'] = 'licensed'
                    elif license['status'] == 'in_progress' and all_states[abbr]['status'] == 'not_licensed':
                        all_states[abbr]['status'] = 'in_progress'
                    
                    # Track earliest expiration date
                    if license.get('expires_on'):
                        if not all_states[abbr].get('expires_on'):
                            all_states[abbr]['expires_on'] = license['expires_on']
                        else:
                            # Keep the earliest expiration
                            if license['expires_on'] < all_states[abbr]['expires_on']:
                                all_states[abbr]['expires_on'] = license['expires_on']
                
                all_states[abbr]['holders'].append(holder['name'])
    

    # Overlay company coverage status
    for abbr in all_states:
        if abbr in coverage.get('covered_states', []):
            all_states[abbr]['company_status'] = 'licensed'
            all_states[abbr]['status_class'] = 'company-licensed'
        elif abbr in coverage.get('in_progress_states', []):
            all_states[abbr]['company_status'] = 'in_progress'
            all_states[abbr]['status_class'] = 'company-in-progress'
        elif abbr in coverage.get('target_states', []):
            all_states[abbr]['company_status'] = 'target'
            all_states[abbr]['status_class'] = 'company-target'
        
        # Add revenue if available
        if abbr in coverage.get('state_revenues', {}):
            all_states[abbr]['revenue'] = coverage['state_revenues'][abbr]
    
    # Add base state data for states not yet licensed
    base_states_file = 'data/base_data/all_states.json'
    if os.path.exists(base_states_file):
        with open(base_states_file, 'r') as f:
            base_states = json.load(f)
            for abbr, state_data in base_states.items():
                if abbr not in all_states:
                    all_states[abbr] = {
                        'name': state_data['name'],
                        'state_abbr': abbr,
                        'status': 'not_licensed',
                        'status_class': 'not-licensed',
                        'company_status': 'not_active',
                        'holders': [],
                        'holder_details': [],
                        'summary': 'Not licensed'
                    }
                    # Check if it's in coverage
                    if abbr in coverage.get('covered_states', []):
                        all_states[abbr]['company_status'] = 'licensed'
                        all_states[abbr]['status_class'] = 'company-licensed'
                    elif abbr in coverage.get('in_progress_states', []):
                        all_states[abbr]['company_status'] = 'in_progress'
                        all_states[abbr]['status_class'] = 'company-in-progress'
                    elif abbr in coverage.get('target_states', []):
                        all_states[abbr]['company_status'] = 'target'
                        all_states[abbr]['status_class'] = 'company-target'

    # Enhance state data for director view
    enhanced_states = {}
    total_due_soon = 0
    total_overdue = 0
    
    for abbr, state_data in all_states.items():
        enhanced = state_data.copy()
        enhanced['status_class'] = get_state_status_class(state_data)
        enhanced['badge_text'] = get_state_badge_text(state_data)
        enhanced['days_remaining'] = calculate_days_remaining(state_data.get('expires_on'))
        
        # Count urgency
        if enhanced['status_class'] == 'due-soon':
            total_due_soon += 1
        elif enhanced['status_class'] == 'overdue':
            total_overdue += 1
        
        enhanced_states[abbr] = enhanced
    
    stats = {
        'licensed': len([s for s in all_states.values() if s['status'] == 'licensed']),
        'in_progress': len([s for s in all_states.values() if s['status'] == 'in_progress']),
        'not_licensed': len([s for s in all_states.values() if s['status'] == 'not_licensed']),
        'due_soon': total_due_soon,
        'overdue': total_overdue,
        'total': len(all_states)
    }
    
    # Director data object
    director_data = {
        'user_id': 'director',
        'name': 'Director View',
        'role': 'Department Leadership',
        'total_licenses': sum(h.get('total_licenses', 0) for h in all_holders),
        'total_certificates': sum(h.get('total_certificates', 0) for h in all_holders),
        'total_holders': len(all_holders)
    }
    
    states_json = json.dumps(enhanced_states)
    
    # Load training roadmap
    training_roadmap = load_training_roadmap('master_plumber_southwest')
    training_roadmap_json = json.dumps(training_roadmap) if training_roadmap else '{}'
    
    return render_template("licensing_roadmap.html",
                         states=enhanced_states,
                         states_json=states_json,
                         stats=stats,
                         holder=director_data,
                         training_roadmap=training_roadmap_json,
                         team_members=all_holders,
                         team_members_json=json.dumps([{'user_id': h.get('user_id'), 'name': h.get('name')} for h in all_holders]),
                         coverage_json=json.dumps(coverage))


@app.route('/api/states')
def api_states():
    """API endpoint for state data (for AJAX/JS usage)"""
    data = load_licensing_data()
    states = data.get('states', {})
    
    # Enhance state data
    enhanced_states = {}
    for abbr, state_data in states.items():
        enhanced = state_data.copy()
        enhanced['status_class'] = get_state_status_class(state_data)
        enhanced['badge_text'] = get_state_badge_text(state_data)
        enhanced['days_remaining'] = calculate_days_remaining(state_data.get('expires_on'))
        enhanced_states[abbr] = enhanced
    
    return jsonify(enhanced_states)


@app.route('/admin/licensing/states')
def admin_states_list():
    """Simple admin view to track state content freshness"""
    data = load_licensing_data()
    states = data.get('states', {})
    
    # Sort by last_reviewed date
    states_list = []
    for abbr, state_data in states.items():
        item = {
            'abbr': abbr,
            'name': state_data.get('name', abbr),
            'last_reviewed': state_data.get('last_reviewed'),
            'coverage_level': state_data.get('coverage_level', 'draft'),
            'status': state_data.get('status')
        }
        states_list.append(item)
    
    # Sort by last_reviewed (oldest first)
    states_list.sort(key=lambda x: x.get('last_reviewed') or '1900-01-01')
    
    return render_template('admin_states.html', states=states_list)



@app.route('/api/leadership-data')
def leadership_data():
    """API endpoint for leadership dashboard data"""
    # Load all license holders
    import glob
    
    all_holders = []
    state_coverage = {}
    expiring_soon = []
    
    holder_files = glob.glob('data/license_holders/*.json')
    
    for holder_file in holder_files:
        with open(holder_file, 'r') as f:
            holder = json.load(f)
            all_holders.append(holder)
            
            # Track coverage by state
            for state_abbr, state_data in holder.get('states', {}).items():
                if state_abbr not in state_coverage:
                    state_coverage[state_abbr] = {
                        'name': state_data['name'],
                        'licensed_count': 0,
                        'in_progress_count': 0,
                        'holders': []
                    }
                
                if state_data['status'] == 'licensed':
                    state_coverage[state_abbr]['licensed_count'] += 1
                elif state_data['status'] == 'in_progress':
                    state_coverage[state_abbr]['in_progress_count'] += 1
                
                state_coverage[state_abbr]['holders'].append(holder['name'])
                
                # Track expiring licenses
                if state_data.get('expires_on'):
                    days_remaining = calculate_days_remaining(state_data['expires_on'])
                    if days_remaining is not None and days_remaining <= 90:
                        expiring_soon.append({
                            'holder': holder['name'],
                            'state': state_data['name'],
                            'state_abbr': state_abbr,
                            'days_remaining': days_remaining,
                            'expires_on': state_data['expires_on']
                        })
    
    # Calculate aggregate stats
    total_licensed = sum(1 for s in state_coverage.values() if s['licensed_count'] > 0)
    total_in_progress = sum(1 for s in state_coverage.values() if s['in_progress_count'] > 0)
    total_licenses = sum(h.get('total_licenses', 0) for h in all_holders)
    total_certificates = sum(h.get('total_certificates', 0) for h in all_holders)
    
    # High-priority states (major markets we should target)
    high_priority_states = ['TX', 'CA', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    coverage_gaps = [s for s in high_priority_states if s not in state_coverage or state_coverage[s]['licensed_count'] == 0]
    
    return jsonify({
        'total_holders': len(all_holders),
        'total_licenses': total_licenses,
        'total_certificates': total_certificates,
        'states_covered': total_licensed,
        'states_in_progress': total_in_progress,
        'state_coverage': state_coverage,
        'expiring_soon': sorted(expiring_soon, key=lambda x: x['days_remaining']),
        'coverage_gaps': coverage_gaps
    })




@app.route('/settings')
def settings():
    """Application settings page"""
    return render_template('settings.html')

@app.route('/manage-licenses')
def manage_licenses():
    """License management page"""
    # Check if manager is viewing a specific holder
    requested_account = request.args.get('account')
    is_manager = session.get('user_type') == 'manager'
    
    # If manager requests a specific holder, show that holder's licenses
    if is_manager and requested_account and requested_account != 'director':
        holder_data = load_license_holder_data(requested_account)
        if not holder_data:
            return "License holder not found", 404
        
        enhanced_licenses = []
        for license in holder_data.get('licenses', []):
            enhanced_licenses.append(enhance_license_data(license))
        
        return render_template('manage_licenses.html', 
                             holder=holder_data,
                             licenses=enhanced_licenses,
                             is_director=True)
    
    # Get account from session or URL parameter
    account = get_allowed_account()
    
    # Handle director view - show all licenses
    if account == 'director':
        import glob
        all_licenses = []
        all_holders = []
        
        holder_files = glob.glob('data/license_holders/*.json')
        for holder_file in holder_files:
            with open(holder_file, 'r') as f:
                holder = json.load(f)
                all_holders.append(holder)
                
                for license in holder.get('licenses', []):
                    enhanced = enhance_license_data(license)
                    enhanced['holder_name'] = holder['name']
                    all_licenses.append(enhanced)
        
        director_data = {
            'user_id': 'director',
            'name': 'Director View',
            'role': 'Department Leadership',
            'total_licenses': sum(h.get('total_licenses', 0) for h in all_holders),
            'total_certificates': sum(h.get('total_certificates', 0) for h in all_holders)
        }
        
        return render_template('manage_licenses.html', 
                             holder=director_data,
                             licenses=all_licenses,
                             is_director=True)
    
    # Individual license holder
    holder_data = load_license_holder_data(account)
    if not holder_data:
        return "License holder not found", 404
    
    enhanced_licenses = []
    for license in holder_data.get('licenses', []):
        enhanced_licenses.append(enhance_license_data(license))
    
    return render_template('manage_licenses.html', 
                         holder=holder_data,
                         licenses=enhanced_licenses,
                         is_director=False)

@app.route('/api/save-license', methods=['POST'])
def save_license():
    """Save/update a license"""
    data = request.get_json()
    account = data.get('account', 'bhambrick')
    state_abbr = data.get('state_abbr')
    license_data = data.get('license_data')
    
    if not state_abbr or not license_data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Load current holder data
    holder_data = load_license_holder_data(account)
    if not holder_data:
        return jsonify({'error': 'License holder not found'}), 404
    
    # Update the state data
    if 'states' not in holder_data:
        holder_data['states'] = {}
    
    holder_data['states'][state_abbr] = license_data
    
    # Save back to file
    import os
    json_path = os.path.join('data', 'license_holders', f'{account}.json')
    with open(json_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return jsonify({'success': True, 'message': 'License saved successfully'})

@app.route('/api/delete-license', methods=['POST'])
def delete_license():
    """Delete a license"""
    data = request.get_json()
    account = data.get('account', 'bhambrick')
    state_abbr = data.get('state_abbr')
    
    if not state_abbr:
        return jsonify({'error': 'Missing state abbreviation'}), 400
    
    # Load current holder data
    holder_data = load_license_holder_data(account)
    if not holder_data:
        return jsonify({'error': 'License holder not found'}), 404
    
    # Delete the state
    if 'states' in holder_data and state_abbr in holder_data['states']:
        del holder_data['states'][state_abbr]
        
        # Save back to file
        import os
        json_path = os.path.join('data', 'license_holders', f'{account}.json')
        with open(json_path, 'w') as f:
            json.dump(holder_data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'License deleted successfully'})
    
    return jsonify({'error': 'License not found'}), 404



    return redirect(f'/manage-licenses?account={account}')



@app.route('/settings/edit-license/<license_id>')
def edit_license(license_id):
    """Edit license form"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    license_data = get_license_by_id(holder_data, license_id)
    if not license_data:
        return "License not found", 404
    
    # Enhance with calculated data
    enhanced_license = enhance_license_data(license_data)
    
    return render_template('edit_license.html',
                         license=enhanced_license,
                         holder=holder_data)

@app.route('/settings/update-license/<license_id>', methods=['POST'])
def update_license(license_id):
    """Update license data"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Find the license
    license_data = None
    for lic in holder_data.get('licenses', []):
        if lic['license_id'] == license_id:
            license_data = lic
            break
    
    if not license_data:
        return "License not found", 404
    
    # Update basic fields
    license_data.update({
        'status': request.form.get('status'),
        'license_type': request.form.get('license_type'),
        'license_number': request.form.get('license_number'),
        'issued_on': request.form.get('issued_on'),
        'expires_on': request.form.get('expires_on'),
        'application_date': request.form.get('application_date'),
        'board_name': request.form.get('board_name'),
        'board_phone': request.form.get('board_phone'),
        'board_url': request.form.get('board_url'),
        'notes': request.form.get('notes')
    })
    
    # Update recurring costs
    if 'renewal_fee' in request.form:
        license_data['recurring']['renewal_fee'] = float(request.form.get('renewal_fee') or 0)
    if 'continuing_ed_fee' in request.form:
        license_data['recurring']['continuing_ed_fee'] = float(request.form.get('continuing_ed_fee') or 0)
    if 'renewal_period_years' in request.form:
        license_data['recurring']['renewal_period_years'] = int(request.form.get('renewal_period_years') or 2)
    
    # Save to file
    import os
    file_path = os.path.join('data', 'license_holders', f'{account}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/manage-licenses?account={account}')



@app.route('/settings/add-license')
def add_license_form():
    """Show add license form"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    prefill_state = request.args.get('prefill')  # Prefill from next target
    
    # All 50 US states
    all_states = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    ]
    
    return render_template('add_license.html', 
                         all_states=all_states,
                         account=account,
                         prefill_state=prefill_state)

@app.route('/settings/add-license', methods=['POST'])
def add_license():
    """Add a new license"""
    account = request.form.get('account', 'bhambrick')
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    state_abbr = request.form.get('state_abbr').upper()
    
    # Check if already exists
    if state_abbr in holder_data.get('states', {}):
        return f"License for {state_abbr} already exists", 400
    
    # Get state name
    state_names = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    
    # Create new license entry
    new_license = {
        'name': state_names.get(state_abbr, state_abbr),
        'status': request.form.get('status'),
        'license_type': request.form.get('license_type') or None,
        'license_number': request.form.get('license_number') or None,
        'issued_on': request.form.get('issued_on') or None,
        'expires_on': request.form.get('expires_on') or None,
        'renewal_cost': float(request.form.get('renewal_cost')) if request.form.get('renewal_cost') else None,
        'board_name': request.form.get('board_name') or None,
        'board_phone': request.form.get('board_phone') or None,
        'board_url': request.form.get('board_url') or None,
        'notes': request.form.get('notes') or None,
        'coverage_level': 'draft'
    }
    
    # Add to holder data
    holder_data['states'][state_abbr] = new_license
    
    # Save to file
    import os
    file_path = os.path.join('data', 'license_holders', f'{account}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/manage-licenses?account={account}')



@app.route('/settings/cost-details/<license_id>')
def cost_details(license_id):
    """View cost details for a license"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    license_data = get_license_by_id(holder_data, license_id)
    if not license_data:
        return "License not found", 404
    
    # Enhance with calculated data
    enhanced_license = enhance_license_data(license_data)
    
    return render_template('cost_details.html',
                         license=enhanced_license,
                         holder=holder_data)

@app.route('/settings/add-cost/<license_id>', methods=['POST'])
def add_cost(license_id):
    """Add a cost line item to a license"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Find the license
    license_data = None
    for lic in holder_data.get('licenses', []):
        if lic['license_id'] == license_id:
            license_data = lic
            break
    
    if not license_data:
        return "License not found", 404
    
    # Create new cost entry
    new_cost = {
        'date': request.form.get('date'),
        'category': request.form.get('category'),
        'amount': float(request.form.get('amount')),
        'vendor': request.form.get('vendor') or None,
        'notes': request.form.get('notes') or None,
        'recurring': request.form.get('category') in ['renewal_fee', 'continuing_ed_fee']
    }
    
    # Add to actual_costs array
    if 'actual_costs' not in license_data:
        license_data['actual_costs'] = []
    
    license_data['actual_costs'].append(new_cost)
    
    # Save to file
    import os
    file_path = os.path.join('data', 'license_holders', f'{account}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/settings/cost-details/{license_id}?account={account}')

@app.route('/settings/update-estimated-costs/<license_id>', methods=['POST'])
def update_estimated_costs(license_id):
    """Update estimated costs for budget planning"""
    # Get account from session or URL parameter
    account = get_allowed_account()
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Find the license
    license_data = None
    for lic in holder_data.get('licenses', []):
        if lic['license_id'] == license_id:
            license_data = lic
            break
    
    if not license_data:
        return "License not found", 404
    
    # Update estimated costs
    license_data['estimated_costs'] = {
        'application_fee': float(request.form.get('application_fee') or 0),
        'test_fee': float(request.form.get('test_fee') or 0),
        'trade_book_fee': float(request.form.get('trade_book_fee') or 0),
        'business_law_book_fee': float(request.form.get('business_law_book_fee') or 0),
        'activation_fee': float(request.form.get('activation_fee') or 0),
        'prep_course_fee': float(request.form.get('prep_course_fee') or 0),
        'travel_fee': float(request.form.get('travel_fee') or 0),
        'shipping_fee': float(request.form.get('shipping_fee') or 0),
        'other_fee': float(request.form.get('other_fee') or 0)
    }
    
    # Update planning data
    license_data['planning'] = {
        'est_study_hours': int(request.form.get('est_study_hours') or 0),
        'test_duration_hours': float(request.form.get('test_duration_hours') or 0)
    }
    
    # Save to file
    import os
    file_path = os.path.join('data', 'license_holders', f'{account}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/settings/cost-details/{license_id}?account={account}')



@app.route('/cost-analytics')
def cost_analytics():
    """Cost analytics dashboard with year-by-year breakdown"""
    from datetime import datetime
    
    account = get_allowed_account()
    
    # Handle director view - aggregate all holders
    if account == 'director':
        import glob
        all_licenses = []
        all_holders = []
        
        holder_files = glob.glob('data/license_holders/*.json')
        for holder_file in holder_files:
            with open(holder_file, 'r') as f:
                holder = json.load(f)
                all_holders.append(holder)
                
                for license in holder.get('licenses', []):
                    enhanced = enhance_license_data(license)
                    enhanced['holder_name'] = holder['name']
                    all_licenses.append(enhanced)
        
        director_data = {
            'user_id': 'director',
            'name': 'Director View',
            'role': 'Department Leadership',
            'total_licenses': sum(h.get('total_licenses', 0) for h in all_holders),
            'total_certificates': sum(h.get('total_certificates', 0) for h in all_holders)
        }
        
        holder_data = director_data
        enhanced_licenses = all_licenses
    else:
        holder_data = load_license_holder_data(account)
        if not holder_data:
            return "License holder not found", 404
        
        enhanced_licenses = []
        for license in holder_data.get('licenses', []):
            enhanced = enhance_license_data(license)
            enhanced_licenses.append(enhanced)
    
    # Calculate totals and year breakdown
    total_estimated = 0
    total_actual = 0
    total_variance = 0
    total_recurring = 0
    
    # Year-by-year breakdown
    years_data = {}
    categories = {}
    
    for license in enhanced_licenses:
        # Sum overall totals
        total_estimated += license['cost_totals']['initial_estimated']
        total_actual += license['cost_totals']['actual_spent']
        total_variance += license['cost_totals']['variance']
        
        # Calculate annual recurring
        period_years = license.get('recurring', {}).get('renewal_period_years', 2)
        recurring_per_period = license['cost_totals']['recurring_cost']
        annual_recurring = recurring_per_period / period_years if period_years > 0 else 0
        total_recurring += annual_recurring
        
        # Break down actual costs by year
        for cost_item in license.get('actual_costs', []):
            date_str = cost_item.get('date', '')
            amount = cost_item.get('amount', 0)
            category = cost_item.get('category', 'other_fee')
            
            # Extract year from date
            try:
                if date_str:
                    year = datetime.strptime(date_str, '%Y-%m-%d').year
                else:
                    year = 'Unknown'
            except:
                year = 'Unknown'
            
            # Add to year totals
            if year not in years_data:
                years_data[year] = {
                    'year': year,
                    'total_spent': 0,
                    'license_count': set(),
                    'categories': {}
                }
            
            years_data[year]['total_spent'] += amount
            years_data[year]['license_count'].add(license.get('license_id'))
            
            # Category breakdown within year
            if category not in years_data[year]['categories']:
                years_data[year]['categories'][category] = 0
            years_data[year]['categories'][category] += amount
            
            # Overall category totals
            categories[category] = categories.get(category, 0) + amount
    
    # Convert year license counts from set to int
    for year in years_data:
        years_data[year]['license_count'] = len(years_data[year]['license_count'])
    
    # Sort years (most recent first)
    years_list = sorted(years_data.values(), key=lambda x: x['year'] if isinstance(x['year'], int) else 0, reverse=True)
    
    # Sort categories by amount
    categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    totals = {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_variance': total_variance,
        'total_recurring': total_recurring
    }
    
    return render_template('cost_analytics.html',
                         holder=holder_data,
                         licenses=enhanced_licenses,
                         totals=totals,
                         categories=categories,
                         years=years_list,
                         is_director=(account == 'director'))

@app.route('/team/manage')
def manage_team():
    """Manage license holders"""
    import glob
    
    holders = []
    holder_files = glob.glob('data/license_holders/*.json')
    
    for holder_file in holder_files:
        with open(holder_file, 'r') as f:
            holder = json.load(f)
            
            # Find the PIN for this holder
            holder_pin = None
            for pin, user in USERS.items():
                if user.get('user_id') == holder.get('user_id'):
                    holder_pin = pin
                    break
            
            holder['pin'] = holder_pin
            holders.append(holder)
    
    # Sort by name
    holders.sort(key=lambda x: x.get('name', ''))
    
    return render_template('manage_team.html', holders=holders)

@app.route('/team/add-holder', methods=['POST'])
def add_holder():
    """Add a new license holder"""
    import os
    
    user_id = request.form.get('user_id').lower().strip()
    name = request.form.get('name')
    role = request.form.get('role') or 'License Holder'
    next_target = request.form.get('next_target_state')
    
    # Create new holder structure
    new_holder = {
        'user_id': user_id,
        'name': name,
        'role': role,
        'total_licenses': 0,
        'total_certificates': 0,
        'next_target_state': next_target if next_target else None,
        'licenses': []
    }
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    
    # Check if already exists
    if os.path.exists(file_path):
        return "User ID already exists", 400
    
    with open(file_path, 'w') as f:
        json.dump(new_holder, f, indent=2)
    
    return redirect('/team/manage')



@app.route('/team/edit-holder/<user_id>')
def edit_holder(user_id):
    """Edit a license holder"""
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    return render_template('edit_holder.html', holder=holder_data)

@app.route('/team/update-holder/<user_id>', methods=['POST'])
def update_holder(user_id):
    """Update license holder info"""
    import os
    
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Update fields
    holder_data['name'] = request.form.get('name')
    holder_data['role'] = request.form.get('role')
    holder_data['total_licenses'] = int(request.form.get('total_licenses') or 0)
    holder_data['total_certificates'] = int(request.form.get('total_certificates') or 0)
    holder_data['next_target_state'] = request.form.get('next_target_state') if request.form.get('next_target_state') else None
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect('/team/manage')





@app.route('/team/view/<user_id>')
def team_view_employee(user_id):
    """Detailed view of a specific employee (Manager only)"""
    # Check if user is manager
    if session.get('user_type') != 'manager':
        return "Access denied", 403
    
    # Load employee data
    employee_data = load_license_holder_data(user_id)
    
    if not employee_data:
        return "Employee not found", 404
    
    # Calculate stats
    licenses = employee_data.get('licenses', [])
    states_count = len(set(lic.get('jurisdiction_abbr') for lic in licenses if lic.get('jurisdiction_abbr')))
    expiring_count = sum(1 for lic in licenses 
                        if lic.get('expires_on') and calculate_days_remaining(lic.get('expires_on')) 
                        and calculate_days_remaining(lic.get('expires_on')) <= 60)
    
    # Calculate costs
    total_estimated = 0
    total_actual = 0
    annual_recurring = 0
    costs_by_state = {}
    
    enhanced_licenses = []
    for license in licenses:
        enhanced = enhance_license_data(license)
        enhanced_licenses.append(enhanced)
        
        total_estimated += enhanced['cost_totals']['initial_estimated']
        total_actual += enhanced['cost_totals']['actual_spent']
        
        period_years = enhanced.get('recurring', {}).get('renewal_period_years', 2)
        recurring_per_period = enhanced['cost_totals']['recurring_cost']
        annual_recurring += recurring_per_period / period_years if period_years > 0 else 0
        
        # Group by state
        state = license.get('jurisdiction')
        if state:
            if state not in costs_by_state:
                costs_by_state[state] = {'state': state, 'initial': 0, 'renewal': 0, 'total': 0}
            costs_by_state[state]['initial'] += enhanced['cost_totals']['initial_estimated']
            costs_by_state[state]['renewal'] += enhanced['cost_totals']['recurring_cost']
            costs_by_state[state]['total'] += enhanced['cost_totals']['initial_estimated'] + enhanced['cost_totals']['recurring_cost']
    
    stats = {
        'states_count': states_count,
        'expiring_count': expiring_count,
        'annual_cost': annual_recurring
    }
    
    costs = {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'annual_recurring': annual_recurring,
        'by_state': sorted(costs_by_state.values(), key=lambda x: x['total'], reverse=True)
    }
    
    # Try to load bio data
    bio = None
    bio_file = f'data/bios/{user_id}_bio.json'
    import os
    if os.path.exists(bio_file):
        with open(bio_file, 'r') as f:
            bio = json.load(f)
    
    return render_template('employee_detail.html',
                         employee=employee_data,
                         stats=stats,
                         licenses=enhanced_licenses,
                         costs=costs,
                         bio=bio)

@app.route('/bio/<user_id>')
def bio_builder(user_id):
    """Bio builder page for a license holder"""
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Load or initialize bio
    if 'bio' not in holder_data:
        # Load default bio structure
        import os
        template_path = 'data/bio_templates/default_bio.json'
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                holder_data['bio'] = json.load(f)
        else:
            holder_data['bio'] = {
                'personal_info': {},
                'work_history': [],
                'education': {},
                'plumbing_experience': {},
                'licenses_certifications': {},
                'references': [],
                'background': {},
                'military': {}
            }
    
    # Calculate completion percentage
    completion = calculate_bio_completion(holder_data['bio'])
    
    return render_template('bio_builder.html',
                         holder=holder_data,
                         bio=holder_data['bio'],
                         completion_percentage=completion)

@app.route('/bio/update/<user_id>/<section>', methods=['POST'])
def update_bio_section(user_id, section):
    """Update a section of the bio"""
    import os
    
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Initialize bio if not exists
    if 'bio' not in holder_data:
        holder_data['bio'] = {
            'personal_info': {},
            'work_history': [],
            'education': {},
            'plumbing_experience': {},
            'licenses_certifications': {},
            'references': [],
            'background': {},
            'military': {}
        }
    
    # Update plumbing experience section
    if section == 'experience':
        holder_data['bio']['plumbing_experience'] = {
            'total_years': float(request.form.get('total_years') or 0),
            'residential_hours': int(request.form.get('residential_hours') or 0),
            'commercial_hours': int(request.form.get('commercial_hours') or 0),
            'industrial_hours': int(request.form.get('industrial_hours') or 0),
            'service_repair_hours': int(request.form.get('service_repair_hours') or 0),
            'new_construction_hours': int(request.form.get('new_construction_hours') or 0),
            'systems_experience': {
                'water_supply': 'water_supply' in request.form,
                'drainage': 'drainage' in request.form,
                'gas_piping': 'gas_piping' in request.form,
                'medical_gas': 'medical_gas' in request.form,
                'backflow': 'backflow' in request.form,
                'fire_sprinkler': 'fire_sprinkler' in request.form
            },
            'experience_narrative': request.form.get('experience_narrative')
        }
    
    # Update personal info section
    elif section == 'personal':
        holder_data['bio']['personal_info'] = {
            'full_legal_name': request.form.get('full_legal_name'),
            'middle_name': request.form.get('middle_name'),
            'suffix': request.form.get('suffix'),
            'date_of_birth': request.form.get('date_of_birth'),
            'ssn_last_4': request.form.get('ssn_last_4'),
            'drivers_license': request.form.get('drivers_license'),
            'current_address': {
                'street': request.form.get('address_street'),
                'city': request.form.get('address_city'),
                'state': request.form.get('address_state'),
                'zip': request.form.get('address_zip')
            },
            'phone_cell': request.form.get('phone_cell'),
            'email_primary': request.form.get('email_primary')
        }
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/bio/{user_id}')


@app.route('/bio/add-work/<user_id>', methods=['POST'])
def add_work_history(user_id):
    """Add a comprehensive work history entry"""
    import os
    
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Initialize bio if not exists
    if 'bio' not in holder_data:
        holder_data['bio'] = {'work_history': []}
    
    if 'work_history' not in holder_data['bio']:
        holder_data['bio']['work_history'] = []
    
    # Create comprehensive work entry
    work_entry = {
        # Company info
        'company_name': request.form.get('company_name'),
        'company_phone': request.form.get('company_phone'),
        'address': request.form.get('address'),
        'address_unit': request.form.get('address_unit'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'zip': request.form.get('zip'),
        'county': request.form.get('county'),
        
        # Position info
        'position': request.form.get('position'),
        'employment_type': request.form.get('employment_type'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date') or None,
        'duration': request.form.get('duration'),
        'total_hours': request.form.get('total_hours'),
        
        # Supervisor info
        'supervisor_name': request.form.get('supervisor_name'),
        'supervisor_title': request.form.get('supervisor_title'),
        'supervisor_phone': request.form.get('supervisor_phone'),
        'supervisor_email': request.form.get('supervisor_email'),
        'may_contact': request.form.get('may_contact'),
        
        # Job details
        'responsibilities': request.form.get('responsibilities'),
        'reason_leaving': request.form.get('reason_leaving'),
        'starting_wage': request.form.get('starting_wage'),
        'ending_wage': request.form.get('ending_wage'),
        
        # Work types
        'work_types': {
            'residential': 'work_residential' in request.form,
            'commercial': 'work_commercial' in request.form,
            'industrial': 'work_industrial' in request.form,
            'service': 'work_service' in request.form,
            'new_construction': 'work_new_construction' in request.form,
            'remodel': 'work_remodel' in request.form
        }
    }
    
    # Add to work history (most recent first)
    holder_data['bio']['work_history'].insert(0, work_entry)
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/bio/{user_id}#work')


def calculate_bio_completion(bio):
    """Calculate how complete the bio is (0-100%)"""
    total_fields = 0
    filled_fields = 0
    
    # Personal info (8 key fields)
    personal = bio.get('personal_info', {})
    personal_fields = ['full_legal_name', 'date_of_birth', 'phone_cell', 'email_primary']
    total_fields += len(personal_fields)
    filled_fields += sum(1 for f in personal_fields if personal.get(f))
    
    # Address (4 fields)
    addr = personal.get('current_address', {})
    addr_fields = ['street', 'city', 'state', 'zip']
    total_fields += len(addr_fields)
    filled_fields += sum(1 for f in addr_fields if addr.get(f))
    
    # Work history (count as 1 major section)
    total_fields += 1
    if bio.get('work_history') and len(bio['work_history']) > 0:
        filled_fields += 1
    
    # Education (count as 1 major section)
    total_fields += 1
    edu = bio.get('education', {})
    if edu.get('high_school', {}).get('name'):
        filled_fields += 1
    
    # Plumbing experience (count as 1 major section)
    total_fields += 1
    if bio.get('plumbing_experience', {}).get('total_years'):
        filled_fields += 1
    
    # References (count as 1 major section)
    total_fields += 1
    if bio.get('references') and len(bio['references']) >= 3:
        filled_fields += 1
    
    return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0



@app.route('/bio/add-reference/<user_id>', methods=['POST'])
def add_reference(user_id):
    """Add a professional reference"""
    import os
    
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Initialize bio if not exists
    if 'bio' not in holder_data:
        holder_data['bio'] = {'references': []}
    
    if 'references' not in holder_data['bio']:
        holder_data['bio']['references'] = []
    
    # Create reference entry
    reference = {
        'name': request.form.get('name'),
        'title': request.form.get('title'),
        'relationship': request.form.get('relationship'),
        'years_known': request.form.get('years_known'),
        'company': request.form.get('company'),
        'company_address': request.form.get('company_address'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'zip': request.form.get('zip'),
        'county': request.form.get('county'),
        'phone': request.form.get('phone'),
        'alternate_phone': request.form.get('alternate_phone'),
        'email': request.form.get('email'),
        'best_time_to_call': request.form.get('best_time_to_call'),
        'can_contact_anytime': 'can_contact_anytime' in request.form,
        'has_letter': 'has_letter' in request.form,
        'notes': request.form.get('notes')
    }
    
    # Add to references
    holder_data['bio']['references'].append(reference)
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/bio/{user_id}#references')



@app.route('/bio/add-job-project/<user_id>', methods=['POST'])
def add_job_project(user_id):
    """Add a job project to the library"""
    import os
    
    holder_data = load_license_holder_data(user_id)
    
    if not holder_data:
        return "License holder not found", 404
    
    # Initialize bio/plumbing_experience if needed
    if 'bio' not in holder_data:
        holder_data['bio'] = {'plumbing_experience': {}}
    
    if 'plumbing_experience' not in holder_data['bio']:
        holder_data['bio']['plumbing_experience'] = {}
    
    if 'job_projects' not in holder_data['bio']['plumbing_experience']:
        holder_data['bio']['plumbing_experience']['job_projects'] = []
    
    # Create job project entry
    job_project = {
        'project_name': request.form.get('project_name'),
        'location': request.form.get('location'),
        'completion_date': request.form.get('completion_date'),
        'job_type': request.form.get('job_type'),
        'project_value': request.form.get('project_value'),
        'hours_on_project': request.form.get('hours_on_project'),
        'client_name': request.form.get('client_name'),
        'client_contact': request.form.get('client_contact'),
        'client_phone': request.form.get('client_phone'),
        'client_email': request.form.get('client_email'),
        'scope_summary': request.form.get('scope_summary'),
        'detailed_description': request.form.get('detailed_description'),
        'systems_worked': request.form.get('systems_worked'),
        'your_role': request.form.get('your_role'),
        'permits_required': request.form.get('permits_required'),
        'supervised_others': 'supervised_others' in request.form,
        'crew_size': request.form.get('crew_size'),
        'special_notes': request.form.get('special_notes'),
        'can_use_as_reference': 'can_use_as_reference' in request.form,
        'have_photos': 'have_photos' in request.form
    }
    
    # Add to job projects (most recent first)
    holder_data['bio']['plumbing_experience']['job_projects'].insert(0, job_project)
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{user_id}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    return redirect(f'/bio/{user_id}#experience')



@app.route('/import-csv-page')
def import_csv_page():
    """CSV import page"""
    return render_template('csv_import.html')

@app.route('/import-csv', methods=['POST'])
def import_csv():
    """Handle CSV file upload and import"""
    import csv
    import io
    import os
    import re
    
    if 'csv_file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['csv_file']
    license_holder = request.form.get('license_holder', 'bhambrick')
    overwrite = 'overwrite_existing' in request.form
    
    if file.filename == '':
        return "No file selected", 400
    
    # Read CSV
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    
    # Load license holder data
    holder_data = load_license_holder_data(license_holder)
    if not holder_data:
        return "License holder not found", 404
    
    # State name to abbreviation mapping
    state_mapping = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY'
    }
    
    def clean_currency(value):
        """Remove $, commas and convert to float"""
        if not value or value.strip() == '':
            return 0.0
        cleaned = re.sub(r'[\$,]', '', str(value))
        try:
            return float(cleaned)
        except:
            return 0.0
    
    def parse_renewal_period(value):
        """Extract years from renewal period"""
        if not value:
            return 2
        match = re.search(r'(\d+)', str(value))
        return int(match.group(1)) if match else 2
    
    def parse_hours(value):
        """Extract hours from string"""
        if not value:
            return 0
        match = re.search(r'(\d+)', str(value))
        return int(match.group(1)) if match else 0
    
    imported_count = 0
    updated_count = 0
    
    for row in csv_reader:
        # Get state info
        state_raw = row.get('State', '').strip()
        if not state_raw:
            continue
        
        # Convert state name to abbreviation
        state_abbr = state_raw.upper() if len(state_raw) == 2 else state_mapping.get(state_raw.lower(), state_raw[:2].upper())
        
        # Find or create license for this state
        license_data = None
        for lic in holder_data.get('licenses', []):
            if lic.get('jurisdiction_abbr') == state_abbr:
                license_data = lic
                break
        
        if not license_data:
            # Create new license
            license_id = f"{state_abbr}-{len(holder_data.get('licenses', [])) + 1:03d}"
            license_data = {
                'license_id': license_id,
                'jurisdiction': state_raw if len(state_raw) > 2 else state_abbr,
                'jurisdiction_abbr': state_abbr,
                'jurisdiction_type': 'state',
                'license_type': row.get('License Type', 'Master Plumber'),
                'status': 'not_licensed',
                'estimated_costs': {},
                'actual_costs': [],
                'recurring': {},
                'planning': {}
            }
            holder_data['licenses'].append(license_data)
            imported_count += 1
        else:
            updated_count += 1
        
        # Update estimated costs (only if overwrite is true OR field is empty)
        if overwrite or not license_data.get('estimated_costs'):
            license_data['estimated_costs'] = {}
        
        costs = license_data['estimated_costs']
        
        if overwrite or not costs.get('application_fee'):
            costs['application_fee'] = clean_currency(row.get('Application Fees', 0))
        if overwrite or not costs.get('test_fee'):
            costs['test_fee'] = clean_currency(row.get('Test Fees', 0))
        if overwrite or not costs.get('trade_book_fee'):
            costs['trade_book_fee'] = clean_currency(row.get('Trade Book fees', 0))
        if overwrite or not costs.get('business_law_book_fee'):
            costs['business_law_book_fee'] = clean_currency(row.get('Bus. & Law Book Fee', 0))
        if overwrite or not costs.get('activation_fee'):
            costs['activation_fee'] = clean_currency(row.get('Lic. Activation Fee', 0))
        if overwrite or not costs.get('prep_course_fee'):
            costs['prep_course_fee'] = clean_currency(row.get('Prep Course fees', 0))
        if overwrite or not costs.get('travel_fee'):
            costs['travel_fee'] = clean_currency(row.get('Travel Fees', 0))
        if overwrite or not costs.get('shipping_fee'):
            costs['shipping_fee'] = clean_currency(row.get('Shipping Fees', 0))
        
        # Update recurring costs
        if overwrite or not license_data.get('recurring'):
            license_data['recurring'] = {}
        
        recurring = license_data['recurring']
        if overwrite or not recurring.get('renewal_fee'):
            recurring['renewal_fee'] = clean_currency(row.get('Renewal Fees', 0))
        if overwrite or not recurring.get('continuing_ed_fee'):
            recurring['continuing_ed_fee'] = clean_currency(row.get('Cont. Ed. Fees', 0))
        if overwrite or not recurring.get('renewal_period_years'):
            recurring['renewal_period_years'] = parse_renewal_period(row.get('Renewal Period', '2 Years'))
        
        # Update planning
        if overwrite or not license_data.get('planning'):
            license_data['planning'] = {}
        
        planning = license_data['planning']
        if overwrite or not planning.get('est_study_hours'):
            planning['est_study_hours'] = parse_hours(row.get('Est. Study Hrs.', 0))
        if overwrite or not planning.get('test_duration_hours'):
            planning['test_duration_hours'] = parse_hours(row.get('Test Duration', 0))
    
    # Save to file
    file_path = os.path.join('data', 'license_holders', f'{license_holder}.json')
    with open(file_path, 'w') as f:
        json.dump(holder_data, f, indent=2)
    
    # Redirect to cost analytics with success message
    return f'''
    <html>
    <head>
        <meta http-equiv="refresh" content="3;url=/cost-analytics?account={license_holder}">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card">
                <div class="card-body text-center">
                    <h3 class="text-success">✅ Import Successful!</h3>
                    <p class="lead">{imported_count} new licenses created</p>
                    <p class="lead">{updated_count} existing licenses updated</p>
                    <p class="text-muted">Redirecting to Cost Analytics...</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/download-csv-template')
def download_csv_template():
    """Download CSV template"""
    import csv
    import io
    from flask import make_response
    
    # Create CSV template
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'State', 'License Type', 'Application Fees', 'Test Fees', 
        'Trade Book fees', 'Bus. & Law Book Fee', 'Lic. Activation Fee',
        'Prep Course fees', 'Travel Fees', 'Shipping Fees', 
        'Renewal Fees', 'Cont. Ed. Fees', 'Renewal Period', 
        'Est. Study Hrs.', 'Test Duration'
    ])
    
    # Example rows
    writer.writerow([
        'Texas', 'Master Plumber', '$225.00', '$0.00', '$126.73', '$0.00',
        '$225.00', '$550.00', '$0.00', '$0.00', '$300.00', '$100.00',
        '1 Years', '24', '8 Hours'
    ])
    writer.writerow([
        'California', 'C-36 Plumbing Contractor', '$235.00', '$0.00', '$0.00', '$0.00',
        '$0.00', '$482.50', '$850.00', '$0.00', '$400.00', '$0.00',
        '2 Years', '10', '10 Hours'
    ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=licensing_costs_template.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response



@app.route('/state/<state_abbr>')
def state_detail(state_abbr):
    """Display detailed state licensing information"""
    import os
    
    # Load state detail data
    state_file = os.path.join('data', 'state_details', f'{state_abbr.upper()}.json')
    
    if not os.path.exists(state_file):
        return f"State information for {state_abbr.upper()} not yet available. We're building this database state by state!", 404
    
    with open(state_file, 'r') as f:
        state_data = json.load(f)
    
    return render_template('state_detail.html', state=state_data)


@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404


# Mapbox configuration
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYmhhbWJyaWNrIiwiYSI6ImNtZzhiZjU1cTA1eHIya3EzdmI2c3Y0bHQifQ.iMTr0v9G_VIPWtJe6S7tkQ'

app.secret_key = 'your-secret-key-change-this-in-production-12345'  # For sessions


@app.context_processor
def inject_mapbox_token():
    """Make Mapbox token available to all templates"""
    return dict(mapbox_token=MAPBOX_ACCESS_TOKEN)

@app.template_filter('format_date')
def format_date(date_string):
    """Format ISO date string to human readable"""
    if not date_string:
        return 'Not set'
    try:
        date_obj = datetime.fromisoformat(date_string)
        return date_obj.strftime('%B %d, %Y')
    except (ValueError, TypeError):
        return date_string


@app.route('/admin/state-encyclopedia')
def admin_state_encyclopedia():
    """Admin page to manage state detail files"""
    print("🔍 DEBUG: admin_state_encyclopedia route hit!")
    import os
    import glob
    
    state_files = glob.glob('data/state_details/*.json')
    states = []
    
    for file_path in state_files:
        with open(file_path, 'r') as f:
            state_data = json.load(f)
            
            # Calculate completion percentage
            completion = calculate_state_completion(state_data)
            
            states.append({
                'abbr': state_data['state_abbr'],
                'name': state_data['state'],
                'completion': completion,
                'file_path': file_path
            })
    
    # Sort by name
    states.sort(key=lambda x: x['name'])
    
    return render_template('admin_state_encyclopedia.html', states=states)




@app.route('/states/directory')
def states_directory():
    """Read-only state requirements directory for license holders"""
    import os
    import glob
    
    state_files = glob.glob('data/state_details/*.json')
    states = []
    
    for file_path in state_files:
        with open(file_path, 'r') as f:
            state_data = json.load(f)
            
            # Calculate completion percentage
            completion = calculate_state_completion(state_data)
            
            states.append({
                'abbr': state_data['state_abbr'],
                'name': state_data['state'],
                'completion': completion,
                'governing_body': state_data.get('governing_body', 'N/A'),
                'board_phone': state_data.get('board_phone', 'N/A')
            })
    
    # Sort by name
    states.sort(key=lambda x: x['name'])
    
    return render_template('states_directory.html', states=states)

@app.route('/admin/edit-state/<state_abbr>')
def admin_edit_state(state_abbr):
    """Edit a specific state's details"""
    import os
    
    file_path = os.path.join('data', 'state_details', f'{state_abbr.upper()}.json')
    
    if not os.path.exists(file_path):
        return f"State file not found for {state_abbr}", 404
    
    with open(file_path, 'r') as f:
        state_data = json.load(f)
    
    return render_template('admin_edit_state.html', state=state_data)


@app.route('/admin/save-state/<state_abbr>', methods=['POST'])
def admin_save_state(state_abbr):
    """Save updated state details"""
    import os
    
    file_path = os.path.join('data', 'state_details', f'{state_abbr.upper()}.json')
    
    # Get JSON data from form
    try:
        state_data = json.loads(request.form.get('state_data'))
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        return redirect(f'/admin/edit-state/{state_abbr}?success=1')
    
    except Exception as e:
        return f"Error saving state: {str(e)}", 500


def calculate_state_completion(state_data):
    """Calculate what percentage of state data is filled out"""
    total_fields = 0
    filled_fields = 0
    
    # Basic info (5 fields)
    basic_fields = ['governing_body', 'board_phone', 'board_website', 'board_address']
    total_fields += len(basic_fields)
    filled_fields += sum(1 for f in basic_fields if state_data.get(f) and state_data.get(f) != 'TBD' and '000-000' not in str(state_data.get(f)))
    
    # License types (count as 1 major section)
    total_fields += 1
    if state_data.get('license_types') and len(state_data['license_types']) > 0:
        first_license = state_data['license_types'][0]
        if first_license.get('experience_required') != 'TBD':
            filled_fields += 1
    
    # Requirements (count as 1 major section)
    total_fields += 1
    if state_data.get('requirements', {}).get('education') != 'TBD':
        filled_fields += 1
    
    # Examination (count as 1 major section)
    total_fields += 1
    if state_data.get('examination', {}).get('provider') != 'TBD':
        filled_fields += 1
    
    # Application process (count as 1 major section)
    total_fields += 1
    if state_data.get('application_process') and len(state_data['application_process']) > 1:
        filled_fields += 1
    
    # Renewal (count as 1 major section)
    total_fields += 1
    renewal_fee = state_data.get('renewal', {}).get('renewal_fee', 0)
    # Handle both string and int renewal fees
    if renewal_fee and str(renewal_fee).strip() and renewal_fee != 0:
        filled_fields += 1
    
    return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0


@app.route('/admin/active-states')
def admin_active_states():
    """Manage active states (Manager only)"""
    if session.get('user_type') != 'manager':
        return "Access denied", 403
    
    import os
    import glob
    
    # Load coverage data
    coverage = {}
    coverage_file = 'data/company/coverage.json'
    if os.path.exists(coverage_file):
        with open(coverage_file, 'r') as f:
            coverage = json.load(f)
    
    # Load all state names
    all_states = {}
    base_states_file = 'data/base_data/all_states.json'
    if os.path.exists(base_states_file):
        with open(base_states_file, 'r') as f:
            states_data = json.load(f)
            all_states = {abbr: data['name'] for abbr, data in states_data.items()}
    
    # Build state names lookup
    state_names = all_states
    
    # Get details about who is licensed in each state
    state_details = {}
    holder_files = glob.glob('data/license_holders/*.json')
    for holder_file in holder_files:
        with open(holder_file, 'r') as f:
            holder = json.load(f)
            for license in holder.get('licenses', []):
                abbr = license.get('jurisdiction_abbr')
                if abbr:
                    if abbr not in state_details:
                        state_details[abbr] = {'holders': []}
                    if holder['name'] not in state_details[abbr]['holders']:
                        state_details[abbr]['holders'].append(holder['name'])
    
    # Load revenues (from coverage or separate file)
    state_revenues = coverage.get('state_revenues', {})
    total_revenue = sum(state_revenues.values())
    
    return render_template('active_states_manager.html',
                         coverage=coverage,
                         all_states=all_states,
                         state_names=state_names,
                         state_details=state_details,
                         state_revenues=state_revenues,
                         total_revenue=total_revenue)

@app.route('/admin/active-states/add', methods=['POST'])
def admin_active_states_add():
    """Add a state to a category"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    state = data.get('state')
    status = data.get('status')
    
    coverage_file = 'data/company/coverage.json'
    with open(coverage_file, 'r') as f:
        coverage = json.load(f)
    
    if status == 'covered':
        if state not in coverage['covered_states']:
            coverage['covered_states'].append(state)
    elif status == 'in_progress':
        if state not in coverage['in_progress_states']:
            coverage['in_progress_states'].append(state)
    elif status == 'target':
        if state not in coverage['target_states']:
            coverage['target_states'].append(state)
    
    coverage['total_states_covered'] = len(coverage['covered_states'])
    coverage['total_states_in_progress'] = len(coverage['in_progress_states'])
    
    with open(coverage_file, 'w') as f:
        json.dump(coverage, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/admin/active-states/move', methods=['POST'])
def admin_active_states_move():
    """Move a state between categories"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    state = data.get('state')
    from_status = data.get('from')
    to_status = data.get('to')
    
    coverage_file = 'data/company/coverage.json'
    with open(coverage_file, 'r') as f:
        coverage = json.load(f)
    
    if from_status == 'covered' and state in coverage['covered_states']:
        coverage['covered_states'].remove(state)
    elif from_status == 'in_progress' and state in coverage['in_progress_states']:
        coverage['in_progress_states'].remove(state)
    elif from_status == 'target' and state in coverage['target_states']:
        coverage['target_states'].remove(state)
    
    if to_status == 'covered' and state not in coverage['covered_states']:
        coverage['covered_states'].append(state)
    elif to_status == 'in_progress' and state not in coverage['in_progress_states']:
        coverage['in_progress_states'].append(state)
    elif to_status == 'target' and state not in coverage['target_states']:
        coverage['target_states'].append(state)
    
    coverage['total_states_covered'] = len(coverage['covered_states'])
    coverage['total_states_in_progress'] = len(coverage['in_progress_states'])
    
    with open(coverage_file, 'w') as f:
        json.dump(coverage, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/admin/active-states/remove', methods=['POST'])
def admin_active_states_remove():
    """Remove a state from a category"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    state = data.get('state')
    status = data.get('status')
    
    coverage_file = 'data/company/coverage.json'
    with open(coverage_file, 'r') as f:
        coverage = json.load(f)
    
    if status == 'covered' and state in coverage['covered_states']:
        coverage['covered_states'].remove(state)
    elif status == 'in_progress' and state in coverage['in_progress_states']:
        coverage['in_progress_states'].remove(state)
    elif status == 'target' and state in coverage['target_states']:
        coverage['target_states'].remove(state)
    
    coverage['total_states_covered'] = len(coverage['covered_states'])
    coverage['total_states_in_progress'] = len(coverage['in_progress_states'])
    
    with open(coverage_file, 'w') as f:
        json.dump(coverage, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/admin/active-states/update-revenue', methods=['POST'])
def admin_active_states_update_revenue():
    """Update revenue for a state"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    state = data.get('state')
    revenue = data.get('revenue', 0)
    
    coverage_file = 'data/company/coverage.json'
    with open(coverage_file, 'r') as f:
        coverage = json.load(f)
    
    if 'state_revenues' not in coverage:
        coverage['state_revenues'] = {}
    
    coverage['state_revenues'][state] = revenue
    
    with open(coverage_file, 'w') as f:
        json.dump(coverage, f, indent=2)
    
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# ==================== ACCOUNT MANAGEMENT ROUTES (DIRECTOR ONLY) ====================

@app.route('/api/account/lock/<user_id>', methods=['POST'])
def lock_account(user_id):
    """Lock a license holder account"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    holder_file = f'data/license_holders/{user_id}.json'
    if not os.path.exists(holder_file):
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    with open(holder_file, 'r') as f:
        holder = json.load(f)
    
    holder['account_status'] = 'locked'
    holder['locked_date'] = datetime.now().strftime('%Y-%m-%d')
    holder['locked_by'] = session.get('name', 'Manager')
    
    with open(holder_file, 'w') as f:
        json.dump(holder, f, indent=2)
    
    return jsonify({'success': True, 'message': f"Account locked for {holder['name']}"})

@app.route('/api/account/unlock/<user_id>', methods=['POST'])
def unlock_account(user_id):
    """Unlock a license holder account"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    holder_file = f'data/license_holders/{user_id}.json'
    if not os.path.exists(holder_file):
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    with open(holder_file, 'r') as f:
        holder = json.load(f)
    
    holder['account_status'] = 'active'
    holder['locked_date'] = None
    holder['locked_by'] = None
    
    with open(holder_file, 'w') as f:
        json.dump(holder, f, indent=2)
    
    return jsonify({'success': True, 'message': f"Account unlocked for {holder['name']}"})

@app.route('/api/account/delete/<user_id>', methods=['POST'])
def delete_account(user_id):
    """Delete a license holder account"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    holder_file = f'data/license_holders/{user_id}.json'
    if not os.path.exists(holder_file):
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Load holder info for confirmation message
    with open(holder_file, 'r') as f:
        holder = json.load(f)
    
    # Delete the file
    os.remove(holder_file)
    
    # Also remove from USERS dict if exists
    pin_to_remove = None
    for pin, user in USERS.items():
        if user['user_id'] == user_id:
            pin_to_remove = pin
            break
    
    if pin_to_remove:
        del USERS[pin_to_remove]
    
    return jsonify({'success': True, 'message': f"Account deleted for {holder['name']}"})

@app.route('/api/account/create', methods=['POST'])
def create_account():
    """Create a new license holder account"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    name = data.get('name', '').strip()
    role = data.get('role', 'License Holder').strip()
    email = data.get('email', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    # Generate user_id from name (lowercase, no spaces)
    user_id = name.lower().replace(' ', '').replace('.', '')[:20]
    
    # Check if user_id already exists
    holder_file = f'data/license_holders/{user_id}.json'
    if os.path.exists(holder_file):
        # Add a number suffix
        counter = 2
        while os.path.exists(f'data/license_holders/{user_id}{counter}.json'):
            counter += 1
        user_id = f'{user_id}{counter}'
        holder_file = f'data/license_holders/{user_id}.json'
    
    # Generate unique PIN (200XXX series)
    import random
    existing_pins = set(USERS.keys())
    while True:
        pin = f'2{random.randint(10000, 99999)}'
        if pin not in existing_pins:
            break
    
    # Create holder data
    holder = {
        'user_id': user_id,
        'name': name,
        'role': role,
        'email': email,
        'account_status': 'active',
        'locked_date': None,
        'locked_by': None,
        'total_licenses': 0,
        'total_certificates': 0,
        'licenses': [],
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'created_by': session.get('name', 'Manager')
    }
    
    # Save to file
    with open(holder_file, 'w') as f:
        json.dump(holder, f, indent=2)
    
    # Add to USERS dict
    USERS[pin] = {
        'pin': pin,
        'user_type': 'license_holder',
        'name': name,
        'email': email,
        'user_id': user_id
    }
    
    return jsonify({
        'success': True,
        'message': f"Account created for {name}",
        'pin': pin,
        'user_id': user_id,
        'name': name
    })


@app.route('/settings/delete-cost/<license_id>/<int:cost_index>', methods=['POST'])
def delete_cost(license_id, cost_index):
    """Delete a cost entry"""
    account = get_allowed_account()
    holder = load_license_holder_data(account)
    
    if not holder:
        return jsonify({'success': False, 'error': 'Holder not found'}), 404
    
    # Find the license
    license = next((lic for lic in holder.get('licenses', []) if lic.get('license_id') == license_id), None)
    
    if not license:
        return jsonify({'success': False, 'error': 'License not found'}), 404
    
    # Delete the cost entry
    actual_costs = license.get('actual_costs', [])
    if 0 <= cost_index < len(actual_costs):
        del actual_costs[cost_index]
        
        # Recalculate totals
        license['cost_totals']['actual_spent'] = sum(c.get('amount', 0) for c in actual_costs)
        
        # Save
        holder_file = f'data/license_holders/{account}.json'
        with open(holder_file, 'w') as f:
            json.dump(holder, f, indent=2)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid cost index'}), 400


@app.route('/team/set-goal/<user_id>', methods=['POST'])
def set_license_goal(user_id):
    """Set next license goal for a holder (Director only)"""
    print(f"DEBUG: set_license_goal called with user_id={user_id}")
    print(f"DEBUG: user_type={session.get('user_type')}")
    
    if session.get('user_type') != 'manager':
        print("DEBUG: Not a manager, redirecting")
        return redirect('/home')
    
    target_state = request.form.get('target_state')
    print(f"DEBUG: target_state={target_state}")
    
    holder_file = f'data/license_holders/{user_id}.json'
    print(f"DEBUG: holder_file={holder_file}, exists={os.path.exists(holder_file)}")
    
    if not os.path.exists(holder_file):
        print("DEBUG: Holder file not found")
        return redirect('/team/manage')
    
    with open(holder_file, 'r') as f:
        holder = json.load(f)
    
    holder['next_target_state'] = target_state
    
    with open(holder_file, 'w') as f:
        json.dump(holder, f, indent=2)
    
    return redirect(f'/manage-licenses?account={user_id}')

@app.route('/team/clear-goal/<user_id>', methods=['POST'])
def clear_license_goal(user_id):
    """Clear next license goal for a holder (Director only)"""
    if session.get('user_type') != 'manager':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    holder_file = f'data/license_holders/{user_id}.json'
    if not os.path.exists(holder_file):
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    with open(holder_file, 'r') as f:
        holder = json.load(f)
    
    holder['next_target_state'] = None
    
    with open(holder_file, 'w') as f:
        json.dump(holder, f, indent=2)
    
    return jsonify({'success': True})



@app.route('/cost-analytics/export-pdf')
def export_cost_analytics_pdf():
    """Generate PDF cost analytics report"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from io import BytesIO
    from datetime import datetime
    
    # Get the same data as the analytics page
    account = get_allowed_account()
    
    if account == 'director':
        import glob
        all_licenses = []
        
        holder_files = glob.glob('data/license_holders/*.json')
        for holder_file in holder_files:
            with open(holder_file, 'r') as f:
                holder = json.load(f)
                for license in holder.get('licenses', []):
                    enhanced = enhance_license_data(license)
                    enhanced['holder_name'] = holder['name']
                    all_licenses.append(enhanced)
        
        enhanced_licenses = all_licenses
    else:
        holder_data = load_license_holder_data(account)
        enhanced_licenses = []
        for license in holder_data.get('licenses', []):
            enhanced = enhance_license_data(license)
            enhanced_licenses.append(enhanced)
    
    # Calculate totals and year breakdown
    total_actual = 0
    total_recurring = 0
    years_data = {}
    categories = {}
    
    for license in enhanced_licenses:
        total_actual += license['cost_totals']['actual_spent']
        
        period_years = license.get('recurring', {}).get('renewal_period_years', 2)
        recurring_per_period = license['cost_totals']['recurring_cost']
        annual_recurring = recurring_per_period / period_years if period_years > 0 else 0
        total_recurring += annual_recurring
        
        for cost_item in license.get('actual_costs', []):
            date_str = cost_item.get('date', '')
            amount = cost_item.get('amount', 0)
            
            try:
                if date_str:
                    year = datetime.strptime(date_str, '%Y-%m-%d').year
                else:
                    year = 'Unknown'
            except:
                year = 'Unknown'
            
            if year not in years_data:
                years_data[year] = {'year': year, 'total_spent': 0, 'license_count': set()}
            
            years_data[year]['total_spent'] += amount
            years_data[year]['license_count'].add(license.get('license_id'))
            
            # Track categories
            category = cost_item.get('category', 'other_fee')
            categories[category] = categories.get(category, 0) + amount
    
    # Sort categories by amount
    categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    for year in years_data:
        years_data[year]['license_count'] = len(years_data[year]['license_count'])
    
    years_list = sorted(years_data.values(), key=lambda x: x['year'] if isinstance(x['year'], int) else 0, reverse=True)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1a2634'), spaceAfter=20, alignment=TA_CENTER)
    elements.append(Paragraph('Licensing Roadmap - Cost Analytics Report', title_style))
    
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph(f'Generated: {datetime.now().strftime("%B %d, %Y")}', subtitle_style))
    
    # Introduction
    intro_style = ParagraphStyle('Intro', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=20, alignment=4)
    intro_text = '''
    <b>Report Overview:</b> This financial analysis provides a comprehensive breakdown of licensing costs 
    for Repipe Specialists' compliance operations across all active jurisdictions. The report includes 
    actual expenditures, recurring annual costs, and year-over-year spending trends.<br/><br/>
    
    <b>Budget Methodology:</b> Budget figures represent estimated licensing costs based on historical 
    data derived from actual expenditures incurred during the initial license acquisition process. 
    These estimates serve as planning benchmarks and may vary based on jurisdiction-specific requirements, 
    examination outcomes, and application timelines. Variance analysis identifies licenses where actual 
    costs exceeded or fell below initial projections.
    '''
    elements.append(Paragraph(intro_text, intro_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    summary_data = [
        ['EXECUTIVE SUMMARY', ''],
        ['Total Spent', f'${total_actual:,.2f}'],
        ['Annual Recurring', f'${total_recurring:,.2f}'],
        ['Total Licenses', str(len(enhanced_licenses))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2634')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Year breakdown
    if years_list:
        year_data = [['SPENDING BY YEAR', '', '']]
        year_data.append(['Year', 'Total Spent', 'License Count'])
        
        for year in years_list:
            year_data.append([
                str(year['year']),
                f"${year['total_spent']:,.2f}",
                str(year['license_count'])
            ])
        
        year_table = Table(year_data, colWidths=[2*inch, 2*inch, 2*inch])
        year_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2634')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(year_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Category breakdown
    if categories:
        category_data = [['SPENDING BY CATEGORY', '', '']]
        category_data.append(['Category', 'Amount', 'Percentage'])
        
        for category, amount in categories.items():
            percentage = (amount / total_actual * 100) if total_actual > 0 else 0
            category_data.append([
                category.replace('_', ' ').title(),
                f"${amount:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        category_table = Table(category_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2634')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(category_table)
        elements.append(PageBreak())
    
    # License details with Budget and Variance
    license_data = [['COSTS BY LICENSE', '', '', '', '', '']]
    if account == 'director':
        license_data.append(['Holder', 'Jurisdiction', 'Budget', 'Actual', 'Variance', 'Ann. Recur.'])
    else:
        license_data.append(['Jurisdiction', 'Type', 'Budget', 'Actual', 'Variance', 'Ann. Recur.'])
    
    for license in enhanced_licenses:
        annual_rec = license['cost_totals']['recurring_cost'] / license.get('recurring', {}).get('renewal_period_years', 2)
        budget = license['cost_totals']['initial_estimated']
        actual = license['cost_totals']['actual_spent']
        variance = actual - budget
        
        variance_str = f"${variance:,.2f}" if variance >= 0 else f"-${abs(variance):,.2f}"
        
        if account == 'director':
            license_data.append([
                license.get('holder_name', ''),
                license['jurisdiction'],
                f"${budget:,.2f}",
                f"${actual:,.2f}",
                variance_str,
                f"${annual_rec:,.2f}"
            ])
        else:
            license_data.append([
                license['jurisdiction'],
                license.get('license_type', ''),
                f"${budget:,.2f}",
                f"${actual:,.2f}",
                variance_str,
                f"${annual_rec:,.2f}"
            ])
    
    license_table = Table(license_data, colWidths=[1.2*inch, 1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
    license_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2634')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(license_table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'cost_analytics_{datetime.now().strftime("%Y-%m-%d")}.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
