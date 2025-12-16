"""
Licensing Roadmap Flask Application
A plumber-focused state licensing tracking system
"""

from flask import Flask, render_template, jsonify, abort, request, redirect, redirect
import json
import os
from datetime import datetime, timedelta
import markdown

app = Flask(__name__)
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
def home():
    """Home dashboard"""
    account = request.args.get('account', 'bhambrick')
    
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
        
        holder_data = {
            'user_id': 'director',
            'name': 'Director View',
            'role': 'Department Leadership',
            'total_licenses': sum(h.get('total_licenses', 0) for h in all_holders),
            'total_certificates': sum(h.get('total_certificates', 0) for h in all_holders)
        }
        enhanced_licenses = all_licenses
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
    account = request.args.get('account', 'bhambrick')
    
    # Handle director view differently
    if account == 'director':
        return render_director_view()
    
    # Load license holder data
    holder_data = load_license_holder_data(account)
    
    if not holder_data:
        return "License holder not found", 404
    
    states = holder_data.get("states", {})
    
    # Convert licenses array to states dict for map compatibility
    enhanced_states = {}
    for license in holder_data.get('licenses', []):
        abbr = license.get('jurisdiction_abbr')
        if abbr:
            # Use the first license for each state (primary)
            if abbr not in enhanced_states:
                enhanced = license.copy()
                enhanced["status_class"] = get_state_status_class(license)
                enhanced["badge_text"] = get_state_badge_text(license)
                enhanced["days_remaining"] = calculate_days_remaining(license.get("expires_on"))
                enhanced["name"] = license.get("jurisdiction")
                enhanced["state_abbr"] = abbr
                enhanced_states[abbr] = enhanced
    
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
                         training_roadmap=training_roadmap_json)

def render_director_view():
    """Render the director/leadership aggregated view"""
    import glob
    
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
                        'board_name': license.get('board_name'),
                        'board_url': license.get('board_url'),
                        'expires_on': license.get('expires_on'),
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
                         training_roadmap=training_roadmap_json)


@app.route('/licensing/<state_abbrev>')
def state_detail(state_abbrev):
    """State-specific detail page"""
    state_abbr = state_abbrev.upper()
    data = load_licensing_data()
    states = data.get('states', {})
    
    if state_abbr not in states:
        abort(404)
    
    state_data = states[state_abbr].copy()
    state_data['status_class'] = get_state_status_class(state_data)
    state_data['badge_text'] = get_state_badge_text(state_data)
    state_data['days_remaining'] = calculate_days_remaining(state_data.get('expires_on'))
    
    # Load detailed content from markdown
    detail_content = load_state_detail(state_abbr)
    
    return render_template('state_detail.html',
                         state=state_data,
                         state_abbr=state_abbr,
                         detail_content=detail_content)


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
    account = request.args.get('account', 'bhambrick')
    
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
                    enhanced['holder_name'] = holder['name']  # Track who owns it
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
    account = request.args.get('account', 'bhambrick')
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
    account = request.args.get('account', 'bhambrick')
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
    account = request.args.get('account', 'bhambrick')
    
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
                         account=account)

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
    account = request.args.get('account', 'bhambrick')
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
    account = request.args.get('account', 'bhambrick')
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
    account = request.args.get('account', 'bhambrick')
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
    """Cost analytics dashboard"""
    account = request.args.get('account', 'bhambrick')
    
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
        # Individual holder
        holder_data = load_license_holder_data(account)
        if not holder_data:
            return "License holder not found", 404
        
        enhanced_licenses = []
        for license in holder_data.get('licenses', []):
            enhanced = enhance_license_data(license)
            enhanced_licenses.append(enhanced)
    
    # Process all licenses
    enhanced_licenses = []
    total_estimated = 0
    total_actual = 0
    total_variance = 0
    total_recurring = 0
    
    # Category breakdown
    categories = {}
    
    for license in holder_data.get('licenses', []):
        enhanced = enhance_license_data(license)
        enhanced_licenses.append(enhanced)
        
        # Sum totals
        total_estimated += enhanced['cost_totals']['initial_estimated']
        total_actual += enhanced['cost_totals']['actual_spent']
        total_variance += enhanced['cost_totals']['variance']
        
        # Calculate annual recurring (normalize to per year)
        period_years = enhanced.get('recurring', {}).get('renewal_period_years', 2)
        recurring_per_period = enhanced['cost_totals']['recurring_cost']
        annual_recurring = recurring_per_period / period_years if period_years > 0 else 0
        total_recurring += annual_recurring
        
        # Break down by category
        for cost_item in enhanced.get('actual_costs', []):
            category = cost_item.get('category', 'other_fee')
            amount = cost_item.get('amount', 0)
            categories[category] = categories.get(category, 0) + amount
    
    # Sort categories by amount (descending)
    categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    totals = {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_variance': total_variance,
        'total_recurring': total_recurring
    }
    
    return render_template('cost_analytics.html',
                         licenses=enhanced_licenses,
                         totals=totals,
                         categories=categories,
                         holder=holder_data)


@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404


# Mapbox configuration
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYmhhbWJyaWNrIiwiYSI6ImNtZzhiZjU1cTA1eHIya3EzdmI2c3Y0bHQifQ.iMTr0v9G_VIPWtJe6S7tkQ'

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/')
def index():
    """Redirect to licensing roadmap"""
    return render_template('index.html')


@app.route('/licensing-roadmap')
@app.route('/licensing/<state_abbrev>')
def state_detail(state_abbrev):
    """State-specific detail page"""
    state_abbr = state_abbrev.upper()
    data = load_licensing_data()
    states = data.get('states', {})
    
    if state_abbr not in states:
        abort(404)
    
    state_data = states[state_abbr].copy()
    state_data['status_class'] = get_state_status_class(state_data)
    state_data['badge_text'] = get_state_badge_text(state_data)
    state_data['days_remaining'] = calculate_days_remaining(state_data.get('expires_on'))
    
    # Load detailed content from markdown
    detail_content = load_state_detail(state_abbr)
    
    return render_template('state_detail.html',
                         state=state_data,
                         state_abbr=state_abbr,
                         detail_content=detail_content)


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


@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404


# Mapbox configuration
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYmhhbWJyaWNrIiwiYSI6ImNtZzhiZjU1cTA1eHIya3EzdmI2c3Y0bHQifQ.iMTr0v9G_VIPWtJe6S7tkQ'

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

