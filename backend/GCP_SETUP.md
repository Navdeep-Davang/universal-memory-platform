# GCP Infrastructure Setup Guide

This guide provides the necessary steps to set up the GCP infrastructure for the Universal Cognitive Memory Engine.

## 1. Initial Setup

Ensure you have the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and initialized.

```bash
# Login to GCP
gcloud auth login

# Set your project ID
gcloud config set project [YOUR_PROJECT_ID]
```

## 2. Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    compute.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com
```

## 3. Create Artifact Registry Repository

This repository will store your backend Docker images.

```bash
gcloud artifacts repositories create memory-engine-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Memory Engine"
```

## 4. Backend Deployment (Cloud Run)

### A. Prepare Environment
Create a `secrets.env` file (locally) with your production keys (OpenAI, etc.). Do NOT commit this file.

### B. Build and Push Image
From the `backend/` directory:

```bash
# Tag and push using Cloud Build (simplest method)
gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/memory-engine-repo/backend:latest .
```

### C. Deploy to Cloud Run
```bash
gcloud run deploy memory-engine-backend \
    --image us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/memory-engine-repo/backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --env-vars-file secrets.env
```

## 5. Database Strategy (Development Phase)

### Option A: Memgraph Cloud (Recommended)
1. Sign up at [Memgraph Cloud](https://memgraph.com/cloud).
2. Create a free instance.
3. Update your `REDIS_URL` and `MEMGRAPH_HOST` in Cloud Run env vars to point to the Memgraph Cloud credentials.

### Option B: Redis (GCP Memorystore)
For production, use GCP Memorystore for Redis.
```bash
gcloud redis instances create memory-cache --size=1 --region=us-central1
```

## 6. Frontend Deployment
You can deploy the Next.js frontend to **Vercel** or **Firebase Hosting**.
Ensure the `NEXT_PUBLIC_API_URL` points to your Cloud Run service URL.
