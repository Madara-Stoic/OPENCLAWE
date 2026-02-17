# OmniHealth Guardian - Product Requirements Document

## Original Problem Statement
Build 'OmniHealth Guardian,' a decentralized platform for real-time monitoring of critical medical IoT devices like insulin pumps and pacemakers.

### Core Requirements
- **Platform**: BNB Chain (opBNB for transactions, Greenfield for storage)
- **AI Engine**: OpenClaw (Moltbot) Framework
- **User Tiers**: Patient, Doctor, Organization dashboards
- **Account Abstraction**: Paymaster on opBNB with Social Auth
- **Guardian Agent**: OpenClaw agent for monitoring with on-chain verification
- **Data Storage**: BNB Greenfield for encrypted medical logs

---

## What's Been Implemented

### ✅ Completed (December 2025)
1. **Full-Stack Application**
   - React frontend with TailwindCSS, Shadcn/UI
   - FastAPI backend with async MongoDB
   - 3 role-based dashboards (Patient, Doctor, Org)

2. **Moltbot/OpenClaw Integration**
   - Real OpenClaw-compatible architecture
   - SKILL.md configuration files
   - Moltbot Gateway with 4 skills:
     - Critical Condition Monitor
     - AI Diet Suggestion
     - Real-time Feedback
     - Daily Progress Tracker

3. **BNB Greenfield**
   - Connected to Mainnet
   - Bucket "openclaw" created
   - Integration code complete

4. **Smart Contracts**
   - HealthAudit.sol written
   - SimplePaymaster.sol written
   - PatientWalletFactory.sol written

5. **UI/UX**
   - Dark theme with high contrast
   - Real-time charts
   - "Verified by OpenClaw" badges
   - Blockchain verification links

---

## Backlog (P0-P2)

### P0 - Critical
- [ ] Fix Greenfield permissions (change Viewer → Editor)
- [ ] Deploy smart contracts to opBNB testnet

### P1 - High Priority
- [ ] Real blockchain transaction recording
- [ ] Implement Account Abstraction with Biconomy

### P2 - Nice to Have
- [ ] "Nearest Hospital" notification
- [ ] WebSocket real-time updates
- [ ] Mobile responsive optimization
- [ ] Email/SMS alerts for critical conditions

---

## Technical Architecture

```
Frontend (React) → Backend (FastAPI) → MongoDB
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
     Moltbot         Greenfield       opBNB
     Gateway         (Mainnet)      (Testnet)
```

## Key Files
- `/app/backend/server.py` - Main API
- `/app/backend/moltbot_gateway.py` - OpenClaw Gateway
- `/app/backend/greenfield_storage.py` - Greenfield integration
- `/app/backend/skills/` - SKILL.md definitions
- `/app/frontend/src/components/OpenClawSkillsPanel.jsx` - Skills UI
