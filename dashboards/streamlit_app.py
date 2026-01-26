"""
Streamlit dashboard for Agentic Metadata.

This application provides visualizations of agent performance and an interactive playground
to test enterprise features.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import clickhouse_connect
import sys
import os
import time

# Add root to verify imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from sdk.enterprise.client import EnterpriseClient
    from sdk.enterprise.cost import BudgetManager, BudgetExceededError
except ImportError:
    # Fallback for dev environment if module not installed
    EnterpriseClient = None

# Page Configuration
st.set_page_config(page_title="Agent Observability", layout="wide", page_icon="🕵️")

# Database Connection
@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='default',
        password='password'
    )

def run_query(query):
    try:
        client = get_client()
        return client.query_df(query)
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

def command(cmd):
    try:
        client = get_client()
        return client.command(cmd)
    except Exception as e:
        return None

# --- VIEWS ---

def show_dashboard():
    st.title("🕵️ Agent Observability Dashboard")
    
    # KPIs
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = command("SELECT count() FROM agent_events")
        st.metric("Total Events", int(total_events) if total_events else 0)
    
    with col2:
        total_cost = command("SELECT sum(cost_usd) FROM agent_events")
        cost_val = float(total_cost) if total_cost is not None else 0.0
        st.metric("Total Cost (USD)", f"${cost_val:.6f}")
    
    with col3:
        total_tokens = command("SELECT sum(tokens_in + tokens_out) FROM agent_events")
        st.metric("Total Tokens", int(total_tokens) if total_tokens else 0)
    
    with col4:
        avg_latency = command("SELECT avg(duration_ms) FROM agent_events")
        lat_val = float(avg_latency) if avg_latency is not None else 0.0
        st.metric("Avg Latency (ms)", f"{lat_val:.2f}")
    
    st.divider()
    col5, col6 = st.columns(2)
    
    with col5:
        success_rate = command("SELECT countIf(status = 'success') / count() FROM agent_events")
        st.metric("Success Rate", f"{float(success_rate) * 100:.1f}%" if success_rate is not None else "0.0%")
    
    with col6:
        error_count = command("SELECT countIf(status = 'error') FROM agent_events")
        st.metric("Error Count", int(error_count) if error_count is not None else 0)

    # Charts
    st.divider()
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("Events Over Time")
        df_time = run_query("""
            SELECT toStartOfMinute(timestamp) as time, count() as events 
            FROM agent_events 
            GROUP BY time 
            ORDER BY time
        """)
        if not df_time.empty:
            fig_time = px.line(df_time, x='time', y='events', title="Events per Minute")
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No data for timeline.")
    
    with col_c2:
        st.subheader("Cost by Model")
        df_cost = run_query("""
            SELECT model, sum(cost_usd) as total_cost 
            FROM agent_events 
            WHERE model != ''
            GROUP BY model
        """)
        if not df_cost.empty:
            fig_cost = px.bar(df_cost, x='model', y='total_cost', title="Cost Distribution")
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("No cost data available.")
    
    # RESTORED CHARTS
    col_c3, col_c4 = st.columns(2)
    
    with col_c3:
        st.subheader("Latency Distribution")
        df_latency = run_query("SELECT duration_ms FROM agent_events")
        if not df_latency.empty:
            fig_lat = px.histogram(df_latency, x="duration_ms", nbins=20, title="Latency Distribution (ms)")
            st.plotly_chart(fig_lat, use_container_width=True)
        else:
            st.info("No latency data.")
            
    with col_c4:
        st.subheader("Token Usage Trend")
        df_tokens = run_query("SELECT timestamp, tokens_in + tokens_out as total_tokens FROM agent_events ORDER BY timestamp")
        if not df_tokens.empty:
            fig_tok = px.line(df_tokens, x='timestamp', y='total_tokens', title="Total Tokens per Event")
            st.plotly_chart(fig_tok, use_container_width=True)
        else:
            st.info("No token data.")

    # Data Table with Filters
    st.divider()
    st.subheader("Recent Events")
    
    # RESTORED FILTERS
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        agents_df = run_query("SELECT DISTINCT agent_id FROM agent_events")
        agents = agents_df['agent_id'].tolist() if not agents_df.empty else []
        selected_agent = st.selectbox("Filter by Agent", ["All"] + agents)

    # Date Range Filter
    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    with filter_col4:
        # Default to today
        end_date = st.date_input("End Date", value=pd.to_datetime("now"))

    # Search Filter
    search_term = st.text_input("Search (Input/Output)", placeholder="Enter keyword...")

    query = "SELECT * FROM agent_events WHERE 1=1"
    
    if selected_agent != "All":
        query += f" AND agent_id = '{selected_agent}'"
    
    query += f" AND timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'"
    
    if search_term:
        query += f" AND (input_data ILIKE '%{search_term}%' OR output_data ILIKE '%{search_term}%')"
        
    query += " ORDER BY timestamp DESC LIMIT 500"
    
    df_events = run_query(query)
    
    if not df_events.empty:
        display_cols = ['event_id', 'step_type', 'model', 'tokens_in', 'tokens_out', 'cost_usd', 'duration_ms', 'status', 'timestamp']
        st.dataframe(df_events[display_cols], use_container_width=True)
        
        # RESTORED EXPORT
        csv = df_events.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='agent_events.csv',
            mime='text/csv',
        )
    else:
        st.info("No events found matching criteria.")
        
    # RESTORED DETAIL VIEW
    st.subheader("Event Details")
    event_id = st.text_input("Enter Event ID to view details")
    if event_id:
        detail_df = run_query(f"SELECT * FROM agent_events WHERE event_id = '{event_id}'")
        if not detail_df.empty:
            event = detail_df.iloc[0]
            
            def safe_json_parse(data):
                if not isinstance(data, str) or not data.strip(): return None
                try: return json.loads(data)
                except: return None
            
            input_json = safe_json_parse(event['input_data'])
            output_json = safe_json_parse(event['output_data'])
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("### Input Prompt")
                if input_json: st.json(input_json)
                else: st.code(event['input_data'])
            with col_d2:
                st.markdown("### Output Response")
                if output_json: st.json(output_json)
                else: st.code(event['output_data'])
            
            st.markdown("### Metadata")
            st.json({k: event[k] for k in display_cols if k in event})


def show_playground():
    st.title("🧪 Enterprise Playground")
    st.markdown("""
    Test the enterprise features live: **PII Redaction**, **Budget Limits**, **Hallucination Guard**, and **Persistent Memory**.
    """)
    
    if not EnterpriseClient:
        st.error("Enterprise SDK not found. Please ensure the code is in the python path.")
        st.stop()

    # sidebar controls
    with st.sidebar:
        st.header("Settings")
        budget_limit = st.number_input("Budget Limit ($)", value=0.001, format="%.6f", step=0.0001)
        agent_id = st.text_input("Agent ID", value="streamlit_user")
        
        if st.button("Reset Budget"):
            BudgetManager().reset()
            BudgetManager().set_budget(budget_limit)
            st.success("Budget Reset!")

    # Initialize Client in Session State
    if "ent_client" not in st.session_state or st.session_state.agent_id != agent_id:
        st.session_state.ent_client = EnterpriseClient(agent_id=agent_id, budget_limit=budget_limit)
        st.session_state.agent_id = agent_id
    
    # Always update budget from input
    st.session_state.ent_client.budget.set_budget(budget_limit)

    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter message (try putting an email or phone number)..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            try:
                with st.status("Processing...", expanded=True) as status:
                    st.write("🔍 Checking PII...")
                    time.sleep(0.5) # Fake delay for visual effect
                    
                    st.write("💰 Checking Budget...")
                    current_cost = st.session_state.ent_client.budget.get_status()['current_cost']
                    st.write(f"   (Current: ${current_cost:.6f})")
                    
                    st.write("🤖 Calling LLM...")
                    # Tracing enabled in client.py!
                    result_dict = st.session_state.ent_client.chat(prompt)
                    response = result_dict["response"]
                    
                    st.write("✅ Validating Response...")
                    status.update(label="Complete!", state="complete", expanded=False)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except BudgetExceededError as e:
                st.error(f"⛔ **Budget Exceeded**: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Live Metrics
    st.divider()
    metrics_col1, metrics_col2 = st.columns(2)
    
    status = st.session_state.ent_client.budget.get_status()
    usage_pct = (status['current_cost'] / status['limit']) if status['limit'] > 0 else 0
    
    with metrics_col1:
        st.caption("Budget Usage")
        st.progress(min(usage_pct, 1.0))
        st.text(f"${status['current_cost']:.6f} / ${status['limit']:.6f}")
    
    with metrics_col2:
        st.caption("Context Size")
        ctx_len = len(st.session_state.ent_client.context.get_context(100))
        st.metric("Messages in Memory", ctx_len)

# --- MAIN NAVIGATION ---

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Playground"])

if page == "Dashboard":
    show_dashboard()
else:
    show_playground()
