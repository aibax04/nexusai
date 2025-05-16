# NEXUS Backend

This repository contains the backend code for NEXUS, a chat application with AI, contact form, and newsletter functionality.

## Features

- AI-powered chat assistant for technology questions
- Contact form that sends messages to your Gmail
- Newsletter subscription system
- User authentication (login/register)

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Copy `sample.env` to `.env`
   - Update the values in `.env` with your credentials

### Setting Up Gmail for Email Functionality

To enable both the newsletter subscription and contact form features that send emails to your Gmail account:

1. Create an App Password for your Gmail account:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" as the app and "Other" as the device (name it "NEXUS")
   - Copy the generated 16-character password

2. Update your `.env` file:
   ```
   EMAIL_USER=mohdaibad04@gmail.com
   EMAIL_PASSWORD=your_generated_app_password
   ```

3. Save the changes and restart the application

## Running the Application

```bash
python app.py
```

The application will be available at http://localhost:8080

## Message and Newsletter Features

- **Contact Form**: Users can send you direct messages through the contact form in the Contact section
- **Newsletter**: Users can subscribe to your newsletter in the footer section
- All messages and subscriptions are sent directly to your Gmail account (mohdaibad04@gmail.com) 