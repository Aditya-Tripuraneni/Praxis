# Praxis — Production Deployment Guide

**For:** First-time deployer
**Last updated:** 2026-03-19
**Time required:** ~2-3 hours (most of it waiting for accounts to verify)

---

## 0. What You Need to Know First

**Your application code almost doesn't change.** Production is the same code you've been running locally — the only difference is the environment variables. Your app reads `SUPABASE_URL`, `STRIPE_SECRET_KEY`, etc. from the environment. In dev, those point to your test Supabase project and Stripe test keys. In production, they point to a new Supabase project and Stripe live keys. That's it.

**The overall plan:**
1. Fix two small code issues (5 minutes)
2. Create a production Supabase project (new database, new keys)
3. Set up Stripe live mode (new keys, new products, new webhook)
4. Deploy to Render.com (push code, set env vars, done)
5. Verify everything works

**Can you test with fake cards in production?** No. Stripe's test card `4242 4242 4242 4242` only works with test mode API keys. In live mode, you must use a real card. You can immediately refund yourself — it costs nothing except a brief hold on your card.

**What if you break something?** You can't break anything permanently. If the deploy fails, Render shows you the error. If the database is wrong, you can re-run the SQL. If Stripe is misconfigured, you just update the webhook URL. There is no "point of no return."

**Should you test production settings on your current laptop first?** Yes — great instinct. Here's the plan:
1. Create the production Supabase project and Stripe live keys
2. Temporarily put those production values in your local `.env`
3. Run `docker compose up` and verify: signup, verify email, subscribe (with real card), generate test, download PDF
4. If everything works, you know the production config is correct
5. Switch your `.env` back to dev values
6. Deploy to Render with the production values
7. Transfer to the new laptop

---

## 1. Quick Fixes (Do Now, 5 Minutes)

### Fix 1: package-lock.json name (ALREADY DONE)

The `package-lock.json` has been updated to say `"name": "praxis-frontend"`. No action needed.

### Fix 2: CSP headers for Stripe

Your `frontend/nginx.conf` already has the correct Stripe CSP directives. One addition recommended by Stripe's latest docs — add `worker-src blob:` for Stripe.js web workers:

Open `frontend/nginx.conf` and find the `Content-Security-Policy` line. Add `worker-src blob: 'self';` to it. The full CSP should be:

```
default-src 'self'; script-src 'self' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data: https://*.stripe.com; font-src 'self' data:; connect-src 'self' https://*.supabase.co https://api.stripe.com; frame-src https://checkout.stripe.com https://js.stripe.com https://hooks.stripe.com; worker-src blob: 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';
```

Changes from current:
- Added `https://*.stripe.com` to `img-src` (Stripe loads card brand logos)
- Added `https://hooks.stripe.com` to `frame-src` (Stripe 3D Secure verification)
- Added `worker-src blob: 'self'` (Stripe.js uses web workers)

---

## 2. Create Production Supabase Project

### Step 1: Go to the Supabase Dashboard

Open your browser and go to: https://supabase.com/dashboard

Sign in with the same account you use for development.

### Step 2: Create a New Project

1. Click **"New project"** (green button, top-left area)
2. Select your organization (or the default one)
3. Fill in:
   - **Name:** `praxis-production` (or whatever you want — this is just a label)
   - **Database Password:** Generate a strong password. **Save this password somewhere safe** — you'll need it if you ever connect directly to the database. Use a password manager, not a sticky note.
   - **Region:** Pick the closest to your users. If you're in Canada, choose `ca-central-1` (Canada) or `us-east-1` (Virginia).
   - **Pricing Plan:** Free tier is fine to start (500 MB database, 50K auth users)
4. Click **"Create new project"**
5. Wait ~2 minutes for the project to provision

**Important:** This is a BRAND NEW database. It has NO tables, NO users, NO data. Your dev database data does NOT transfer here. That's correct — production starts fresh.

### Step 3: Find Your Production Keys

Once the project is ready:

