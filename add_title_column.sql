-- Add title column to pds_tables if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'pds_tables' 
        AND column_name = 'title'
    ) THEN
        ALTER TABLE pds_tables ADD COLUMN title VARCHAR;
    END IF;
END $$; 