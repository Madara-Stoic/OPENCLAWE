# OmniHealth Guardian

> Decentralized AI-IoT Medical Monitoring Platform for BNB Chain "Good Vibes Only" Hackathon

[![OpenClaw](https://img.shields.io/badge/AI%20Agent-OpenClaw-purple)](https://openclaw.ai)
[![opBNB](https://img.shields.io/badge/Blockchain-opBNB%20Testnet-yellow)](https://testnet.opbnbscan.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🏥 Overview

OmniHealth Guardian is a decentralized platform for real-time monitoring of critical medical IoT devices (insulin pumps, pacemakers, glucose monitors). It features:

- **3 User Dashboards**: Patient, Doctor, Organization
- **4 OpenClaw AI Skills**: Autonomous health monitoring agents
- **Blockchain Verification**: SHA-256 hashed alerts on opBNB
- **Smart Contract Wallets**: Account Abstraction for gas-free transactions

## 🎯 Features

### User Dashboards
| Role | Features |
|------|----------|
| **Patient** | Real-time vitals, AI diet plans, alert history, OpenClaw skills panel |
| **Doctor** | Live patient telemetry, alert logs, condition distribution charts |
| **Organization** | System analytics, device deployment, Moltbot activity feed |

### OpenClaw AI Skills
1. **Critical Condition Monitor** - Real-time vital monitoring with blockchain-verified alerts
2. **AI Diet Suggestion** - Personalized meal plans based on medical condition
3. **Real-time Feedback** - Instant coaching tips and trend analysis
4. **Daily Progress Tracker** - Health scores and daily recommendations

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React, Tailwind CSS, Shadcn UI, Recharts |
| Backend | FastAPI, Python 3.11 |
| Database | MongoDB |
| AI | OpenAI GPT-4o (via Emergent LLM Key) |
| Blockchain | opBNB Testnet (Chain ID: 5611) |
| Smart Contracts | Solidity 0.8.19 |

## 📦 Project Structure

```
/app
├── backend/
│   ├── server.py              # FastAPI main application
│   ├── openclaw_agent.py      # OpenClaw AI skills implementation
│   ├── deploy_contracts.py    # Smart contract deployment script
│   ├── contracts/             # Solidity smart contracts
│   │   ├── HealthAudit.sol
│   │   ├── SimplePaymaster.sol
│   │   └── PatientWalletFactory.sol
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard pages
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   └── context/          # Auth context
│   ├── package.json
│   └── .env
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js >= 18
- Python >= 3.10
- MongoDB
- opBNB Testnet BNB (for contract deployment)

### 1. Clone & Install

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
yarn install
```

### 2. Environment Variables

**Backend (.env)**
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="omnihealth"
EMERGENT_LLM_KEY=your_emergent_llm_key
DEPLOYER_PRIVATE_KEY=your_private_key  # For contract deployment
```

**Frontend (.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Run Development Servers

```bash
# Backend (port 8001)
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend (port 3000)
cd frontend
yarn start
```

### 4. Deploy Smart Contracts (Optional)

```bash
# Fund wallet first from https://www.l2faucet.com/opbnb
cd backend
export DEPLOYER_PRIVATE_KEY=your_funded_wallet_private_key
python deploy_contracts.py
```

## 📡 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Social auth login (creates smart wallet) |
| GET | `/api/patients` | List all patients |
| GET | `/api/telemetry/live` | Real-time device readings |
| GET | `/api/alerts` | Critical alerts with blockchain hashes |

### OpenClaw Skill Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/openclaw/skills` | List all 4 AI skills |
| POST | `/api/openclaw/skill/critical-monitor/{patient_id}` | Run critical monitor |
| POST | `/api/openclaw/skill/diet-suggestion/{patient_id}` | Generate diet plan |
| POST | `/api/openclaw/skill/realtime-feedback/{patient_id}` | Get real-time coaching |
| POST | `/api/openclaw/skill/daily-progress/{patient_id}` | Generate daily report |
| POST | `/api/openclaw/run-all/{patient_id}` | Execute all skills |

### Blockchain Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/blockchain/contracts` | Deployed contract info |
| GET | `/api/blockchain/wallet/{patient_id}` | Patient smart wallet |
| GET | `/api/blockchain/verify/{tx_hash}` | Verify transaction |

## 🔗 Smart Contracts

### HealthAudit.sol
Stores SHA-256 hashes of critical medical alerts on-chain.
```solidity
function recordAlert(bytes32 alertHash, address patient, string alertType) returns (uint256)
function verifyAlertHash(uint256 alertId, bytes32 hashToVerify) returns (bool)
```

### SimplePaymaster.sol
Sponsors gas fees for critical alert transactions (Account Abstraction).
```solidity
function sponsorGas(address user, uint256 gasAmount, string reason)
function whitelistCaller(address caller)
```

### PatientWalletFactory.sol
Creates smart contract wallets for patients.
```solidity
function createWallet(address patientEOA, address guardian) returns (address)
function getWallet(address patient) returns (address)
```

## ⚠️ What's Simulated vs Real

| Feature | Status | Notes |
|---------|--------|-------|
| Patient/Doctor/Org Dashboards | ✅ Real | Fully functional UI |
| OpenClaw AI Skills | ✅ Real | 4 working autonomous skills |
| AI Diet Suggestions | ✅ Real | OpenAI GPT-4o integration |
| Mock Patient Data | ✅ Real | 10 patients, 20 doctors, 30 hospitals |
| BNB Greenfield Storage | ✅ Implemented | Simulated mode, ready for real Greenfield |
| Blockchain TX Hashes | ⚠️ Simulated | Mock hashes until contracts deployed |
| Smart Contract Wallets | ⚠️ Simulated | Addresses generated, not on-chain |
| Account Abstraction Paymaster | ⚠️ Simulated | Contract ready, needs deployment |

## 🔐 Deployer Wallet

**Address:** `0xBbbd90a05650cE647889258251A861e479ca2e4f`

**Private Key:** `e6e3df99443d25570c88b91f8f3a26e2221f5b35b8c1b95d7cf526803e7538a4`

⚠️ This is a TESTNET wallet. Do not use on mainnet.

**Get Test BNB:**
- https://www.l2faucet.com/opbnb
- https://faucets.chain.link/opbnb-testnet

## 📋 Hackathon Submission Checklist

- [x] Working demo application
- [x] OpenClaw AI agent integration
- [x] 3 user dashboards (Patient, Doctor, Organization)
- [x] Blockchain verification with opBNB explorer links
- [ ] Deploy contracts on opBNB testnet
- [ ] Record 2-minute demo video
- [ ] Submit contract addresses

## 🔮 Future Enhancements

1. **Real Greenfield Bucket** - Create bucket on mainnet with proper credentials
2. **Real Account Abstraction** - Biconomy/Particle integration
3. **WebSocket Real-time** - Live skill execution streaming
4. **Push Notifications** - Critical alert notifications
5. **Multi-language Support** - i18n for global accessibility

## 📡 BNB Greenfield Storage

Medical records are stored on BNB Greenfield decentralized storage:

### Greenfield Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/greenfield/status` | Storage status and stats |
| POST | `/api/greenfield/store-alert?alert_id=xxx` | Store alert on Greenfield |
| POST | `/api/greenfield/store-diet/{patient_id}` | Store diet plan |
| POST | `/api/greenfield/store-progress/{patient_id}` | Store daily progress |
| POST | `/api/greenfield/store-all/{patient_id}` | Store all patient records |

### Enable Real Greenfield
```env
# In backend/.env
USE_REAL_GREENFIELD=true
```

### Greenfield CID Format
```
gf://omnihealth-medical-records/{bundle_name}/{patient_id}/{record_type}/{timestamp}.json
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [BNB Chain](https://www.bnbchain.org/) - Blockchain infrastructure
- [OpenClaw](https://openclaw.ai/) - AI agent framework
- [Emergent Labs](https://emergentagent.com/) - Development platform

---

**Built for BNB Chain "Good Vibes Only: OpenClaw Edition" Hackathon 2026**
