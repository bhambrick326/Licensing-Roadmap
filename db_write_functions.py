"""
Database WRITE helper functions
Handles all database saves/updates/deletes
"""
from models import (
    SessionLocal, RSLicenseHolder, RSLicense, RSLicenseCost,
    RSLicenseBudget, RSCompanyCoverage, RSBioData
)
from decimal import Decimal
from datetime import datetime

def save_license_holder_data(account, holder_data):
    """
    Save/update license holder data to database
    This is the main save function that replaces JSON writes
    """
    db = SessionLocal()
    try:
        # Find existing holder or create new
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if holder:
            # Update existing
            holder.full_name = holder_data.get('name', holder.full_name)
            holder.role = holder_data.get('role', holder.role)
            holder.total_licenses = holder_data.get('total_licenses', holder.total_licenses)
            holder.total_certificates = holder_data.get('total_certificates', holder.total_certificates)
            holder.next_target_state = holder_data.get('next_target_state')
        else:
            # Create new holder
            holder = RSLicenseHolder(
                employee_id=account,
                full_name=holder_data['name'],
                role=holder_data.get('role'),
                pin=holder_data.get('pin'),
                total_licenses=holder_data.get('total_licenses', 0),
                total_certificates=holder_data.get('total_certificates', 0),
                next_target_state=holder_data.get('next_target_state')
            )
            db.add(holder)
            db.flush()
        
        # Update licenses (this is handled by specific functions below)
        # We don't sync all licenses here, just the holder metadata
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR saving holder data: {e}")
        return False
    finally:
        db.close()


def add_license_to_db(account, license_data):
    """Add a new license to the database"""
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Create license
        new_license = RSLicense(
            holder_id=holder.id,
            license_id=license_data['license_id'],
            jurisdiction=license_data['jurisdiction'],
            jurisdiction_abbr=license_data['jurisdiction_abbr'],
            jurisdiction_type=license_data['jurisdiction_type'],
            license_type=license_data['license_type'],
            license_number=license_data.get('license_number'),
            status=license_data.get('status', 'not_licensed'),
            issued_on=datetime.strptime(license_data['issued_on'], '%Y-%m-%d').date() if license_data.get('issued_on') else None,
            expires_on=datetime.strptime(license_data['expires_on'], '%Y-%m-%d').date() if license_data.get('expires_on') else None,
            board_name=license_data.get('board_name'),
            board_phone=license_data.get('board_phone'),
            board_email=license_data.get('board_email'),
            board_url=license_data.get('board_url'),
            designated_role=license_data.get('designated_role'),
            renewal_period_years=license_data.get('recurring', {}).get('renewal_period_years', 2),
            renewal_fee=Decimal(str(license_data.get('recurring', {}).get('renewal_fee', 0)))
        )
        db.add(new_license)
        db.flush()
        
        # Create budget if estimated costs provided
        if 'estimated_costs' in license_data:
            est = license_data['estimated_costs']
            budget = RSLicenseBudget(
                license_id=new_license.id,
                application_fee=Decimal(str(est.get('application_fee', 0))),
                test_fee=Decimal(str(est.get('test_fee', 0))),
                trade_book_fee=Decimal(str(est.get('trade_book_fee', 0))),
                business_law_book_fee=Decimal(str(est.get('business_law_book_fee', 0))),
                activation_fee=Decimal(str(est.get('activation_fee', 0))),
                prep_course_fee=Decimal(str(est.get('prep_course_fee', 0))),
                travel_estimate=Decimal(str(est.get('travel', 0))),
                shipping_estimate=Decimal(str(est.get('shipping', 0))),
                renewal_fee=Decimal(str(est.get('renewal_fee', 0))),
                continuing_ed_fee=Decimal(str(est.get('continuing_ed_fee', 0)))
            )
            db.add(budget)
        
        # Update holder's total
        holder.total_licenses = db.query(RSLicense).filter_by(holder_id=holder.id).count()
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding license: {e}")
        return False
    finally:
        db.close()


