-- Licensing Roadmap Database Schema
-- Adds RS (Repipe Specialists) internal license tracking tables
-- To shared compliance database used by Partner Portal

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- License holders table
CREATE TABLE rs_license_holders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    employee_id VARCHAR(50),
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    hire_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    next_target_state VARCHAR(2),
    pin VARCHAR(10) UNIQUE,
    total_licenses INTEGER DEFAULT 0,
    total_certificates INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Licenses table
CREATE TABLE rs_licenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    holder_id UUID NOT NULL REFERENCES rs_license_holders(id) ON DELETE CASCADE,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL,
    jurisdiction_abbr VARCHAR(2) NOT NULL,
    jurisdiction_type VARCHAR(50) NOT NULL,
    license_type VARCHAR(100) NOT NULL,
    license_number VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'not_licensed',
    issued_on DATE,
    expires_on DATE,
    board_name VARCHAR(255),
    board_phone VARCHAR(20),
    board_email VARCHAR(255),
    board_url TEXT,
    board_address TEXT,
    designated_role VARCHAR(50),
    renewal_period_years INTEGER DEFAULT 2,
    renewal_fee DECIMAL(10,2),
    continuing_ed_required BOOLEAN DEFAULT false,
    continuing_ed_hours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- License costs table
CREATE TABLE rs_license_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_id UUID NOT NULL REFERENCES rs_licenses(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    vendor VARCHAR(255),
    notes TEXT,
    receipt_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- License budgets table
CREATE TABLE rs_license_budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_id UUID NOT NULL REFERENCES rs_licenses(id) ON DELETE CASCADE,
    application_fee DECIMAL(10,2) DEFAULT 0,
    test_fee DECIMAL(10,2) DEFAULT 0,
    trade_book_fee DECIMAL(10,2) DEFAULT 0,
    business_law_book_fee DECIMAL(10,2) DEFAULT 0,
    activation_fee DECIMAL(10,2) DEFAULT 0,
    prep_course_fee DECIMAL(10,2) DEFAULT 0,
    travel_estimate DECIMAL(10,2) DEFAULT 0,
    shipping_estimate DECIMAL(10,2) DEFAULT 0,
    renewal_fee DECIMAL(10,2) DEFAULT 0,
    continuing_ed_fee DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company coverage table
CREATE TABLE rs_company_coverage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state_code VARCHAR(2) NOT NULL UNIQUE,
    state_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'target',
    licensed_holders TEXT[],
    primary_license_holder_id UUID REFERENCES rs_license_holders(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bio data table
CREATE TABLE rs_bio_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    holder_id UUID NOT NULL UNIQUE REFERENCES rs_license_holders(id) ON DELETE CASCADE,
    personal_info JSONB,
    addresses JSONB,
    work_history JSONB[],
    plumbing_experience JSONB,
    job_projects JSONB[],
    education JSONB,
    references JSONB[],
    background JSONB,
    military JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_rs_licenses_holder ON rs_licenses(holder_id);
CREATE INDEX idx_rs_licenses_status ON rs_licenses(status);
CREATE INDEX idx_rs_licenses_expires ON rs_licenses(expires_on);
CREATE INDEX idx_rs_license_costs_license ON rs_license_costs(license_id);
CREATE INDEX idx_rs_license_costs_date ON rs_license_costs(date);
CREATE INDEX idx_rs_company_coverage_status ON rs_company_coverage(status);

-- Update timestamp trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_rs_license_holders_updated_at BEFORE UPDATE ON rs_license_holders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rs_licenses_updated_at BEFORE UPDATE ON rs_licenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rs_license_budgets_updated_at BEFORE UPDATE ON rs_license_budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rs_company_coverage_updated_at BEFORE UPDATE ON rs_company_coverage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rs_bio_data_updated_at BEFORE UPDATE ON rs_bio_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Licensing Roadmap tables created successfully!';
    RAISE NOTICE 'Tables: rs_license_holders, rs_licenses, rs_license_costs, rs_license_budgets, rs_company_coverage, rs_bio_data';
END $$;
