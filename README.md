# Suck My Sol

Automated Solana wallet sweeper that periodically transfers all SOL and a chosen SPL-token from a hot wallet to a cold wallet.

---

## ✨ Features

* Monitors the wallet every *n* seconds (default **5 s**) and automatically sweeps:
  * Native SOL balance – keeps the minimum lamports required for fees.
  * A specific SPL token (configurable in the code).
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
4. Hit **Deploy** – your worker starts immediately and restarts on crash/redeploy.

That's it! 🎉

---

## 📝 Customisation

* **Destination address** – edit `destination_address` in `send_solana_funds.py`.
* **SPL token mint** – edit `spl_token_address` in the same file.
* **Gas reserve** – tweak `min_sol_keep`. Currently set to keep 0.000005 SOL.

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