1. Click **Settings** (gear icon, left sidebar)
2. Click **API** (under "Project Settings")
3. You'll see:
   - **Project URL** — looks like `https://xxxxx.supabase.co`. Copy this. This is your `SUPABASE_URL`.
   - **anon / public key** — starts with `eyJ...` (it's a JWT). Copy this. This is your `SUPABASE_ANON_KEY`.
   - **service_role key** — Click "Reveal" to see it. Starts with `eyJ...`. Copy this. This is your `SUPABASE_SERVICE_ROLE_KEY`.
     **This key is SECRET. Never expose it in frontend code or commit it to Git.**

4. For the JWT Secret:
   - Still in Settings, click **Auth** (under "Project Settings")
   - Scroll down or look for **JWT Signing Keys** section
   - Copy the JWT Secret. This is your `SUPABASE_JWT_SECRET`.

**Write all four values down in a safe place (password manager, NOT a text file on your desktop).**

### Step 4: Create the Database Tables

1. In the Supabase Dashboard, click **SQL Editor** (left sidebar, looks like a terminal icon)
2. Click **"New query"**
3. Paste this entire SQL block and click **"Run"**:

```sql
-- =============================================
-- Praxis Production Database Setup
-- Run this ONCE in a new Supabase project
-- =============================================

-- 1. Subscriptions table
CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT NOT NULL,
    stripe_subscription_id TEXT UNIQUE,
    plan TEXT NOT NULL DEFAULT 'student',
    status TEXT NOT NULL DEFAULT 'inactive',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own subscription" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- 2. User stats table
CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tests_generated INTEGER NOT NULL DEFAULT 0,
    questions_generated INTEGER NOT NULL DEFAULT 0,
    topic_counts JSONB NOT NULL DEFAULT '{}',
    streak_current INTEGER NOT NULL DEFAULT 0,
    streak_best INTEGER NOT NULL DEFAULT 0,
    last_practice_date DATE,
    last_test_duration INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own stats" ON user_stats
    FOR SELECT USING (auth.uid() = user_id);

-- 3. Saved tests table
CREATE TABLE saved_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    test_name TEXT NOT NULL,
    config JSONB NOT NULL,
    seed INTEGER NOT NULL,
    questions JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT saved_tests_name_length CHECK (char_length(test_name) BETWEEN 1 AND 100)
);

CREATE INDEX idx_saved_tests_user_id ON saved_tests(user_id);

ALTER TABLE saved_tests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own saved tests" ON saved_tests
    FOR SELECT USING (auth.uid() = user_id);
```

4. You should see "Success. No rows returned" — that means all three tables were created.
5. Click **Table Editor** (left sidebar) and verify you see: `subscriptions`, `user_stats`, `saved_tests`.

### Step 5: Configure Auth Settings

1. In Supabase Dashboard, click **Auth** (left sidebar) → **URL Configuration**
2. **Site URL:** Change this to your production domain. For now, if you don't have a domain yet, leave it as `http://localhost:3000` and update it later when you have a Render URL.
3. **Redirect URLs:** Add your production frontend URL (e.g., `https://praxis-frontend.onrender.com`). You can add multiple — add both your Render URL and a custom domain if you have one.

**Email:** Supabase's built-in email sender works for testing but is rate-limited and looks unprofessional (emails come from `noreply@mail.app.supabase.io`). For production, set up a custom SMTP provider. The cheapest option: **Resend** (free tier: 100 emails/day) or **AWS SES** (pennies per email). This is not urgent for launch — the built-in sender works, just with limits.

---

## 3. Set Up Stripe Live Mode

### Step 1: Activate Your Stripe Account

1. Go to https://dashboard.stripe.com
2. You'll see a banner or a toggle at the top that says **"Test mode"** / **"Live mode"**.
3. Before you can use live mode, Stripe needs to verify your identity. Click **Settings** → **Account details** (or look for "Activate your account" / "Complete your profile").
4. Fill in:
   - **Business type:** Individual / Sole proprietorship (if you're a student with no registered business)
   - **Personal details:** Legal name, date of birth, address
   - **Business details:** Description of what you sell ("Online math practice subscription platform")
   - **Banking info:** Your bank account for receiving payouts
5. Stripe may verify you instantly or take 1-2 business days.

### Step 2: Get Live Mode API Keys

1. Toggle to **"Live mode"** (the toggle at the top of the Stripe Dashboard)
2. Go to **Developers** → **API keys**
3. Copy:
   - **Publishable key** — starts with `pk_live_...`. This goes in your frontend `.env` as `VITE_STRIPE_PUBLISHABLE_KEY`.
   - **Secret key** — Click "Reveal live key". Starts with `sk_live_...`. This goes in your backend env as `STRIPE_SECRET_KEY`. **This key is SECRET.**

### Step 3: Create Products and Prices (Live Mode)

**Make sure you're in Live mode (not Test mode) when doing this.**

1. Go to **Product catalog** → **+ Add product**
2. Create the Student product:
   - **Name:** Praxis Student
   - **Price:** $5.00 CAD, Recurring, Monthly
   - Click **Add product**
   - Copy the **Price ID** (click the price row → starts with `price_live_...`). This is your `STRIPE_STUDENT_PRICE_ID`.
3. Create the Tutor product:
   - **Name:** Praxis Tutor
   - **Price:** $12.99 CAD, Recurring, Monthly
   - Click **Add product**
   - Copy the **Price ID**. This is your `STRIPE_TUTOR_PRICE_ID`.

### Step 4: Create the Production Webhook

1. Still in Live mode, go to **Developers** → **Webhooks**
2. Click **+ Add endpoint**
3. **Endpoint URL:** `https://your-backend-url.onrender.com/api/billing/webhook`
   (You won't have this URL yet — come back to this step after deploying to Render in Section 4. For now, you can skip and return.)
4. **Events to send:** Click "Select events" and check these:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Click **Add endpoint**
6. On the endpoint page, click **"Signing secret"** → **Reveal**. Copy this — it's your `STRIPE_WEBHOOK_SECRET`.
   **You can only reveal this once. If you lose it, you must delete the endpoint and create a new one.**

### About Test Cards in Live Mode

**Stripe's test card (4242...) does NOT work in live mode.** To test a real checkout:
1. Use your own real credit card
2. Complete the checkout (you'll be charged $5 or $12.99 CAD)
3. Immediately go to Stripe Dashboard → Payments → find the charge → click **Refund**
4. You get your money back within 5-10 business days

---

## 4. Choose and Set Up Hosting

### Recommendation: Render.com

Render is the simplest Docker hosting platform. Free tier works for launching. You deploy two services:
- **Backend:** Docker web service (runs your FastAPI container)
- **Frontend:** Static site (serves your Vite build via CDN)

### Step 1: Create a Render Account

1. Go to https://render.com
2. Sign up with GitHub (easiest — it'll connect to your repos)

### Step 2: Push Your Code to GitHub

If you haven't already:
1. Create a **private** repository on GitHub
2. Push your code (make sure `.env` is in `.gitignore` — NEVER push secrets)

### Step 3: Deploy the Backend

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `praxis-api`
   - **Region:** Same as your Supabase project (e.g., Oregon for us-west, Ohio for us-east)
   - **Branch:** `main`
   - **Root Directory:** `PROBLEMGENERATOR/backend`
   - **Runtime:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **Docker Build Target:** `production`
   - **Instance Type:** Free (or Starter at $7/mo to avoid cold starts)
4. Click **"Advanced"** → **"Add Environment Variable"** and add ALL of these:

```
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_ANON_KEY=eyJ...(your production anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJ...(your production service role key)
SUPABASE_JWT_SECRET=your-production-jwt-secret
STRIPE_SECRET_KEY=sk_live_...(your live secret key)
STRIPE_WEBHOOK_SECRET=whsec_...(your live webhook secret)
STRIPE_STUDENT_PRICE_ID=price_...(your live student price)
STRIPE_TUTOR_PRICE_ID=price_...(your live tutor price)
FRONTEND_URL=https://praxis-frontend.onrender.com
CORS_ORIGINS=["https://praxis-frontend.onrender.com"]
HIBP_ENABLED=true
LOG_LEVEL=info
TRUSTED_PROXY_COUNT=1
```

5. Click **"Create Web Service"**
6. Wait for the build (~3-5 minutes). When it says "Live", your backend is deployed.
7. Copy the backend URL (e.g., `https://praxis-api.onrender.com`). You'll need this for the frontend.

### Step 4: Deploy the Frontend

1. In Render, click **"New +"** → **"Static Site"**
2. Connect the same repository
3. Configure:
   - **Name:** `praxis-frontend`
   - **Root Directory:** `PROBLEMGENERATOR/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Add environment variables:

```
VITE_API_URL=https://praxis-api.onrender.com
VITE_SUPABASE_URL=https://your-prod-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...(your production anon key)
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...(your live publishable key)
```

5. Click **"Create Static Site"**
6. Wait for the build (~2-3 minutes).

### Step 5: Complete the Webhook Setup

Now that you have the backend URL:

1. Go back to Stripe Dashboard → Developers → Webhooks
2. If you skipped the webhook earlier, create it now with URL: `https://praxis-api.onrender.com/api/billing/webhook`
3. If you already created it, click the endpoint and update the URL.

### Step 6: Update Supabase Redirect URLs

1. Go to Supabase Dashboard → Auth → URL Configuration
2. Set **Site URL** to: `https://praxis-frontend.onrender.com`
3. Add to **Redirect URLs:** `https://praxis-frontend.onrender.com`

### Step 7: Update CORS and Frontend URL

If your Render URLs are different from what you set in env vars, update them in the Render dashboard (Service → Environment → edit the variables).

### About Cold Starts (Free Tier)

Render free tier spins down your backend after 15 minutes of inactivity. The first request after spin-down takes ~25-30 seconds. Options:
- **Accept it:** Fine for a student project. The loading spinner covers the wait.
- **Use a free pinger:** UptimeRobot (free, 50 monitors) can ping your `/api/health` endpoint every 5 minutes to keep it warm.
- **Upgrade:** Render Starter ($7/mo) eliminates cold starts.

---

## 5. Production Environment Variables Template

Save this as a reference. **Do NOT commit this file with real values.**

```env
# =============================================
# Praxis Production Environment Variables
# =============================================
# WHERE TO GET EACH VALUE:
#   Supabase: Dashboard > Settings > API
#   Stripe: Dashboard > Developers > API keys (LIVE MODE)
#   Render: Set these in the service's Environment tab
# =============================================

# --- Supabase (from: supabase.com/dashboard > your project > Settings > API) ---
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...(your production anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...(your production service role key, SECRET)
SUPABASE_JWT_SECRET=your-production-jwt-secret-string

# --- Stripe LIVE mode (from: dashboard.stripe.com > Developers > API keys) ---
STRIPE_SECRET_KEY=sk_live_...(SECRET, never expose)
STRIPE_WEBHOOK_SECRET=whsec_...(SECRET, from webhook endpoint config)
STRIPE_STUDENT_PRICE_ID=price_...(from Product catalog > Student product)
STRIPE_TUTOR_PRICE_ID=price_...(from Product catalog > Tutor product)

# --- Application ---
FRONTEND_URL=https://praxis-frontend.onrender.com
CORS_ORIGINS=["https://praxis-frontend.onrender.com"]
HIBP_ENABLED=true
LOG_LEVEL=info
TRUSTED_PROXY_COUNT=1

# --- Frontend env vars (set in Render Static Site, NOT in backend) ---
# VITE_API_URL=https://praxis-api.onrender.com
# VITE_SUPABASE_URL=https://your-prod-project.supabase.co
# VITE_SUPABASE_ANON_KEY=eyJ...(same anon key as above — this one is public/safe)
# VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...(publishable keys are safe for frontend)
```

---

## 6. Test Production Config Locally (Your Plan — Do This First)

Before deploying to Render, test the production config on your current laptop:

### Step 1: Back Up Your Dev .env

```bash
cd PROBLEMGENERATOR
cp .env .env.dev.backup
```

### Step 2: Replace with Production Values

Edit your root `.env` and your `frontend/.env` with the production Supabase + Stripe values from sections 2 and 3 above.

### Step 3: Run Docker

```bash
docker compose down -v
docker compose up --build
```

### Step 4: Test the Full Flow

1. Open `http://localhost:5173`
2. **Register** a new account (this creates a user in your PRODUCTION Supabase)
3. **Verify email** (check your email — it comes from Supabase's default sender)
4. **Subscribe** — pick Student or Tutor. This opens Stripe's LIVE checkout.
   Use your real credit card. You will be charged $5 or $12.99 CAD.
   **You can refund yourself immediately in Stripe Dashboard after testing.**
5. **Generate a test** — verify questions render with math
6. **Download PDF** — verify it generates
7. **Check Stripe Dashboard** — you should see the subscription in Live mode
8. **Check Supabase Dashboard** — you should see the user in the production project's Auth table, and a row in the `subscriptions` table

### Step 5: Restore Dev Config

```bash
cp .env.dev.backup .env
# Also restore frontend/.env to dev values
docker compose down -v
docker compose up --build
```

**If the production test worked, you know the config is correct. Deployment is just putting those same env vars on Render.**

---

## 7. Transferring to a New Laptop

### Your Zip-and-Email Plan: Works, But Watch Out for These

**What to include in the zip:**
- All source code (backend/, frontend/, docs/, specs/, etc.)
- docker-compose.yml, Makefile
- .env.example files (templates with placeholder values)
- This deployment guide

**What to EXCLUDE from the zip:**
- `node_modules/` — 200+ MB of packages. Regenerated by `npm install`.
- `__pycache__/` — Python cache. Regenerated automatically.
- `.venv/` — Python virtual environment. Regenerated by `pip install`.
- `backend/.env` — Contains your development secrets
- `frontend/.env` — Contains your dev Supabase/Stripe keys
- `.env` (root) — Contains your dev secrets
- Any `.env` file with real keys in it

**The safe way to handle secrets:**
1. Do NOT email yourself `.env` files with real API keys in them
2. Instead, save your production keys in a password manager (Bitwarden is free)
3. On the new laptop, create fresh `.env` files and paste the keys from your password manager

### Setting Up the New Laptop

1. **Install Docker Desktop** — https://www.docker.com/products/docker-desktop/
2. **Install Git** — https://git-scm.com/downloads (may already be installed)
3. **Unzip the project** to a folder like `~/Projects/Praxis/`
4. **Create your .env files** — copy from `.env.example` and fill in your dev or production values from your password manager
5. **Run it:**
   ```bash
   cd ~/Projects/Praxis/PROBLEMGENERATOR
   docker compose up --build
   ```
6. First build takes ~5 minutes (downloads Docker images, installs dependencies). Subsequent starts are fast.

### Better Alternative: Use Git

Instead of zip + email:

1. Create a **private** GitHub repository
2. Push your code (`.env` is already in `.gitignore`, so secrets won't be pushed)
3. On the new laptop: `git clone https://github.com/yourusername/praxis.git`
4. Create `.env` files from `.env.example`
5. `docker compose up --build`

This is better because:
- No giant zip file to email
- Version history preserved
- Easy to deploy to Render (it connects to GitHub directly)

---

## 8. Post-Launch Checklist

Run through this after your first production deploy:

- [ ] **Health check**: Visit `https://praxis-api.onrender.com/api/health` — should return `{"status": "ok"}`
- [ ] **Landing page**: Visit your frontend URL — Praxis logo, pricing cards, feature sections all render
- [ ] **Sign up**: Register with a real email — verification email arrives
- [ ] **Verify email**: Enter the OTP code — redirects to verified state
- [ ] **Subscribe (Student)**: Complete Stripe checkout with real card — subscription activates
- [ ] **Generate test**: Pick topics, difficulty, count — questions render with LaTeX math
- [ ] **Download PDF**: Click Download — PDF generates and downloads with questions + answers
- [ ] **Stats update**: Dashboard shows test count and question count incremented
- [ ] **Streak**: Dashboard shows 1-day streak after generating
- [ ] **Stripe Dashboard**: Live mode shows the subscription and payment
- [ ] **Supabase Dashboard**: Auth tab shows the user, subscriptions table shows the row
- [ ] **Refund yourself**: Stripe Dashboard → Payments → find the charge → Refund (get your money back)
- [ ] **Cancel test sub**: Stripe Dashboard → Subscriptions → Cancel immediately (clean up test data)
- [ ] **Monitor logs**: Check Render's Logs tab for the first 24 hours — look for errors

### If Something Doesn't Work

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Frontend loads but API calls fail | CORS misconfigured | Check `CORS_ORIGINS` matches your frontend URL exactly (including https://) |
| "Not authenticated" on all requests | Supabase JWT secret wrong | Verify `SUPABASE_JWT_SECRET` matches the production project |
| Stripe checkout fails | Wrong price ID or wrong mode | Make sure you're using live mode price IDs, not test mode |
| Webhook not received | Webhook URL wrong or not created | Check Stripe Dashboard → Webhooks → verify the URL is your production backend |
| Webhook returns 400 | Wrong webhook secret | Verify `STRIPE_WEBHOOK_SECRET` is the live mode secret, not the test mode one |
| Email verification doesn't arrive | Supabase email limit | Free tier has email rate limits. Check Supabase Dashboard → Auth → Users to see if the user was created |
| Cold start timeout | Render free tier spin-down | Normal — first request takes 25-30s. Set up UptimeRobot to prevent this |

---

## Quick Reference: Where Every Key Comes From

| Env Var | Where to Get It | Secret? |
|---------|----------------|---------|
| `SUPABASE_URL` | Supabase → Settings → API | No |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API | No (public) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Reveal | **YES** |
| `SUPABASE_JWT_SECRET` | Supabase → Settings → Auth → JWT | **YES** |
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys (Live) | **YES** |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Developers → Webhooks → Reveal | **YES** |
| `STRIPE_STUDENT_PRICE_ID` | Stripe → Product catalog → Student price | No |
| `STRIPE_TUTOR_PRICE_ID` | Stripe → Product catalog → Tutor price | No |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe → Developers → API keys (Live) | No (public) |
| `FRONTEND_URL` | Your Render static site URL | No |
| `CORS_ORIGINS` | Same as FRONTEND_URL, in array format | No |
