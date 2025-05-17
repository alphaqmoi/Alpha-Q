# Deploying Alpha-Q to Vercel

This guide will help you deploy the Alpha-Q application to Vercel.

## Prerequisites

1. A Vercel account
2. Git installed on your machine
3. Supabase account and database (already set up)

## Deployment Steps

### 1. Fork or Clone the Repository

First, fork or clone this repository to your own GitHub account.

### 2. Set Up Environment Variables in Vercel

When deploying to Vercel, you'll need to set up the following environment variables:

- `SUPABASE_URL`: https://xxwrambzzwfmxqytoroh.supabase.co
- `SUPABASE_ANON_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4d3JhbWJ6endmbXhxeXRvcm9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwMDg3MzUsImV4cCI6MjA2MjU4NDczNX0.5Lhs8qnzbjQSSF_TH_ouamrWEmte6L3bb3_DRxpeRII
- `SUPABASE_SERVICE_ROLE_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4d3JhbWJ6endmbXhxeXRvcm9oIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzAwODczNSwiZXhwIjoyMDYyNTg0NzM1fQ.gTjSiNnCTtz4D6GrBFs3UTr-liUNdNuJ7IKtdP2KLro
- `JWT_SECRET`: 4hK0mlO2DRol5s/f2SlmjsXuDGHVtqM96RdrUfiLN62gec2guQj0Vzy380k/MYuqa/4NT+7jT2DOhmi62zFOCw==
- `SESSION_SECRET`: Generate a strong random secret key for session security

### 3. Deploy Using Vercel Dashboard

1. Log in to your Vercel account
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Framework Preset: Other
   - Build Command: Leave empty (Vercel will use the vercel.json configuration)
   - Output Directory: Leave empty
   - Install Command: pip install -r requirements.txt
5. Add the environment variables from step 2
6. Click "Deploy"

### 4. Alternative: Deploy from CLI

To deploy from the Vercel CLI:

1. Install Vercel CLI: `npm i -g vercel`
2. Log in to Vercel: `vercel login`
3. Navigate to your project directory
4. Run: `vercel --prod`

## Vercel.json Configuration

The project already includes a vercel.json file configured for Flask:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "PYTHONUNBUFFERED": "1",
    "FLASK_ENV": "production",
    "FLASK_APP": "main.py"
  }
}
```

## Post-Deployment

After deployment, your app will be available at `your-project-name.vercel.app`. You may want to:

1. Set up a custom domain
2. Configure additional security settings
3. Set up CI/CD for automatic deployments

## Troubleshooting

- If you encounter any issues with the deployment, check Vercel logs for detailed error messages
- Ensure all environment variables are correctly set
- Make sure the Supabase URL and API keys are correct
- Check that dependencies are properly specified

## Local Development

For local development, create a `.env` file at the root of your project with the environment variables listed above. This will allow you to run the application locally without hardcoding sensitive values.