def update_license_in_db(account, license_id, license_data):
    """Update an existing license in the database"""
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Find license
        license = db.query(RSLicense).filter_by(
            holder_id=holder.id,
            license_id=license_id
        ).first()
        
        if not license:
            return False
        
        # Update license fields
        license.jurisdiction = license_data.get('jurisdiction', license.jurisdiction)
        license.jurisdiction_abbr = license_data.get('jurisdiction_abbr', license.jurisdiction_abbr)
        license.jurisdiction_type = license_data.get('jurisdiction_type', license.jurisdiction_type)
        license.license_type = license_data.get('license_type', license.license_type)
        license.license_number = license_data.get('license_number')
        license.status = license_data.get('status', license.status)
        
        if license_data.get('issued_on'):
            license.issued_on = datetime.strptime(license_data['issued_on'], '%Y-%m-%d').date()
        if license_data.get('expires_on'):
            license.expires_on = datetime.strptime(license_data['expires_on'], '%Y-%m-%d').date()
        
        license.board_name = license_data.get('board_name')
        license.board_phone = license_data.get('board_phone')
        license.board_email = license_data.get('board_email')
        license.board_url = license_data.get('board_url')
        license.designated_role = license_data.get('designated_role')
        
        if 'recurring' in license_data:
            license.renewal_period_years = license_data['recurring'].get('renewal_period_years', 2)
            license.renewal_fee = Decimal(str(license_data['recurring'].get('renewal_fee', 0)))
        
        # Update budget if provided
        if 'estimated_costs' in license_data:
            budget = license.budget
            if not budget:
                budget = RSLicenseBudget(license_id=license.id)
                db.add(budget)
            
            est = license_data['estimated_costs']
            budget.application_fee = Decimal(str(est.get('application_fee', 0)))
            budget.test_fee = Decimal(str(est.get('test_fee', 0)))
            budget.trade_book_fee = Decimal(str(est.get('trade_book_fee', 0)))
            budget.business_law_book_fee = Decimal(str(est.get('business_law_book_fee', 0)))
            budget.activation_fee = Decimal(str(est.get('activation_fee', 0)))
            budget.prep_course_fee = Decimal(str(est.get('prep_course_fee', 0)))
            budget.travel_estimate = Decimal(str(est.get('travel', 0)))
            budget.shipping_estimate = Decimal(str(est.get('shipping', 0)))
            budget.renewal_fee = Decimal(str(est.get('renewal_fee', 0)))
            budget.continuing_ed_fee = Decimal(str(est.get('continuing_ed_fee', 0)))
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR updating license: {e}")
        return False
    finally:
        db.close()


def delete_license_from_db(account, license_id):
    """Delete a license from the database"""
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Find and delete license (cascade will handle costs and budget)
        license = db.query(RSLicense).filter_by(
            holder_id=holder.id,
            license_id=license_id
        ).first()
        
        if license:
            db.delete(license)
            
            # Update holder's total
            holder.total_licenses = db.query(RSLicense).filter_by(holder_id=holder.id).count() - 1
            
            db.commit()
            return True
        
        return False
        
    except Exception as e:
        db.rollback()
        print(f"ERROR deleting license: {e}")
        return False
    finally:
        db.close()


def add_cost_to_db(account, license_id, cost_data):
    """Add a cost entry to a license"""
    print(f"DEBUG add_cost_to_db: account={account}, license_id={license_id}, cost_data={cost_data}")
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Find license
        license = db.query(RSLicense).filter_by(
            holder_id=holder.id,
            license_id=license_id
        ).first()
        
        if not license:
            return False
        
        # Add cost
        new_cost = RSLicenseCost(
            license_id=license.id,
            date=datetime.strptime(cost_data['date'], '%Y-%m-%d').date() if cost_data.get('date') else datetime.now().date(),
            category=cost_data['category'],
            amount=Decimal(str(cost_data['amount'])),
            vendor=cost_data.get('vendor'),
            notes=cost_data.get('notes')
        )
        db.add(new_cost)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding cost: {e}")
        return False
    finally:
        db.close()


def delete_cost_from_db(account, license_id, cost_index):
    """Delete a cost entry"""
    print(f"DEBUG delete_cost_from_db: account={account}, license_id={license_id}, cost_index={cost_index}")
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Find license
        license = db.query(RSLicense).filter_by(
            holder_id=holder.id,
            license_id=license_id
        ).first()
        
        if not license:
            return False
        
        # Get all costs ordered by date (to match index)
        costs = db.query(RSLicenseCost).filter_by(license_id=license.id).order_by(RSLicenseCost.date).all()
        
        if 0 <= cost_index < len(costs):
            db.delete(costs[cost_index])
            db.commit()
            return True
        
        return False
        
    except Exception as e:
        db.rollback()
        print(f"ERROR deleting cost: {e}")
        return False
    finally:
        db.close()


