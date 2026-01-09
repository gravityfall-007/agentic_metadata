import clickhouse_connect
import os

def init_db():
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='default',
        password='password'
    )
    
    sql_path = os.path.join(os.path.dirname(__file__), '../storage/olap/agent_events.sql')
    with open(sql_path, 'r') as f:
        schema = f.read()

    # Split by semicolon to handle multiple statements if any, though likely just one
    statements = [s.strip() for s in schema.split(';') if s.strip()]
    
    for statement in statements:
        print(f"Executing: {statement[:50]}...")
        client.command(statement)
    
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
