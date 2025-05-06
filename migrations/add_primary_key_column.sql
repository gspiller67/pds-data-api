-- Add is_primary_key column to table_columns
ALTER TABLE table_columns ADD COLUMN IF NOT EXISTS is_primary_key BOOLEAN DEFAULT false; 