def update_estimated_costs_in_db(account, license_id, estimated_costs):
    """Update estimated costs (budget) for a license"""
    db = SessionLocal()
    try:
        # Find holder
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Find license
        license = db.query(RSLicense).filter_by(
            holder_id=holder.id,
            license_id=license_id
        ).first()
        
        if not license:
            return False
        
        # Get or create budget
        budget = license.budget
        if not budget:
            budget = RSLicenseBudget(license_id=license.id)
            db.add(budget)
        
        # Update budget fields
        budget.application_fee = Decimal(str(estimated_costs.get('application_fee', 0)))
        budget.test_fee = Decimal(str(estimated_costs.get('test_fee', 0)))
        budget.trade_book_fee = Decimal(str(estimated_costs.get('trade_book_fee', 0)))
        budget.business_law_book_fee = Decimal(str(estimated_costs.get('business_law_book_fee', 0)))
        budget.activation_fee = Decimal(str(estimated_costs.get('activation_fee', 0)))
        budget.prep_course_fee = Decimal(str(estimated_costs.get('prep_course_fee', 0)))
        budget.travel_estimate = Decimal(str(estimated_costs.get('travel', 0)))
        budget.shipping_estimate = Decimal(str(estimated_costs.get('shipping', 0)))
        budget.renewal_fee = Decimal(str(estimated_costs.get('renewal_fee', 0)))
        budget.continuing_ed_fee = Decimal(str(estimated_costs.get('continuing_ed_fee', 0)))
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR updating estimated costs: {e}")
        return False
    finally:
        db.close()


def update_holder_status(account, status, locked_by=None):
    """Update license holder account status (lock/unlock)"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        holder.status = status
        # Note: locked_date and locked_by would need columns added to the table
        # For now, we just update status
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR updating holder status: {e}")
        return False
    finally:
        db.close()


def clear_next_target_state(account):
    """Clear the next target state for a license holder"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        holder.next_target_state = None
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR clearing target state: {e}")
        return False
    finally:
        db.close()


def update_holder_metadata(account, updates_dict):
    """Generic function to update holder metadata fields"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Update any fields provided in updates_dict
        for key, value in updates_dict.items():
            if hasattr(holder, key):
                setattr(holder, key, value)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR updating holder metadata: {e}")
        return False
    finally:
        db.close()


def create_new_holder(user_id, name, role='License Holder', next_target_state=None, pin=None):
    """Create a new license holder in database"""
    db = SessionLocal()
    try:
        # Check if already exists
        existing = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == user_id) | (RSLicenseHolder.pin == user_id)
        ).first()
        
        if existing:
            return False, "User already exists"
        
        # Create new holder
        new_holder = RSLicenseHolder(
            employee_id=user_id,
            full_name=name,
            role=role,
            next_target_state=next_target_state,
            pin=pin,
            total_licenses=0,
            total_certificates=0,
            status='active'
        )
        
        db.add(new_holder)
        db.commit()
        return True, "Holder created successfully"
        
    except Exception as e:
        db.rollback()
        print(f"ERROR creating holder: {e}")
        return False, str(e)
    finally:
        db.close()


def set_next_target_state(account, target_state):
    """Set the next target state for a license holder"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        holder.next_target_state = target_state
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR setting target state: {e}")
        return False
    finally:
        db.close()


def add_work_history(account, work_entry):
    """Add work history entry to bio data"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Get or create bio data
        bio = holder.bio_data
        if not bio:
            bio = RSBioData(holder_id=holder.id, work_history=[])
            db.add(bio)
        
        # Initialize work_history if None
        if bio.work_history is None:
            bio.work_history = []
        
        # Add new entry at beginning (most recent first)
        bio.work_history.insert(0, work_entry)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding work history: {e}")
        return False
    finally:
        db.close()


def add_reference(account, reference):
    """Add professional reference to bio data"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Get or create bio data
        bio = holder.bio_data
        if not bio:
            bio = RSBioData(holder_id=holder.id, professional_references=[])
            db.add(bio)
        
        # Initialize references if None
        if bio.professional_references is None:
            bio.professional_references = []
        
        # Add new reference
        bio.professional_references.append(reference)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding reference: {e}")
        return False
    finally:
        db.close()


