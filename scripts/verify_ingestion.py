"""
Verification script for data ingestion.

This script queries the ClickHouse database to verify that events (including input/output data)
are being correctly stored.
"""

import clickhouse_connect
import sys

def verify():
    """
    Connect to ClickHouse and verify event storage.

    Prints the total event count and specific details of the latest event.
    """
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='default',
            password='password'
        )
        
        result = client.query("SELECT count() FROM agent_events")
        count = result.result_rows[0][0]
        print(f"Event count: {count}")
        
        if count > 0:
            events = client.query("SELECT event_id, input_data, output_data FROM agent_events ORDER BY timestamp DESC LIMIT 1").result_rows
            print("Latest event I/O:", events)
            
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
