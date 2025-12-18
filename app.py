import streamlit as st
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from database.db_manager import add_complaint, get_all_complaints, update_complaint_status, authenticate_admin, init_db
from models.model_logic import predict_complaint
from utils.email_service import send_complaint_notification

# Initialize DB on start
init_db()

st.set_page_config(page_title="Smart Complaint Management", layout="wide")

# CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .complaint-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        background-color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .priority-high { color: #dc3545; font-weight: bold; }
    .priority-medium { color: #ffc107; font-weight: bold; }
    .priority-low { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def customer_page():
    st.title("📩 Submit Your Complaint")
    st.info("Our AI will automatically categorize and prioritize your request.")
    
    with st.form("complaint_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        name = col_f1.text_input("Full Name", placeholder="e.g. John Doe")
        email = col_f2.text_input("Email Address", placeholder="e.g. john@example.com")
        
        col_f3, col_f4 = st.columns(2)
        phone = col_f3.text_input("Phone Number", placeholder="e.g. +92 300 1234567")
        city = col_f4.text_input("City", placeholder="e.g. Karachi")
        
        address = st.text_area("Full Address", placeholder="Enter your full address here...")
        complaint_text = st.text_area("Complaint Description", placeholder="Describe your issue here...")
        
        submitted = st.form_submit_button("Submit Complaint")
        
        if submitted:
            if name and email and phone and complaint_text:
                # AI Prediction
                category, priority, department, response_time = predict_complaint(complaint_text)
                tracking_id = str(uuid.uuid4())[:8].upper()
                
                # Save to DB
                add_complaint(tracking_id, name, email, phone, city, address, complaint_text, category, priority, department)
                
                # Send Notification (Simulated)
                send_complaint_notification(email, tracking_id, department)
                
                st.success(f"Complaint Submitted Successfully! Tracking ID: **{tracking_id}**")
                
                # Display Prediction Summary
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Category", category)
                col2.metric("Priority", priority)
                col3.metric("Department", department)
                col4.metric("Est. Response", response_time)
                
                st.info(f"An auto-response has been sent to **{email}**. Your request is forwarded to the **{department}** department. Estimated response time: **{response_time}**.")
            else:
                st.error("Please fill in all fields.")

def admin_dashboard():
    st.title("📊 Admin Analytics & Management")
    
    df = get_all_complaints()
    
    if df.empty:
        st.write("No complaints found.")
        return

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Manage Complaints", "Analytics"])
    
    with tab1:
        st.subheader("Key Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Complaints", len(df))
        c2.metric("Pending", len(df[df['status'] == 'Pending']))
        c3.metric("In Progress", len(df[df['status'] == 'In Progress']))
        c4.metric("Resolved", len(df[df['status'] == 'Resolved']))

        # Quick view cards
        st.markdown("### Recent Complaints")
        for idx, row in df.head(5).iterrows():
            p_class = f"priority-{row['priority'].lower()}"
            st.markdown(f"""
                <div class="complaint-card">
                    <strong>ID: {row['tracking_id']}</strong> | Status: {row['status']} <br>
                    Category: {row['category']} | Priority: <span class="{p_class}">{row['priority']}</span> <br>
                    <strong>Customer:</strong> {row['customer_name']} | <strong>Phone:</strong> {row['phone']} | <strong>City:</strong> {row['city']}<br>
                    <strong>Email:</strong> {row['email']} <br>
                    <strong>Address:</strong> {row['address']} <br>
                    <em>Text: {row['complaint_text']}</em>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Filter & Update Status")
        search_query = st.text_input("Search by Tracking ID or Name")
        status_filter = st.multiselect("Filter by Status", options=['Pending', 'In Progress', 'Resolved'], default=['Pending', 'In Progress'])
        
        filtered_df = df
        if search_query:
            filtered_df = df[df['tracking_id'].str.contains(search_query, case=False) | df['customer_name'].str.contains(search_query, case=False)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
        st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        st.subheader("Update Complaint Status")
        col_up1, col_up2 = st.columns(2)
        target_id = col_up1.text_input("Enter Tracking ID to update")
        new_status = col_up2.selectbox("New Status", ["In Progress", "Resolved"])
        
        if st.button("Update Status"):
            if target_id:
                update_complaint_status(target_id, new_status)
                
                # Fetch email for notification
                target_complaint = df[df['tracking_id'] == target_id]
                if not target_complaint.empty:
                    cust_email = target_complaint.iloc[0]['email']
                    send_complaint_notification(cust_email, target_id, "N/A", status=new_status)
                
                st.success(f"Status updated for {target_id} and customer notified.")
                st.rerun()

    with tab3:
        st.subheader("Data Visualizations")
        
        # Row 1: Category and Priority
        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            st.markdown("**Category Distribution**")
            fig1, ax1 = plt.subplots()
            df['category'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax1, colors=sns.color_palette('pastel'))
            st.pyplot(fig1)
            
        with col_vis2:
            st.markdown("**Priority Ratio**")
            fig2, ax2 = plt.subplots()
            sns.countplot(data=df, x='priority', palette='viridis', ax=ax2)
            st.pyplot(fig2)

        # Row 2: Department and Status
        st.divider()
        col_vis3, col_vis4 = st.columns(2)
        with col_vis3:
            st.markdown("**Department-wise Distribution**")
            fig3, ax3 = plt.subplots()
            df['department'].value_counts().plot(kind='bar', ax=ax3, color='#4A90E2')
            plt.xticks(rotation=45)
            st.pyplot(fig3)

        with col_vis4:
            st.markdown("**Status Breakdown**")
            fig4, ax4 = plt.subplots()
            df['status'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax4, colors=['#ff9999','#66b3ff','#99ff99'])
            st.pyplot(fig4)

        # Row 3: Complex Analytics
        st.divider()
        st.markdown("**Department vs Status (Resolution Progress)**")
        dept_status = df.groupby(['department', 'status']).size().unstack().fillna(0)
        fig5, ax5 = plt.subplots(figsize=(10, 5))
        dept_status.plot(kind='bar', stacked=True, ax=ax5, color=['#ff9999','#66b3ff','#99ff99'])
        plt.legend(title='Status')
        st.pyplot(fig5)
            
        st.divider()
        st.markdown("**Monthly Complaint Trend**")
        df['month'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m')
        trend = df.groupby('month').size()
        st.line_chart(trend)
        
        st.download_button(
            label="Download Complaints Data (CSV)",
            data=df.to_csv(index=False),
            file_name="complaints_report.csv",
            mime="text/csv"
        )

def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Customer Portal", "Admin Login"])
    
    if choice == "Customer Portal":
        customer_page()
    else:
        st.sidebar.divider()
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
            
        if not st.session_state['logged_in']:
            st.title("🔒 Admin Authentication")
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("Login"):
                if authenticate_admin(user, pw):
                    st.session_state['logged_in'] = True
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            if st.sidebar.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()
            admin_dashboard()

if __name__ == "__main__":
    main()