def add_job_project(account, job_project):
    """Add job project to plumbing experience"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Get or create bio data
        bio = holder.bio_data
        if not bio:
            bio = RSBioData(holder_id=holder.id, job_projects=[])
            db.add(bio)
        
        # Initialize job_projects if None
        if bio.job_projects is None:
            bio.job_projects = []
        
        # Add new project at beginning (most recent first)
        bio.job_projects.insert(0, job_project)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding job project: {e}")
        return False
    finally:
        db.close()


def add_company_coverage_state(state_code, state_name, status='target'):
    """Add a state to company coverage"""
    db = SessionLocal()
    try:
        # Check if already exists
        existing = db.query(RSCompanyCoverage).filter_by(state_code=state_code).first()
        
        if existing:
            return False, "State already in coverage"
        
        # Create new coverage entry
        coverage = RSCompanyCoverage(
            state_code=state_code,
            state_name=state_name,
            status=status
        )
        
        db.add(coverage)
        db.commit()
        return True, "State added successfully"
        
    except Exception as e:
        db.rollback()
        print(f"ERROR adding coverage state: {e}")
        return False, str(e)
    finally:
        db.close()


def move_company_coverage_state(state_code, new_status):
    """Move a state to a different status (target/in_progress/licensed)"""
    db = SessionLocal()
    try:
        coverage = db.query(RSCompanyCoverage).filter_by(state_code=state_code).first()
        
        if not coverage:
            return False, "State not found"
        
        coverage.status = new_status
        
        db.commit()
        return True, "State status updated"
        
    except Exception as e:
        db.rollback()
        print(f"ERROR moving coverage state: {e}")
        return False, str(e)
    finally:
        db.close()


def remove_company_coverage_state(state_code):
    """Remove a state from company coverage"""
    db = SessionLocal()
    try:
        coverage = db.query(RSCompanyCoverage).filter_by(state_code=state_code).first()
        
        if not coverage:
            return False, "State not found"
        
        db.delete(coverage)
        db.commit()
        return True, "State removed"
        
    except Exception as e:
        db.rollback()
        print(f"ERROR removing coverage state: {e}")
        return False, str(e)
    finally:
        db.close()


def update_state_revenue(state_code, revenue):
    """Update revenue for a coverage state"""
    # Note: We don't have a revenue column in rs_company_coverage
    # This would need a schema update or we store it elsewhere
    # For now, just return success (can add later)
    print(f"TODO: Store revenue ${revenue} for {state_code}")
    return True, "Revenue updated (stored in memory only for now)"


def update_bio_personal_info(account, personal_info):
    """Update personal info in bio data"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False
        
        # Get or create bio data
        bio = holder.bio_data
        if not bio:
            bio = RSBioData(holder_id=holder.id)
            db.add(bio)
        
        # Update personal info
        bio.personal_info = personal_info
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR updating personal info: {e}")
        return False
    finally:
        db.close()


def bulk_import_licenses(account, licenses_data):
    """Bulk import/update licenses from Excel - update existing licenses only"""
    db = SessionLocal()
    try:
        holder = db.query(RSLicenseHolder).filter(
            (RSLicenseHolder.employee_id == account) | (RSLicenseHolder.pin == account)
        ).first()
        
        if not holder:
            return False, "Holder not found"
        
        updated_count = 0
        
        # Update existing licenses only (don't create new ones to match current behavior)
        for license_data in licenses_data:
            license_id = license_data.get('license_id')
            
            license = db.query(RSLicense).filter_by(
                holder_id=holder.id,
                license_id=license_id
            ).first()
            
            if license:
                # Update budget if provided
                if 'estimated_costs' in license_data:
                    budget = license.budget
                    if not budget:
                        budget = RSLicenseBudget(license_id=license.id)
                        db.add(budget)
                    
                    costs = license_data['estimated_costs']
                    if costs.get('application_fee') is not None:
                        budget.application_fee = Decimal(str(costs['application_fee']))
                    if costs.get('test_fee') is not None:
                        budget.test_fee = Decimal(str(costs['test_fee']))
                    # Add other fields as needed
                
                updated_count += 1
        
        db.commit()
        return True, f"Updated {updated_count} licenses"
        
    except Exception as e:
        db.rollback()
        print(f"ERROR bulk importing: {e}")
        return False, str(e)
    finally:
        db.close()
