# Suck My Sol

Automated Solana wallet sweeper that periodically transfers all SOL and a chosen SPL-token from a hot wallet to a cold wallet.

---

## ✨ Features

* Monitors the wallet every *n* seconds (default **5 s**) and automatically sweeps:
  * Native SOL balance – keeps the minimum lamports required for fees.
  * A specific SPL token (configurable via env variable).
* Writes detailed logs to `solana_transfers.log` *and* to STDOUT.
* Ready-to-deploy on [Railway](https://railway.app) with **zero extra config** (Nixpacks build + `Procfile`).

---

## ⚙️ Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.11.x  |
| pip         | ≥ 23    |

> You do **not** need the Solana CLI; everything is done via RPC.

---

## 🏗️ Local setup

```bash
# 1. Clone the repo
$ git clone https://github.com/oneandzeros-co/suck-my-sol.git
$ cd suck-my-sol

# 2. (Optional) create a virtualenv
$ python3 -m venv .venv
$ source .venv/bin/activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Create a .env file with at least your private key
$ cp .env.example .env   # see below for variables
$ nano .env

# 5. Run the sweeper
$ python send_solana_funds.py
```

### .env example

```dotenv
# Base-58 encoded 64-byte private key (NOT the mnemonic!)
SOLANA_PRIVATE_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# The wallet that receives all swept funds (cold wallet)
DESTINATION_ADDRESS="DestinationWalletPubkeyHere"

# SPL token mint that should be swept (leave empty to disable)
SPL_TOKEN_ADDRESS="CwbpyHPZJ133hgWQvd1hZA4ZxjQu3mL7WRxEhmqQYkCB"

# Optional – interval in seconds between scans (default 5)
SCAN_INTERVAL=10
```

---

## 🚀 Deploying to Railway (recommended)

1. Click **"Deploy from Repo"** in Railway and select this GitHub repository.
2. Railway automatically detects Python via Nixpacks, installs `requirements.txt`, and uses the `Procfile`:
   ```
   start: python send_solana_funds.py
   ```
3. In the Railway **Variables** tab add at least `SOLANA_PRIVATE_KEY` (and optionally `SCAN_INTERVAL`).
4. In the Railway **Variables** tab add:
   * `SOLANA_PRIVATE_KEY` – your hot-wallet private key
   * `DESTINATION_ADDRESS` – the cold-wallet address that will receive funds
   * `SPL_TOKEN_ADDRESS` – the SPL-token mint to sweep (optional)
   * (optional) `SCAN_INTERVAL` – override the 5-second default
5. Hit **Deploy** – your worker starts immediately and restarts on crash/redeploy.

That's it! 🎉

---

## 📝 Customisation

All behaviour is now controlled via environment variables – **no code edits required**:

| Variable | Purpose |
|----------|---------|
| `DESTINATION_ADDRESS` | The cold-wallet that will receive the SOL + tokens. |
| `SPL_TOKEN_ADDRESS`   | The SPL token mint to sweep alongside SOL. |
| `SCAN_INTERVAL`       | Seconds between balance scans (optional, default 5). |

Simply change the values in your `.env` (or Railway "Variables" tab) and restart the worker.

---

## 🗒️ Logs

Logs are written both to:

* `solana_transfers.log` (rotates via your process manager)
* STDOUT – useful for Railway/Heroku log dashboards.

---

## ❗ Security disclaimer

This script **moves ALL FUNDS** out of the private key you provide. Treat it as a hot wallet:

* Never commit real keys to Git.
* Use a dedicated key with only the funds you intend to sweep.
* Review the code before deploying.

---

## 📄 License

MIT © 2024 Your Name 