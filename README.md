# AI-Based Smart Complaint Management System 🚀

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-based-smart-complaint-management-system-8wqmt2hcjh7km8mhkpa.streamlit.app/)

An automated system designed for companies and institutes to handle thousands of customer complaints efficiently using AI and Data Science.

## 🌐 Live Demo
**[View Live Application →](https://ai-based-smart-complaint-management-system-8wqmt2hcjh7km8mhkpa.streamlit.app/)**

## 🌟 Key Features

### 👤 Customer Portal
- **Smart Submission**: Submit complaints with automated categorization and prioritization.
- **AI-Powered**: Automatically detects Category (Technical, Billing, Delivery, General) and predicts Priority.
- **Multilingual Support**: Supports both English and **Roman Urdu** (e.g., "Mera internet slow hai").
- **Bulk Upload**: Upload complaints via **CSV** or **PDF** files for batch processing.
- **Real-time Tracking**: Check the status of your complaint instantly using a unique **Tracking ID**.

### 📊 Admin Dashboard
- **Secure Authentication**: Protected login for administrators.
- **Complaint Management**: Filter, search, and update the status of complaints (Pending → In Progress → Resolved).
- **Advanced Analytics**:
  - Monthly complaint trends.
  - Priority and Category distribution charts.
  - Department-wise workload analysis.
- **Data Export**: Export all complaint data to CSV for offline reporting.

## 🛠️ Technology Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **AI/NLP**: Scikit-Learn (TF-IDF + Logistic Regression)
- **Database**: SQLite
- **Visualization**: Pandas, Matplotlib, Seaborn

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/AbdurrehmanArif/AI-Based-Smart-Complaint-Management-System.git
cd AI-Based-Smart-Complaint-Management-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

## 🔐 Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 📁 Project Structure
- `app.py`: Main Streamlit application.
- `models/`: AI model training and prediction logic.
- `database/`: SQLite database management script.
- `utils/`: Email service and utility functions.
- `requirements.txt`: List of required Python libraries.

## 📧 Notifications
The system includes an automated email notification utility (`utils/email_service.py`) that can be configured with your SMTP credentials to send updates to customers on submission and status changes.

---
Built by [Abdurrehman Arif](https://github.com/AbdurrehmanArif)
