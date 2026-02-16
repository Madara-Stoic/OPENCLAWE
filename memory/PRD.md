# OmniHealth Guardian - Product Requirements Document

## Original Problem Statement
Build a decentralized platform for real-time monitoring of critical medical IoT devices like insulin pumps and pacemakers. The platform includes:
- Three dashboards: Patient, Doctor, Organization
- Account Abstraction with Paymaster on opBNB
- OpenClaw/Moltbot Guardian Agent for monitoring
- Critical alerts with SHA-256 hashing and blockchain verification
- BNB Greenfield for off-chain storage (simulated)
- AI diet suggestions

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB
- **AI**: OpenAI GPT-4o via Emergent LLM Key
- **Blockchain**: opBNB Testnet (simulated)

## User Personas
1. **Patient**: Views personal vitals, receives AI diet plans, monitors device battery
2. **Doctor**: Monitors multiple patients, views alerts, tracks patient trends
3. **Organization**: System-wide analytics, device deployment, system health

## Core Requirements (Static)
- Real-time device telemetry (glucose, heart rate, battery)
- Critical alert detection with SHA-256 hashing
- AI-powered diet suggestions
- Dark-mode, high-contrast medical UI
- Simulated blockchain verification on opBNB

## What's Been Implemented (Feb 2026)
- ✅ Landing page with social auth simulation
- ✅ Patient Dashboard with real-time vitals and AI diet plans
- ✅ Doctor Dashboard with live patient telemetry
- ✅ Organization Dashboard with system analytics
- ✅ Moltbot activity feed with "Verified by OpenClaw" badges
- ✅ Mock data: 10 patients, 20 doctors, 30 hospitals
- ✅ Critical alert system with blockchain verification links
- ✅ Smart Contract Wallet creation simulation

## Simulated/Mocked Components
- Blockchain transactions (mock tx_hash, links to real opBNB explorer)
- Account Abstraction (simulated wallet creation)
- BNB Greenfield storage (local SHA-256 hashing)
- OpenClaw agent (using OpenAI GPT-4o instead)

## Prioritized Backlog

### P0 - Critical (Not Blocked)
- All P0 features implemented

### P1 - High Priority
- Actual smart contract deployment on opBNB testnet
- Real Account Abstraction with Biconomy/Particle
- Push notifications for critical alerts
- Patient data encryption

### P2 - Medium Priority
- BNB Greenfield integration for medical record storage
- Historical data export
- Multi-language support
- Mobile responsive improvements

## Next Tasks
1. Deploy HealthAudit.sol contract on opBNB testnet
2. Integrate real Paymaster for gas-free critical alerts
3. Add WebSocket for true real-time updates
4. Implement patient data encryption at rest
