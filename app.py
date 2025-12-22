import streamlit as st
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import sys
import base64

PDF_SUPPORT = False
PDF_ERROR = ""
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError as e:
    PDF_ERROR = str(e)
    try:
        import pypdf
        PDF_SUPPORT = True
    except ImportError as e2:
        PDF_ERROR += f" | {str(e2)}"
from database.db_manager import add_complaint, get_all_complaints, update_complaint_status, authenticate_admin, init_db, get_complaint_by_id
from models.model_logic import predict_complaint
from utils.email_service import send_complaint_notification

# Initialize DB on start
init_db()

st.set_page_config(page_title="Complaint Tracker", layout="wide")

LOGO_PATH = "C:/Users/user/.gemini/antigravity/brain/e6d95019-77fa-4e58-8904-a8116d431a45/complaint_tracker_search_logo_1766371646848.png"

# Theme CSS is applied dynamically in main() based on sidebar selection

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

def render_header():
    """Renders the consistent app header with logo."""
    img_base64 = get_base64_image(LOGO_PATH)
    img_src = f"data:image/png;base64,{img_base64}" if img_base64 else ""
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            {f'<img src="{img_src}" alt="Logo" style="width: 120px; margin-bottom: 1rem;">' if img_base64 else ''}
            <h1 style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent; 
                       font-size: 3.5rem; 
                       font-weight: 800; 
                       margin-bottom: 0.5rem;">
                Complaint Tracker
            </h1>
            <p style="color: #64748b; font-size: 1.2rem;">Detailed Analysis & Quick Resolution</p>
        </div>
    """, unsafe_allow_html=True)

def customer_page():
    render_header()
    st.markdown("### 📩 Submit Your Complaint")
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
                send_complaint_notification(
                    customer_email=email,
                    tracking_id=tracking_id,
                    department=department,
                    status="received",
                    customer_name=name,
                    category=category,
                    priority=priority,
                    response_time=response_time,
                    customer_phone=phone,
                    city=city,
                    address=address,
                    complaint_text=complaint_text
                )
                
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

    st.divider()
    st.subheader("📁 Bulk Upload (CSV / PDF)")
    
    if not PDF_SUPPORT:
        st.warning(f"⚠️ PDF support is currently unavailable. Error: {PDF_ERROR}")
        st.info("Try running: `pip install pdfplumber pypdf` and restart.")
        
    with st.expander("📥 CSV Format Guide"):
        st.write("Ensure your CSV has a column for the complaint text. We will automatically look for columns named 'complaint', 'text', or simply use the first column.")
        st.code("complaint_text,name,email\nMy internet is slow,John,john@example.com")

    uploaded_file = st.file_uploader("Upload a file containing complaints", type=["csv", "pdf"] if PDF_SUPPORT else ["csv"])
    
    if uploaded_file is not None:
        bulk_data = []
        if uploaded_file.type == "text/csv":
            df_upload = pd.read_csv(uploaded_file)
            
            # Flexible column detection
            target_col = None
            for col in df_upload.columns:
                if 'complaint' in col.lower() or 'text' in col.lower():
                    target_col = col
                    break
            
            if target_col is None:
                target_col = df_upload.columns[0] # Default to first column
                st.warning(f"Could not find a 'complaint' or 'text' column. Using the first column: **{target_col}**")

            for idx, row in df_upload.iterrows():
                text = str(row[target_col])
                if not text.strip(): continue
                
                cust_name = row.get('name', row.get('customer_name', 'Bulk User'))
                cust_email = row.get('email', 'bulk@example.com')
                cust_phone = row.get('phone', 'N/A')
                cust_city = row.get('city', 'N/A')
                cust_address = row.get('address', 'N/A')
                bulk_data.append((text, cust_name, cust_email, cust_phone, cust_city, cust_address))
        
        elif uploaded_file.type == "application/pdf" and PDF_SUPPORT:
            try:
                full_text = ""
                # Try pdfplumber first
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                        for page in pdf.pages:
                            full_text += (page.extract_text() or "") + "\n"
                except ImportError:
                    # Fallback to pypdf
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
                    for page in reader.pages:
                        full_text += (page.extract_text() or "") + "\n"
                
                if full_text.strip():
                    bulk_data.append((full_text, "PDF User", "pdf@example.com", "N/A", "N/A", "N/A"))
                else:
                    st.error("Could not extract text from PDF.")
            except Exception as e:
                st.error(f"Error processing PDF: {e}")

        if bulk_data:
            if st.button(f"Process {len(bulk_data)} complaints"):
                progress_bar = st.progress(0)
                for i, (text, name, email, phone, city, address) in enumerate(bulk_data):
                    category, priority, department, response_time = predict_complaint(text)
                    tracking_id = str(uuid.uuid4())[:8].upper()
                    add_complaint(tracking_id, name, email, phone, city, address, text, category, priority, department)
                    progress_bar.progress((i + 1) / len(bulk_data))
                
                st.success(f"Successfully processed {len(bulk_data)} complaints from file!")
                st.rerun()

def track_complaint_page():
    render_header()
    st.markdown("### 🔍 Track Your Complaint")
    st.info("Enter your unique Tracking ID below to check the current status of your complaint.")
    
    track_id = st.text_input("Tracking ID", placeholder="e.g. ABC12345")
    
    if st.button("Check Status"):
        if track_id:
            track_df = get_complaint_by_id(track_id.strip().upper())
            if not track_df.empty:
                complaint = track_df.iloc[0]
                status = complaint['status']
                
                # Visual status indicator
                status_color = "#ff4b4b" if status == "Pending" else "#007bff" if status == "In Progress" else "#28a745"
                st.markdown(f"""
                    <div style="padding: 20px; border-radius: 10px; background-color: white; border-left: 10px solid {status_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: black;">
                        <h3 style="margin-top: 0; color: {status_color};">Complaint Status: {status}</h3>
                        <p><strong>Tracking ID:</strong> {complaint['tracking_id']}</p>
                        <p><strong>Submitted On:</strong> {complaint['created_at']}</p>
                        <p><strong>Department:</strong> {complaint['department']}</p>
                        <p><strong>Category:</strong> {complaint['category']} | <strong>Priority:</strong> {complaint['priority']}</p>
                        <hr>
                        <p><strong>Complaint Text:</strong><br>{complaint['complaint_text']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if status == "Resolved":
                    st.balloons()
            else:
                st.error("Tracking ID not found. Please check and try again.")
        else:
            st.warning("Please enter a Tracking ID.")

def admin_dashboard():
    render_header()
    st.markdown("### 📊 Admin Analytics & Management")
    
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
                    complaint_data = target_complaint.iloc[0]
                    send_complaint_notification(
                        customer_email=complaint_data['email'],
                        tracking_id=target_id,
                        department=complaint_data['department'],
                        status=new_status,
                        customer_name=complaint_data['customer_name'],
                        category=complaint_data['category'],
                        priority=complaint_data['priority']
                    )
                
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
    # Theme Configuration
    if 'theme' not in st.session_state:
        st.session_state.theme = 'Light Mode'
    
    # Sidebar Header
    st.sidebar.image(LOGO_PATH, width=120)
    st.sidebar.title("Complaint Tracker")
    st.sidebar.markdown("---")
    
    st.sidebar.title("🎨 Theme")
    theme = st.sidebar.radio("Select Mode", ["Light Mode", "Dark Mode"], 
                            index=0 if st.session_state.theme == 'Light Mode' else 1,
                            label_visibility="collapsed")
    st.session_state.theme = theme

    # Common Styles
    st.markdown("""
        <style>
        .priority-high { color: #dc3545; font-weight: bold; }
        .priority-medium { color: #ffc107; font-weight: bold; }
        .priority-low { color: #28a745; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # Apply Theme-Specific CSS
    if theme == "Dark Mode":
        st.markdown("""
            <style>
            /* ===== PROFESSIONAL DARK MODE ===== */
            
            /* Background & Container */
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
                color: #e2e8f0 !important;
            }
            
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
                border-right: 1px solid #334155 !important;
            }
            
            [data-testid="stHeader"] {
                background-color: rgba(15, 23, 42, 0.95) !important;
                backdrop-filter: blur(10px);
            }
            
            /* Typography */
            .stMarkdown, .stText, h1, h2, h3, p, label, .stMetric {
                color: #e2e8f0 !important;
            }
            
            h1, h2, h3 {
                color: #f1f5f9 !important;
                font-weight: 600 !important;
            }
            
            /* Complaint Cards */
            .complaint-card {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
                border-left: 4px solid #3b82f6 !important;
                color: #e2e8f0 !important;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .complaint-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 24px rgba(59, 130, 246, 0.2);
            }
            
            /* Input Fields */
            div[data-baseweb="input"] > div,
            div[data-baseweb="textarea"] > div {
                background-color: #1e293b !important;
                color: #e2e8f0 !important;
                border: 1px solid #475569 !important;
                border-radius: 8px;
            }
            
            input, textarea {
                color: #e2e8f0 !important;
            }
            
            input::placeholder, textarea::placeholder {
                color: #64748b !important;
            }
            
            /* Premium Buttons */
            button, .stButton > button, section[data-testid="stFileUploader"] label {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 8px;
                height: 3em;
                width: 100%;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            button:hover, .stButton > button:hover, section[data-testid="stFileUploader"] label:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                background-color: transparent !important;
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: #1e293b !important;
                color: #94a3b8 !important;
                border-radius: 8px 8px 0 0;
                padding: 12px 24px;
                border: none !important;
            }
            
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: #ffffff !important;
            }
            
            /* DataFrames */
            .stDataFrame {
                background-color: #1e293b !important;
                border-radius: 8px;
            }
            
            /* Metrics */
            [data-testid="stMetricValue"] {
                color: #f1f5f9 !important;
                font-weight: 600;
            }
            
            /* Info/Success/Error boxes */
            .stAlert {
                background-color: #1e293b !important;
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            /* ===== LIGHT MODE ===== */
            [data-testid="stAppViewContainer"] { 
                background-color: #f8fafc; 
            }
            
            .complaint-card { 
                padding: 1.5rem; 
                border-radius: 12px; 
                border-left: 4px solid #3b82f6; 
                background-color: white; 
                margin-bottom: 1rem; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .complaint-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
            }
            
            /* Premium Buttons */
            button, .stButton>button, section[data-testid="stFileUploader"] label {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: #ffffff !important;
                border-radius: 8px;
                height: 3em;
                width: 100%;
                border: none;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            button:hover, .stButton>button:hover, section[data-testid="stFileUploader"] label:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            }
            </style>
        """, unsafe_allow_html=True)

    st.sidebar.divider()
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Customer Portal", "Track Complaint", "Admin Login"])
    
    if choice == "Customer Portal":
        customer_page()
    elif choice == "Track Complaint":
        track_complaint_page()
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
