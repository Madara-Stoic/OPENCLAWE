# OmniHealth Guardian - Smart Contract Deployment Guide

## 🚀 Quick Deploy Instructions

### Step 1: Get Test BNB on opBNB Testnet

Fund the deployer wallet with test BNB from one of these faucets:

**Deployer Wallet Address:**
```
0xBbbd90a05650cE647889258251A861e479ca2e4f
```

**Faucet Options:**
1. **L2 Faucet (Recommended)**: https://www.l2faucet.com/opbnb
2. **Chainlink Faucet**: https://faucets.chain.link/opbnb-testnet
3. **BSC Testnet + Bridge**:
   - Get BSC testnet BNB: https://testnet.bnbchain.org/faucet-smart
   - Bridge to opBNB: https://opbnb-testnet-bridge.bnbchain.org/deposit

### Step 2: Run Deployment

Once the wallet is funded, run:

```bash
cd /app/backend
export DEPLOYER_PRIVATE_KEY=e6e3df99443d25570c88b91f8f3a26e2221f5b35b8c1b95d7cf526803e7538a4
python deploy_contracts.py
```

### Step 3: Expected Output

After successful deployment, you'll get:
- **HealthAudit Contract**: Stores critical medical alert hashes
- **SimplePaymaster Contract**: Sponsors gas for critical transactions  
- **PatientWalletFactory Contract**: Creates smart wallets for patients

All deployed contract addresses and transaction hashes will be saved to:
`/app/backend/deployment_result.json`

---

## 📋 Contract Details

### HealthAudit.sol
Stores SHA-256 hashes of critical medical alerts on-chain.
- `recordAlert(bytes32 hash, address patient, string alertType)` - Record new alert
- `getAlert(uint256 id)` - Retrieve alert details
- `verifyAlertHash(uint256 id, bytes32 hash)` - Verify hash matches

### SimplePaymaster.sol
Sponsors gas fees for critical medical transactions.
- `deposit()` - Add funds for sponsorship
- `sponsorGas(address user, uint256 amount, string reason)` - Sponsor gas
- `whitelistCaller(address caller)` - Authorize contract to use paymaster

### PatientWalletFactory.sol
Creates smart contract wallets for each patient.
- `createWallet(address patientEOA, address guardian)` - Deploy new patient wallet
- `getWallet(address patient)` - Get wallet address for patient
- `getWalletCount()` - Total wallets created

---

## 🔗 Network Details

| Network | Chain ID | RPC URL | Explorer |
|---------|----------|---------|----------|
| opBNB Testnet | 5611 | https://opbnb-testnet-rpc.bnbchain.org | https://testnet.opbnbscan.com |

---

## ⚠️ Security Notes

- **Private Key**: `e6e3df99443d25570c88b91f8f3a26e2221f5b35b8c1b95d7cf526803e7538a4`
- This is a TESTNET wallet - do NOT use on mainnet
- For production, generate new keys and keep them secure
