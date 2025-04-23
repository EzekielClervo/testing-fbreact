# Facebook Reaction Tool

A web-based Facebook reaction automation tool with user authentication, admin panel, and deployment configuration for Render.

## Features

- User authentication (register/login)
- Admin dashboard to manage users and tokens
- Post reaction automation
- Comment reaction automation 
- Dark purple UI design

## Admin Credentials

- Username: david143
- Password: david1433

## Deployment Instructions for Render

### Option 1: Manual Deployment

1. Create a new account on [Render](https://render.com/) if you don't have one
2. Create a new PostgreSQL database on Render
   - Go to "New+" → "PostgreSQL"
   - Name your database (e.g., fb-react-db)
   - Choose a region closest to your users
   - Select the Free plan
   - Click "Create Database"
   - Keep note of the Internal Database URL

3. Create a new Web Service on Render
   - Go to "New+" → "Web Service"
   - Connect to your GitHub repository
   - Name: facebook-reaction-tool
   - Region: Choose closest to your users
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`
   
4. Set up Environment Variables
   - Add the following environment variables:
     - `DATABASE_URL`: Your PostgreSQL database connection string from step 2
     - `SESSION_SECRET`: A random string for session security (can be generated)

5. Deploy your service
   - Click "Create Web Service"
   - Wait for the deployment to complete

### Option 2: Blueprint Deployment (Recommended)

1. Push your code to GitHub
2. Log in to Render and create a new Blueprint instance
   - Go to "New+" → "Blueprint"
   - Connect to your GitHub repository
   - Render will automatically detect the render.yaml file and set up the services

3. Confirm the deployment
   - Review the proposed resources
   - Click "Apply" to start the deployment

### Option 3: Using an Existing Database (Free Tier Workaround)

If you already have a free tier PostgreSQL database on Render and can't create another one:

1. Get your existing database connection URL from Render dashboard
2. Edit the render.yaml file in your repository:
   - Remove the database section completely
   - Update the DATABASE_URL environment variable to use your existing database

3. When deploying, you'll need to:
   - Create a new schema in your existing database for this application
   - Set the DATABASE_URL environment variable to include the schema in the connection string

## Local Development

1. Set up environment variables:
   - `DATABASE_URL`: Connection string for your local database
   - `SESSION_SECRET`: Any random string

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## License

This project is proprietary.