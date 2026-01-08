"""
Migrate JSON license data to PostgreSQL database
Converts data/license_holders/*.json -> rs_* tables
"""
import json
import os
from datetime import datetime
from models import (
    SessionLocal, RSLicenseHolder, RSLicense, RSLicenseCost, 
    RSLicenseBudget, RSCompanyCoverage, RSBioData
)
from decimal import Decimal

def parse_date(date_str):
    """Convert date string to date object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def migrate_holder(holder_data, db):
    """Migrate a single license holder"""
    print(f"\n📋 Migrating: {holder_data['name']}")
    
    # Create holder
    holder = RSLicenseHolder(
        employee_id=holder_data.get('user_id'),
        full_name=holder_data['name'],
        role=holder_data.get('role'),
        status='active',
        next_target_state=holder_data.get('next_target_state'),
        pin=holder_data.get('pin'),
        total_licenses=holder_data.get('total_licenses', 0),
        total_certificates=holder_data.get('total_certificates', 0)
    )
    db.add(holder)
    db.flush()  # Get the holder.id
    
    print(f"  ✅ Created holder: {holder.full_name} (ID: {holder.id})")
    
    # Migrate licenses
    license_count = 0
    cost_count = 0
    
    for lic_data in holder_data.get('licenses', []):
        # Create license
        license = RSLicense(
            holder_id=holder.id,
            license_id=lic_data['license_id'],
            jurisdiction=lic_data['jurisdiction'],
            jurisdiction_abbr=lic_data['jurisdiction_abbr'],
            jurisdiction_type=lic_data['jurisdiction_type'],
            license_type=lic_data['license_type'],
            license_number=lic_data.get('license_number'),
            status=lic_data.get('status', 'not_licensed'),
            issued_on=parse_date(lic_data.get('issued_on')),
            expires_on=parse_date(lic_data.get('expires_on')),
            board_name=lic_data.get('board_name'),
            board_phone=lic_data.get('board_phone'),
            board_email=lic_data.get('board_email'),
            board_url=lic_data.get('board_url'),
            designated_role=lic_data.get('designated_role'),
            renewal_period_years=lic_data.get('recurring', {}).get('renewal_period_years', 2),
            renewal_fee=Decimal(str(lic_data.get('recurring', {}).get('renewal_fee', 0)))
        )
        db.add(license)
        db.flush()
        license_count += 1
        
        # Create budget
        estimated = lic_data.get('estimated_costs', {})
        budget = RSLicenseBudget(
            license_id=license.id,
            application_fee=Decimal(str(estimated.get('application_fee', 0))),
            test_fee=Decimal(str(estimated.get('test_fee', 0))),
            trade_book_fee=Decimal(str(estimated.get('trade_book_fee', 0))),
            business_law_book_fee=Decimal(str(estimated.get('business_law_book_fee', 0))),
            activation_fee=Decimal(str(estimated.get('activation_fee', 0))),
            prep_course_fee=Decimal(str(estimated.get('prep_course_fee', 0))),
            travel_estimate=Decimal(str(estimated.get('travel', 0))),
            shipping_estimate=Decimal(str(estimated.get('shipping', 0))),
            renewal_fee=Decimal(str(estimated.get('renewal_fee', 0))),
            continuing_ed_fee=Decimal(str(estimated.get('continuing_ed_fee', 0)))
        )
        db.add(budget)
        
        # Create costs
        for cost_data in lic_data.get('actual_costs', []):
            cost = RSLicenseCost(
                license_id=license.id,
                date=parse_date(cost_data['date']),
                category=cost_data['category'],
                amount=Decimal(str(cost_data['amount'])),
                vendor=cost_data.get('vendor'),
                notes=cost_data.get('notes')
            )
            db.add(cost)
            cost_count += 1
    
    print(f"  ✅ Created {license_count} licenses with {cost_count} costs")
    
    # Migrate bio data if exists
    if 'bio' in holder_data:
        bio = RSBioData(
            holder_id=holder.id,
            personal_info=holder_data['bio'].get('personal_info'),
            addresses=holder_data['bio'].get('addresses'),
            work_history=holder_data['bio'].get('work_history'),
            plumbing_experience=holder_data['bio'].get('plumbing_experience'),
            job_projects=holder_data['bio'].get('job_projects'),
            education=holder_data['bio'].get('education'),
            professional_references=holder_data['bio'].get('references'),
            background=holder_data['bio'].get('background'),
            military=holder_data['bio'].get('military')
        )
        db.add(bio)
        print(f"  ✅ Created bio data")

def migrate_company_coverage(db):
    """Migrate company coverage data"""
    coverage_file = 'data/company/coverage.json'
    if not os.path.exists(coverage_file):
        print("⚠️  No company coverage file found")
        return
    
    with open(coverage_file, 'r') as f:
        coverage_data = json.load(f)
    
    print(f"\n🌍 Migrating company coverage...")
    
    for state_code, state_info in coverage_data.items():
        coverage = RSCompanyCoverage(
            state_code=state_code,
            state_name=state_info['state_name'],
            status=state_info.get('status', 'target'),
            licensed_holders=state_info.get('licensed_holders', [])
        )
        db.add(coverage)
    
    print(f"  ✅ Created {len(coverage_data)} state coverage records")

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 LICENSING ROADMAP - JSON TO DATABASE MIGRATION")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Migrate license holders
        holder_dir = 'data/license_holders'
        holder_files = [f for f in os.listdir(holder_dir) if f.endswith('.json')]
        
        print(f"\nFound {len(holder_files)} license holder files")
        
        for filename in holder_files:
            if filename == 'director.json':
                continue  # Skip director account
            
            filepath = os.path.join(holder_dir, filename)
            with open(filepath, 'r') as f:
                holder_data = json.load(f)
            
            migrate_holder(holder_data, db)
        
        # Migrate company coverage
        # migrate_company_coverage(db)  # Already migrated separately
        
        # Commit everything
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        
        # Summary
        holder_count = db.query(RSLicenseHolder).count()
        license_count = db.query(RSLicense).count()
        cost_count = db.query(RSLicenseCost).count()
        coverage_count = db.query(RSCompanyCoverage).count()
        
        print(f"\n📊 Summary:")
        print(f"  License Holders: {holder_count}")
        print(f"  Licenses: {license_count}")
        print(f"  Cost Entries: {cost_count}")
        print(f"  State Coverage: {coverage_count}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    main()
