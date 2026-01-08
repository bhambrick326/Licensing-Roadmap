"""
Database replacement functions for app.py
These replace the JSON file reading functions
"""

def load_license_holder_data(user_id='bhambrick'):
    """Load data for a specific license holder from database"""
    db = SessionLocal()
    try:
        # Query by employee_id or pin
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == user_id) | (RSLicenseHolder.pin == user_id)
        ).first()
        
        if not holder:
            return None
        
        # Convert to dictionary format (same as old JSON structure)
        holder_data = {
            'user_id': holder.employee_id or holder.pin,
            'name': holder.full_name,
            'role': holder.role,
            'total_licenses': holder.total_licenses,
            'total_certificates': holder.total_certificates,
            'next_target_state': holder.next_target_state,
            'pin': holder.pin,
            'licenses': []
        }
        
        # Add licenses
        for lic in holder.licenses:
            license_dict = {
                'license_id': lic.license_id,
                'jurisdiction': lic.jurisdiction,
                'jurisdiction_abbr': lic.jurisdiction_abbr,
                'jurisdiction_type': lic.jurisdiction_type,
                'license_type': lic.license_type,
                'license_number': lic.license_number,
                'status': lic.status,
                'issued_on': lic.issued_on.isoformat() if lic.issued_on else None,
                'expires_on': lic.expires_on.isoformat() if lic.expires_on else None,
                'board_name': lic.board_name,
                'board_phone': lic.board_phone,
                'board_email': lic.board_email,
                'board_url': lic.board_url,
                'designated_role': lic.designated_role,
                'recurring': {
                    'renewal_period_years': lic.renewal_period_years,
                    'renewal_fee': float(lic.renewal_fee) if lic.renewal_fee else 0
                },
                'actual_costs': [],
                'estimated_costs': {},
                'cost_totals': {
                    'initial_estimated': 0,
                    'actual_spent': 0,
                    'variance': 0,
                    'recurring_cost': 0
                }
            }
            
            # Add actual costs
            for cost in lic.costs:
                license_dict['actual_costs'].append({
                    'date': cost.date.isoformat() if cost.date else None,
                    'category': cost.category,
                    'amount': float(cost.amount),
                    'vendor': cost.vendor,
                    'notes': cost.notes
                })
            
            # Add budget (estimated costs)
            if lic.budget:
                budget = lic.budget
                license_dict['estimated_costs'] = {
                    'application_fee': float(budget.application_fee or 0),
                    'test_fee': float(budget.test_fee or 0),
                    'trade_book_fee': float(budget.trade_book_fee or 0),
                    'business_law_book_fee': float(budget.business_law_book_fee or 0),
                    'activation_fee': float(budget.activation_fee or 0),
                    'prep_course_fee': float(budget.prep_course_fee or 0),
                    'travel': float(budget.travel_estimate or 0),
                    'shipping': float(budget.shipping_estimate or 0),
                    'renewal_fee': float(budget.renewal_fee or 0),
                    'continuing_ed_fee': float(budget.continuing_ed_fee or 0)
                }
                
                # Calculate totals
                initial_estimated = sum([
                    float(budget.application_fee or 0),
                    float(budget.test_fee or 0),
                    float(budget.trade_book_fee or 0),
                    float(budget.business_law_book_fee or 0),
                    float(budget.activation_fee or 0),
                    float(budget.prep_course_fee or 0),
                    float(budget.travel_estimate or 0),
                    float(budget.shipping_estimate or 0)
                ])
                
                actual_spent = sum(float(c.amount) for c in lic.costs)
                recurring_cost = float(budget.renewal_fee or 0) + float(budget.continuing_ed_fee or 0)
                
                license_dict['cost_totals'] = {
                    'initial_estimated': initial_estimated,
                    'actual_spent': actual_spent,
                    'variance': actual_spent - initial_estimated,
                    'recurring_cost': recurring_cost
                }
            
            holder_data['licenses'].append(license_dict)
        
        # Add bio data if exists
        if holder.bio_data:
            bio = holder.bio_data
            holder_data['bio'] = {
                'personal_info': bio.personal_info,
                'addresses': bio.addresses,
                'work_history': bio.work_history,
                'plumbing_experience': bio.plumbing_experience,
                'job_projects': bio.job_projects,
                'education': bio.education,
                'references': bio.professional_references,
                'background': bio.background,
                'military': bio.military
            }
        
        return holder_data
        
    finally:
        db.close()


def load_company_data():
    """Load company-wide coverage data from database"""
    db = SessionLocal()
    try:
        coverage_records = db.query(RSCompanyCoverage).all()
        
        company_data = {
            'company_name': 'Repipe Specialists',
            'covered_states': [],
            'in_progress_states': [],
            'target_states': []
        }
        
        for record in coverage_records:
            if record.status == 'licensed':
                company_data['covered_states'].append(record.state_code)
            elif record.status == 'in_progress':
                company_data['in_progress_states'].append(record.state_code)
            elif record.status == 'target':
                company_data['target_states'].append(record.state_code)
        
        company_data['total_states_covered'] = len(company_data['covered_states'])
        company_data['total_states_in_progress'] = len(company_data['in_progress_states'])
        
        return company_data
        
    finally:
        db.close()
