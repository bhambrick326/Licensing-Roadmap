"""
Fix: Migrate company coverage with correct format
"""
import json
from models import SessionLocal, RSCompanyCoverage

def migrate_company_coverage():
    """Migrate company coverage data"""
    with open('data/company/coverage.json', 'r') as f:
        coverage_data = json.load(f)
    
    db = SessionLocal()
    
    try:
        print("\n🌍 Migrating company coverage...")
        
        # Map state codes to full names
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
        
        count = 0
        
        # Covered states (licensed)
        for state_code in coverage_data.get('covered_states', []):
            coverage = RSCompanyCoverage(
                state_code=state_code,
                state_name=state_names.get(state_code, state_code),
                status='licensed'
            )
            db.add(coverage)
            count += 1
        
        # In progress states
        for state_code in coverage_data.get('in_progress_states', []):
            coverage = RSCompanyCoverage(
                state_code=state_code,
                state_name=state_names.get(state_code, state_code),
                status='in_progress'
            )
            db.add(coverage)
            count += 1
        
        # Target states
        for state_code in coverage_data.get('target_states', []):
            coverage = RSCompanyCoverage(
                state_code=state_code,
                state_name=state_names.get(state_code, state_code),
                status='target'
            )
            db.add(coverage)
            count += 1
        
        db.commit()
        print(f"  ✅ Created {count} state coverage records")
        print("\n✅ Company coverage migration complete!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    migrate_company_coverage()
