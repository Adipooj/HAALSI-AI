# HAALSI AI — Free Online Hosting Guide

This guide explains how to host both the **Frontend** and **Backend** of HAALSI AI completely for free using modern cloud platforms.

---

## 1. Hosting Architecture Overview

Because HAALSI AI is a decoupled full-stack application (Python FastAPI Backend + React/TypeScript Frontend), the best practice for free hosting is:

- **Frontend:** Hosted for free on **Vercel** or **Netlify** (Global CDN, instant SSL, zero cold starts).
- **Backend:** Hosted for free on **Render** (render.com) or **Koyeb** (Dockerized or Python Web Service).

---

## 2. Step-by-Step Free Deployment

### Step A: Push Code to GitHub
1. Create a GitHub repository (e.g. `haalsi-ai`).
2. Initialize git and commit:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: HAALSI AI production release"
   git remote add origin https://github.com/<your-username>/haalsi-ai.git
   git branch -M main
   git push -u origin main
   ```

---

### Step B: Deploy Backend to Render (Free Tier)
1. Go to [Render.com](https://render.com) and sign up with GitHub.
2. Click **New +** $\to$ **Web Service**.
3. Select your GitHub repository.
4. Configure the service:
   - **Name:** `haalsi-ai-backend`
   - **Environment:** `Python 3`
   - **Root Directory:** Leave blank (or `.`)
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy aiosqlite greenlet "bcrypt<4.1.0" passlib python-jose email-validator && python -m backend.app.db.seed
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free` (512 MB RAM)
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: `your_random_secure_jwt_secret_here`
   - `DEPLOYMENT_MODE`: `clinical_evaluation`
6. Click **Deploy Web Service**.
7. Once deployed, Render will provide a public HTTPS URL (e.g. `https://haalsi-ai-backend.onrender.com`).

---

### Step C: Deploy Frontend to Vercel (Free Tier)
1. Go to [Vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** $\to$ **Project**.
3. Import your GitHub repository.
4. In the project settings:
   - **Root Directory:** Click edit and select `frontend`.
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Under **Environment Variables**, add:
   - `VITE_API_URL`: `https://haalsi-ai-backend.onrender.com/api/v1` (replace with your Render backend URL).
6. Click **Deploy**.
7. Vercel will build and launch your application at a free `.vercel.app` address with automatic HTTPS.

---

## 3. Alternative: Single-Container Deployment (Hugging Face Spaces)
If you prefer hosting both frontend and backend together on a single free GPU/CPU instance:
1. Create a **Docker Space** on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Push your `docker-compose.yml` or root `Dockerfile`.
3. Hugging Face provides persistent 16 GB RAM CPU instances completely free for research and clinical AI demonstrations.
