# Deployment Guide for Render (Free Tier)

Since Render Blueprints are not available on the free tier, you will need to create **3 separate Web Services** manually.

## Prerequisites
- A GitHub repository with this code pushed.
- A [Render](https://render.com) account.

## Step 1: Deploy Product 1 (Demand Forecasting)

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub repository.
4.  Configure the service:
    *   **Name**: `product-1-demand-forecasting` (or similar)
    *   **Root Directory**: `Product_1_Rental_Demand_Forecasting`
    *   **Environment**: `Python 3`
    *   **Region**: Singapore (or nearest to you)
    *   **Branch**: `main` (or your working branch)
    *   **Build Command**: `./render_build.sh`
    *   **Start Command**: `gunicorn api_server:app`
    *   **Plan**: Free
    *   **Environment Variables**:
        *   `PYTHON_VERSION`: `3.10.12`
5.  Click **Create Web Service**.
6.  **Wait** for the deployment to finish.
7.  **Copy the URL** (e.g., `https://product-1-demand-forecasting-xxxx.onrender.com`). You will need this for Product 3.

## Step 2: Deploy Product 2 (Gap Analysis)

1.  Go to Dashboard > **New +** > **Web Service**.
2.  Connect the **same repository**.
3.  Configure the service:
    *   **Name**: `product-2-gap-analysis`
    *   **Root Directory**: `Product_2_Demand_Supply_Gap_Identification`
    *   **Environment**: `Python 3`
    *   **Build Command**: `./render_build.sh`
    *   **Start Command**: `gunicorn api_server:app`
    *   **Plan**: Free
    *   **Environment Variables**:
        *   `PYTHON_VERSION`: `3.10.12`
4.  Click **Create Web Service**.
5.  **Wait** for deployment.
6.  **Copy the URL** (e.g., `https://product-2-gap-analysis-xxxx.onrender.com`). You will need this for Product 3.

## Step 3: Deploy Product 3 (Chatbot)

This service needs to know where Product 1 and 2 are located.

1.  Go to Dashboard > **New +** > **Web Service**.
2.  Connect the **same repository**.
3.  Configure the service:
    *   **Name**: `product-3-chatbot`
    *   **Root Directory**: `Product_3_Conversational_AI_Chatbot`
    *   **Environment**: `Python 3`
    *   **Build Command**: `./render_build.sh`
    *   **Start Command**: `gunicorn api_server:app`
    *   **Plan**: Free
4.  **Environment Variables**:
    Scroll down to the "Environment Variables" section and add these two:
    *   `DEMAND_API_URL`: Paste Product 1 URL (e.g., `https://product-1-xxxx.onrender.com`)
    *   `GAP_API_URL`: Paste Product 2 URL (e.g., `https://product-2-xxxx.onrender.com`)
    *   **CRITICAL**: Scroll up to "Environment Variables" and add:
        *   `PYTHON_VERSION`: `3.10.12`
        (This is required because your models were trained on older Python versions and may fail on the default Python 3.13)
5.  Click **Create Web Service**.

## Troubleshooting Build Errors
If you see an error like `Cannot import 'setuptools.build_meta'`, ensure you have added the `PYTHON_VERSION` environment variable as described above. The libraries used (pandas 1.5.3, etc.) are not fully compatible with the latest Python 3.13.

## Verification
Once all three are live:
*   Frontend developers can use the **Product 3 URL** to interact with the chatbot.
*   The chatbot will internally call Product 1 and Product 2 using the URLs you provided.

## Important Note for Free Tier
Free tier services spin down after 15 minutes of inactivity. When a new request comes in, it may take roughly **50 seconds** to spin back up. This is normal behavior for the free tier.
