# OmniHealth Guardian

<div align="center">

![OmniHealth Guardian](https://img.shields.io/badge/OmniHealth-Guardian-00D4AA?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwMEQ0QUEiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTIyIDEyaC00bC0zIDlMOSAzbC0zIDloLTQiLz48L3N2Zz4=)
![BNB Chain](https://img.shields.io/badge/BNB-Chain-F0B90B?style=for-the-badge&logo=binance)
![OpenClaw](https://img.shields.io/badge/Moltbot-OpenClaw-8B5CF6?style=for-the-badge)

**Decentralized AI-IoT Medical Monitoring Platform**

Real-time vital tracking • Blockchain-verified alerts • AI-powered health insights

[Live Demo](#) • [Documentation](#architecture) • [Deploy](#deployment)

</div>

---

## 🏥 Overview

OmniHealth Guardian is a decentralized platform for real-time monitoring of critical medical IoT devices like insulin pumps and pacemakers. It combines:

- **BNB Chain (opBNB)** for tamper-proof alert verification
- **BNB Greenfield** for decentralized medical record storage
- **Moltbot/OpenClaw** AI agent framework for autonomous health monitoring
- **Account Abstraction** for gas-free critical transactions

---

## ✨ Features

### 🔴 Real-Time Monitoring
- Continuous vital sign tracking (glucose, heart rate)
- Device battery monitoring
- Critical threshold detection

### 🤖 Moltbot AI Agent (OpenClaw-Compatible)
Four autonomous skills powered by the OpenClaw framework:

| Skill | Description |
|-------|-------------|
| 🚨 **Critical Condition Monitor** | Detects dangerous vitals, triggers blockchain verification |
| 🥗 **AI Diet Suggestion** | Personalized meal plans based on condition |
| 💬 **Real-time Feedback** | Immediate coaching and health tips |
| 📊 **Daily Progress Tracker** | Comprehensive daily health reports |

### ⛓️ Blockchain Integration
- SHA-256 hashing of all critical alerts
- On-chain verification on opBNB
- Immutable audit trail

### 💾 Decentralized Storage
- Medical records stored on BNB Greenfield
- Patient-controlled data access
- HIPAA-compliant architecture

### 👥 Multi-Role Dashboards
- **Patient**: Real-time vitals, AI diet plans, alert history
- **Doctor**: Patient trends, alert management, care coordination
- **Organization**: Device analytics, system health, compliance

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TailwindCSS, Shadcn/UI, Recharts |
| **Backend** | FastAPI (Python), Motor (async MongoDB) |
| **Database** | MongoDB |
| **AI Agent** | Moltbot Gateway (OpenClaw-compatible) |
| **Blockchain** | opBNB (Solidity smart contracts) |
| **Storage** | BNB Greenfield (NodeReal Bundle Service) |
| **Auth** | Account Abstraction (Smart Contract Wallets) |

---

## 📁 Project Structure

```
omnihealth-guardian/
├── backend/
│   ├── contracts/                 # Solidity smart contracts
│   │   ├── HealthAudit.sol       # Critical alert logging
│   │   ├── SimplePaymaster.sol   # Gas sponsorship
│   │   └── PatientWalletFactory.sol
│   ├── skills/                    # Moltbot SKILL.md files
│   │   ├── critical_monitor/
│   │   ├── diet_suggestion/
│   │   ├── realtime_feedback/
│   │   └── daily_progress/
│   ├── server.py                  # FastAPI application
│   ├── moltbot_gateway.py         # OpenClaw Gateway implementation
│   ├── greenfield_storage.py      # BNB Greenfield integration
│   ├── openclaw_agent.py          # Legacy agent (for reference)
│   ├── deploy_contracts.py        # Contract deployment script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/               # Shadcn components
│   │   │   ├── OpenClawSkillsPanel.jsx
│   │   │   └── DashboardLayout.jsx
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── PatientDashboard.jsx
│   │   │   ├── DoctorDashboard.jsx
│   │   │   └── OrganizationDashboard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── context/
│   │       └── AuthContext.js
│   └── package.json
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.9
- **MongoDB** >= 6.0
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/omnihealth-guardian.git
cd omnihealth-guardian
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=omnihealth_guardian
CORS_ORIGINS=*
EMERGENT_LLM_KEY=your-openai-api-key
USE_REAL_GREENFIELD=true
GREENFIELD_BUCKET_NAME=your-bucket-name
GREENFIELD_USE_MAINNET=true
EOF

# Start MongoDB (if not running)
mongod --dbpath /path/to/data

# Run the backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Create environment file
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

# Start development server
yarn start
```

### 4. Access the Application

Open http://localhost:3000 in your browser.

---

## ⛓️ Blockchain Setup (Optional)

### Deploy Smart Contracts to opBNB Testnet

1. **Get testnet tokens**
   - Visit: https://testnet.bnbchain.org/faucet-smart
   - Request tokens for your deployer wallet

2. **Configure deployment**
   ```bash
   cd backend
   
   # Add your private key to .env
   echo "DEPLOYER_PRIVATE_KEY=your-private-key" >> .env
   ```

3. **Deploy contracts**
   ```bash
   python deploy_contracts.py
   ```

4. **Update contract addresses**
   The script will output deployed addresses. Update `.env`:
   ```
   HEALTH_AUDIT_ADDRESS=0x...
   PAYMASTER_ADDRESS=0x...
   WALLET_FACTORY_ADDRESS=0x...
   ```

---

## 💾 BNB Greenfield Setup

### 1. Create a Bucket

1. Go to [DCellar](https://dcellar.io) (Mainnet) or [DCellar Testnet](https://testnet.dcellar.io)
2. Connect your wallet
3. Click "Create Bucket"
4. Name it (e.g., `omnihealth-records`)

### 2. Grant Bundler Permissions

The NodeReal Bundle Service needs write access:

1. Click on your bucket → Share/Manage Access
2. Add this address: `0x4605BFc98E0a5EA63D9D5a4a1Df549732a6963f3`
3. Grant **Editor/Writer** permission (not Viewer)
4. Confirm the transaction

### 3. Update Configuration

```bash
# In backend/.env
GREENFIELD_BUCKET_NAME=your-bucket-name
GREENFIELD_USE_MAINNET=true  # or false for testnet
```

---

## 🔌 API Reference

### Moltbot Gateway Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/moltbot/gateway` | GET | Gateway status and info |
| `/api/moltbot/skills` | GET | List all available skills |
| `/api/moltbot/execute` | POST | Execute a skill |
| `/api/moltbot/skill/critical-monitor/{patient_id}` | POST | Run critical monitoring |
| `/api/moltbot/skill/diet-suggestion/{patient_id}` | POST | Generate diet plan |
| `/api/moltbot/skill/realtime-feedback/{patient_id}` | POST | Get real-time feedback |
| `/api/moltbot/skill/daily-progress/{patient_id}` | POST | Generate daily report |
| `/api/moltbot/run-all/{patient_id}` | POST | Execute all skills |
| `/api/moltbot/activities` | GET | Activity feed |
| `/api/moltbot/stats` | GET | Gateway statistics |

### Greenfield Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/greenfield/status` | GET | Storage connection status |
| `/api/greenfield/store-alert` | POST | Store alert on Greenfield |
| `/api/greenfield/store-diet/{patient_id}` | POST | Store diet plan |
| `/api/greenfield/store-progress/{patient_id}` | POST | Store daily progress |

### Patient/Doctor/Hospital Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/patients` | GET | List all patients |
| `/api/patients/{id}` | GET | Get patient details |
| `/api/patients/{id}/readings` | GET | Patient device readings |
| `/api/patients/{id}/alerts` | GET | Patient alerts |
| `/api/doctors` | GET | List all doctors |
| `/api/hospitals` | GET | List all hospitals |
| `/api/telemetry/live` | GET | Live telemetry data |

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Test API Endpoints

```bash
# Get gateway status
curl http://localhost:8001/api/moltbot/gateway

# Execute critical monitor skill
curl -X POST http://localhost:8001/api/moltbot/skill/critical-monitor/{patient_id}

# Check Greenfield status
curl http://localhost:8001/api/greenfield/status
```

---

## 📝 Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URL` | MongoDB connection string | Yes |
| `DB_NAME` | Database name | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | Yes |
| `EMERGENT_LLM_KEY` | OpenAI API key for AI features | Yes |
| `USE_REAL_GREENFIELD` | Enable real Greenfield storage | No |
| `GREENFIELD_BUCKET_NAME` | Your Greenfield bucket name | No |
| `GREENFIELD_USE_MAINNET` | Use Mainnet (true) or Testnet (false) | No |
| `DEPLOYER_PRIVATE_KEY` | For contract deployment | No |

### Frontend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_BACKEND_URL` | Backend API URL | Yes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Patient  │  │  Doctor  │  │   Org    │  │ Moltbot Skills   │ │
│  │Dashboard │  │Dashboard │  │Dashboard │  │     Panel        │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
└───────┼─────────────┼─────────────┼─────────────────┼───────────┘
        │             │             │                 │
        └─────────────┴─────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   MOLTBOT GATEWAY                          │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐│ │
│  │  │  Critical  │ │    Diet    │ │  Realtime  │ │  Daily   ││ │
│  │  │  Monitor   │ │ Suggestion │ │  Feedback  │ │ Progress ││ │
│  │  │   SKILL    │ │   SKILL    │ │   SKILL    │ │  SKILL   ││ │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └────┬─────┘│ │
│  └────────┼──────────────┼──────────────┼─────────────┼──────┘ │
│           │              │              │             │        │
│  ┌────────▼──────────────▼──────────────▼─────────────▼──────┐ │
│  │                      MongoDB                               │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│    opBNB      │  │ BNB Greenfield│  │    OpenAI     │
│  Blockchain   │  │    Storage    │  │   (GPT-4o)    │
│               │  │               │  │               │
│ • HealthAudit │  │ • Medical     │  │ • Diet Plans  │
│ • Paymaster   │  │   Records     │  │ • Feedback    │
│ • Wallets     │  │ • Alerts      │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## 🔐 Security Considerations

- All critical alerts are SHA-256 hashed before storage
- Medical records are encrypted on Greenfield
- Smart contract wallets isolate patient funds
- Paymaster prevents unauthorized gas spending
- Role-based access control for dashboards

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

- **Documentation**: [docs.omnihealth.io](#)
- **Issues**: [GitHub Issues](https://github.com/yourusername/omnihealth-guardian/issues)
- **Email**: support@omnihealth.io

---

<div align="center">

**Built for BNB Chain Hackathon 2025**

Powered by **opBNB** • **BNB Greenfield** • **OpenClaw/Moltbot**

</div>
