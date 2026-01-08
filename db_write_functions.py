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
