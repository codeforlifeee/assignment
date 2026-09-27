# End-to-End Deployment Guide 🚀

This document provides a highly detailed, step-by-step guide to deploying the complete EVE Healthcare backend architecture (FastAPI, Celery, PostgreSQL, and Redis) to the web using **Railway.app**. 

Railway is the optimal choice for this stack because it flawlessly supports stateful background workers (Celery) and managed databases (Redis/PostgreSQL) in a unified project canvas.

---

## 🏗️ Architecture Overview
To successfully deploy this application, you must run **4 separate components** simultaneously in the cloud:
1. **PostgreSQL Database**: The primary persistent storage for users, centres, and bookings.
2. **Redis Database**: The message broker for Celery background tasks, and the storage engine for API caching and Rate Limiting.
3. **Web API Service**: The FastAPI web server (managed by Uvicorn) that receives HTTP requests.
4. **Worker Service**: The Celery background processor that executes delayed webhook requests.

---

## 🛠️ Step 1: Provision the Infrastructure (Databases)

1. Go to [Railway.app](https://railway.app/) and log in with your GitHub account.
2. Click **New Project** -> **Provision PostgreSQL**.
   * *Wait a few seconds for the database block to appear on your project canvas and initialize.*
3. On the same canvas, click the **+ New** button in the top right corner.
4. Select **Provision Redis**.
   * *You now have your two core databases actively running in the cloud.*

---

## 🌐 Step 2: Deploy the Web API (FastAPI)

1. On your project canvas, click **+ New** -> **GitHub Repo**.
2. Select your repository: `codeforlifeee/assignment`.
3. Railway will immediately detect the `Procfile` in your repository and begin building the web service. Click on this new service block.
4. Go to the **Variables** tab for this Web Service.
5. You must link your databases and secrets to this service. Click **New Variable**:
   * **Name**: `DATABASE_URL` -> **Value**: Click the dropdown and select the auto-suggested reference (e.g., `${{Postgres.DATABASE_URL}}`).
   * **Name**: `REDIS_URL` -> **Value**: Click the dropdown and select the auto-suggested reference (e.g., `${{Redis.REDIS_URL}}`).
   * **Name**: `SECRET_KEY` -> **Value**: Enter a secure, random string (e.g., `my_super_secret_production_key_12345!`).
6. **Watch the Logs**: Go to the **Deployments** tab and click on the active deployment. You will see the logs automatically execute `alembic upgrade head` to build your database tables, followed by the Uvicorn server booting up successfully!

---

## ⚙️ Step 3: Deploy the Background Worker (Celery)

If you skip this step, simulating payments will fail because there will be no background process listening for the webhook triggers!

1. Go back to your main project canvas.
2. Click **+ New** -> **GitHub Repo**.
3. Select the **exact same** repository again: `codeforlifeee/assignment`. (Yes, you will have two identical blocks of your code on the canvas).
4. Click on this new (second) service block.
5. Go to the **Settings** tab.
6. Scroll down to the **Deploy** section. Find the **Start Command** input field and type exactly this:
   ```bash
   celery -A eve_health.celery_app.celery_app worker --loglevel=info
   ```
   *(This overrides the default `Procfile` behavior so this block becomes a dedicated Celery worker).*
7. Go to the **Variables** tab for this Worker Service and add the exact same database links:
   * **Name**: `DATABASE_URL` -> **Value**: Reference `${{Postgres.DATABASE_URL}}`.
   * **Name**: `REDIS_URL` -> **Value**: Reference `${{Redis.REDIS_URL}}`.
8. Railway will rebuild the service. Check the logs—you should see the iconic Celery ASCII logo indicating the worker is successfully connected to Redis!

---

## 🌍 Step 4: Expose to the Public Internet

By default, Railway services are private. You must generate a public URL for your Web API so users (and the webhook simulation) can reach it.

1. Click on your **Web API Service** block.
2. Go to the **Settings** tab.
3. Scroll down to the **Environment / Domains** section.
4. Click **Generate Domain**.
5. Railway will instantly assign a public HTTPS URL (e.g., `assignment-production.up.railway.app`).

---

## ✅ Step 5: Test the Live Production System

1. Click on your newly generated public URL.
2. Append `/docs` to the end of the URL (e.g., `https://assignment-production.up.railway.app/docs`).
3. You should see your fully interactive Swagger UI!
4. **Test the Flow**: 
   - Use the `/users/signup` endpoint to create an account.
   - Use `/users/login` to get your JWT token.
   - Click **Authorize** at the top of Swagger and paste your token.
   - Create a centre and a test.
   - Create a booking.
   - Trigger a payment. Watch your Celery logs in Railway—you will see the background worker pick up the task, delay for 2 seconds, and successfully fire the webhook!

### Congratulations! Your enterprise-grade API is fully deployed.
