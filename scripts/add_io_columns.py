"""
Database migration script to add input_data and output_data columns.

This script connects to ClickHouse and executes ALTER TABLE statements to add new columns.
"""

import clickhouse_connect
import sys

def migrate_db():
    """
    Migrate the database schema to include input/output columns.

    This function adds 'input_data' and 'output_data' columns to the 'agent_events' table
    if they do not already exist.
    """
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='default',
            password='password'
        )
        
        print("Adding input_data column...")
        client.command("ALTER TABLE agent_events ADD COLUMN IF NOT EXISTS input_data String")
        
        print("Adding output_data column...")
        client.command("ALTER TABLE agent_events ADD COLUMN IF NOT EXISTS output_data String")
        
        print("Migration completed successfully.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_db()
