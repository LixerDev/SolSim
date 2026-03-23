# 🚀 SolSim

  A paper trading simulator for meme coins on the Solana blockchain. Practice trading without risking real assets.

  **Built by LixerDev**

  ![Version](https://img.shields.io/badge/version-1.0.0-blue)
  ![Python](https://img.shields.io/badge/python-3.13-green)
  ![Streamlit](https://img.shields.io/badge/streamlit-1.41.1-red)

  ## 📋 Table of Contents
  - [Features](#-features)
  - [API Key Setup](#-api-key-setup)
  - [Quick Start](#-quick-start)
  - [Installation](#️-installation)
  - [Troubleshooting](#️-troubleshooting)
  - [Dependencies](#-dependencies)
  - [License](#-license)

  ## 🚀 Features
  - Paper trade tokens with real-time data
  - Real-time token price tracking
  - Portfolio management with P/L tracking
  - Trade history with CSV export
  - Customizable trading fees
  - Docker support

  ## 🔑 API Key Setup
  1. Sign up at [BitQuery](https://account.bitquery.io/auth/signup)
  2. In BitQuery dashboard, navigate to 'Account' > 'Applications'
  3. Click on 'New Application'
  4. Enter any name (e.g. 'SolSim') and select an access token lifespan (Recommended: 3 months)
  5. Navigate to 'Access Tokens'
  6. Select the application and click 'Generate Access Token'
  7. Copy and paste your 'Access token' in the settings page of the app

  ## ⚡ Quick Start
  1. Clone the repository and install dependencies
  2. Navigate to `http://localhost:8501` in your browser
  3. Create a database and add your BitQuery API key in settings
  4. Start paper trading!

  ## 🛠️ Installation

  ### Option 1: Python (Local)
  ```bash
  git clone https://github.com/LixerDev/SolSim.git
  cd SolSim
  pip install -r requirements.txt
  python run.py
  ```

  ### Option 2: Docker (Simple)
  ```bash
  docker build -t solsim .
  docker run -p 8501:8501 solsim
  ```

  ### Option 3: Docker (Advanced)
  ```bash
  docker run -d -p 8501:8501 --name solsim --restart unless-stopped solsim
  ```

  ## 🛠️ Troubleshooting
  - **API errors**: Make sure your BitQuery API key is valid and has not expired
  - **Database errors**: Delete `trades.ddb` and create a new one in Settings
  - **Token not found**: The token may not have enough trading activity on-chain

  ## 📦 Dependencies
  - streamlit
  - pandas
  - duckdb
  - pyyaml
  - streamlit-extras

  ## 📄 License
  MIT License — see [LICENSE](LICENSE) for details.
  