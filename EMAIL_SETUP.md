# 📧 Email Setup Guide

Follow these steps to enable email notifications:

## Step 1: Create Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Enable **2-Step Verification** if not already enabled
4. Scroll down to **App passwords**
5. Click **App passwords**
6. Select app: **Mail**
7. Select device: **Other (Custom name)**
8. Enter name: **Complaint Management System**
9. Click **Generate**
10. **Copy the 16-digit password** (it will look like: `abcd efgh ijkl mnop`)

## Step 2: Create .env File

1. In your project folder, create a file named `.env` (no extension)
2. Copy the content from `.env.example`
3. Replace with your actual credentials:

```
SENDER_EMAIL=your-actual-email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
```

**Important:** Remove spaces from the app password!

## Step 3: Test Email

1. Restart your Streamlit app
2. Submit a test complaint
3. Check the terminal for email status messages:
   - ✅ Success: "Email sent successfully"
   - ❌ Error: Check the error message

## Troubleshooting

**"Email not configured" message:**
- Make sure `.env` file exists in the project root
- Check that credentials are correct (no quotes, no spaces)

**"Authentication failed" error:**
- Verify 2-Step Verification is enabled
- Generate a new App Password
- Make sure you're using the App Password, not your regular Gmail password

**"Connection refused" error:**
- Check your internet connection
- Gmail might be blocking the connection - try again later

## Security Note

- Never commit `.env` file to GitHub
- `.env` is already in `.gitignore`
- Only share `.env.example` as a template
