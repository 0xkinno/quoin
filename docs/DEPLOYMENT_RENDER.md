# Deploying QUOIN to Render

This guide provides the complete, production-ready setup steps to deploy QUOIN on [Render](https://render.com).

QUOIN consists of two services:
1. **Backend Service (`quoin-api`)**: FastAPI deterministic authority fence service (Python 3.11).
2. **Frontend Service (`quoin-web`)**: Next.js 14 editorial web application with Replay design aesthetic.

---

## Option 1: Automatic Blueprint Deployment (Recommended)

QUOIN includes a verified `render.yaml` infrastructure-as-code blueprint that provisions both services automatically with service discovery.

### Steps:
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository (`https://github.com/0xkinno/quoin`).
4. Render automatically parses `render.yaml` and configures `quoin-api` and `quoin-web`.
5. Click **Apply**.
6. Render will provision both services and link `NEXT_PUBLIC_API_URL` on the frontend directly to the internal host of `quoin-api`.

---

## Option 2: Manual Service Deployment

If you prefer to deploy services individually via the Render dashboard:

### Step 1: Deploy Backend API (`quoin-api`)
1. Click **New +** -> **Web Service**.
2. Connect repository `https://github.com/0xkinno/quoin`.
3. Configure settings:
   - **Name**: `quoin-api`
   - **Region**: `Oregon (US West)` or `Ohio (US East)` (match your AWS region if using live AWS)
   - **Branch**: `main`
   - **Root Directory**: *(leave blank — repository root)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r apps/api/requirements.txt`
   - **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `CORS_ORIGINS`: `*`
   - `QUOIN_MODE`: `local` *(or `agentcore` if using live AWS)*
   - *(Optional for Live AWS integration)*:
     - `AWS_REGION`: `us-east-1`
     - `AWS_ACCESS_KEY_ID`: `<your-aws-key>`
     - `AWS_SECRET_ACCESS_KEY`: `<your-aws-secret>`
     - `BEDROCK_MODEL_ID`: `us.amazon.nova-lite-v1:0`
     - `DYNAMODB_TABLE_NAME`: `quoin_authority_ledger`
     - `AGENTCORE_MEMORY_ID`: `<your-memory-id>`
5. Click **Create Web Service**.
6. Once deployed, copy your backend public URL (e.g. `https://quoin-api.onrender.com`).

---

### Step 2: Deploy Frontend Interface (`quoin-web`)
1. Click **New +** -> **Web Service**.
2. Connect repository `https://github.com/0xkinno/quoin`.
3. Configure settings:
   - **Name**: `quoin-web`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `apps/web`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start -- -p $PORT`
4. In **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: `https://quoin-api.onrender.com` *(use your actual backend URL from Step 1)*
   - `NODE_VERSION`: `18.20.0` or `20.x`
5. Click **Create Web Service**.

---

## Verification & Health Check Commands

Once deployment completes, test the live services from your local terminal:

```bash
# 1. Test Backend API Health
curl -s https://quoin-api.onrender.com/api/health

# Expected JSON response:
# {
#   "status": "HEALTHY",
#   "service": "quoin-backend",
#   "version": "1.0.0",
#   "authority_ledger": "sqlite_wal_durable",
#   "planes_active": [...]
# }

# 2. Test Live Policy Precondition Evaluation
curl -X POST https://quoin-api.onrender.com/api/requests/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"test_req_001\",\"amount\":500,\"tenant_id\":\"agency_operations\"}"

# 3. Test Frontend Service Status
curl -I https://quoin-web.onrender.com
# HTTP/2 200 OK
```
