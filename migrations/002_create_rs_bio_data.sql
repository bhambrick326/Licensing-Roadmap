-- Fix rs_bio_data table (references is a reserved word)
CREATE TABLE rs_bio_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    holder_id UUID NOT NULL UNIQUE REFERENCES rs_license_holders(id) ON DELETE CASCADE,
    personal_info JSONB,
    addresses JSONB,
    work_history JSONB[],
    plumbing_experience JSONB,
    job_projects JSONB[],
    education JSONB,
    professional_references JSONB[],
    background JSONB,
    military JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for updated_at
CREATE TRIGGER update_rs_bio_data_updated_at BEFORE UPDATE ON rs_bio_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success
SELECT 'rs_bio_data table created successfully!' as result;
