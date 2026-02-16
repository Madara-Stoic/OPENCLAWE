"""
Deploy OmniHealth Guardian Smart Contracts to opBNB Testnet
- HealthAudit: Critical alert storage
- SimplePaymaster: Gas sponsorship
- PatientWalletFactory: Smart contract wallet factory
"""

import os
import json
import subprocess
from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc

# Install solc
print("Installing Solidity compiler...")
install_solc("0.8.19")

# opBNB Testnet Configuration
OPBNB_TESTNET_RPC = "https://opbnb-testnet-rpc.bnbchain.org"
CHAIN_ID = 5611

# Connect to opBNB Testnet
w3 = Web3(Web3.HTTPProvider(OPBNB_TESTNET_RPC))
print(f"Connected to opBNB Testnet: {w3.is_connected()}")
print(f"Chain ID: {w3.eth.chain_id}")

# Generate a new deployer wallet
deployer = Account.create()
print(f"\n=== DEPLOYER WALLET ===")
print(f"Address: {deployer.address}")
print(f"Private Key: {deployer.key.hex()}")
print(f"\n⚠️  IMPORTANT: Fund this address with test BNB from opBNB faucet!")
print(f"Faucet: https://opbnb-testnet-bridge.bnbchain.org/deposit")
print(f"Or BSC Testnet faucet + bridge: https://testnet.bnbchain.org/faucet-smart")

# Load contract source files
def load_contract(filename):
    with open(f"/app/backend/contracts/{filename}", "r") as f:
        return f.read()

health_audit_source = load_contract("HealthAudit.sol")
paymaster_source = load_contract("SimplePaymaster.sol")
wallet_factory_source = load_contract("PatientWalletFactory.sol")

# Compile contracts
def compile_contract(source, contract_name):
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            f"{contract_name}.sol": {"content": source}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            },
            "optimizer": {
                "enabled": True,
                "runs": 200
            }
        }
    }, solc_version="0.8.19")
    
    contract_data = compiled["contracts"][f"{contract_name}.sol"][contract_name]
    return {
        "abi": contract_data["abi"],
        "bytecode": contract_data["evm"]["bytecode"]["object"]
    }

print("\nCompiling contracts...")
health_audit = compile_contract(health_audit_source, "HealthAudit")
paymaster = compile_contract(paymaster_source, "SimplePaymaster")
wallet_factory = compile_contract(wallet_factory_source, "PatientWalletFactory")

# Also compile PatientWallet for reference
patient_wallet_compiled = compile_standard({
    "language": "Solidity",
    "sources": {
        "PatientWalletFactory.sol": {"content": wallet_factory_source}
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        },
        "optimizer": {
            "enabled": True,
            "runs": 200
        }
    }
}, solc_version="0.8.19")

patient_wallet_abi = patient_wallet_compiled["contracts"]["PatientWalletFactory.sol"]["PatientWallet"]["abi"]

print("✅ HealthAudit compiled")
print("✅ SimplePaymaster compiled")
print("✅ PatientWalletFactory compiled")

# Save compiled contracts for later use
compiled_contracts = {
    "deployer": {
        "address": deployer.address,
        "private_key": deployer.key.hex()
    },
    "network": {
        "name": "opBNB Testnet",
        "rpc": OPBNB_TESTNET_RPC,
        "chain_id": CHAIN_ID,
        "explorer": "https://testnet.opbnbscan.com"
    },
    "contracts": {
        "HealthAudit": {
            "abi": health_audit["abi"],
            "bytecode": health_audit["bytecode"]
        },
        "SimplePaymaster": {
            "abi": paymaster["abi"],
            "bytecode": paymaster["bytecode"]
        },
        "PatientWalletFactory": {
            "abi": wallet_factory["abi"],
            "bytecode": wallet_factory["bytecode"]
        },
        "PatientWallet": {
            "abi": patient_wallet_abi
        }
    }
}

with open("/app/backend/compiled_contracts.json", "w") as f:
    json.dump(compiled_contracts, f, indent=2)

print("\n✅ Compiled contracts saved to /app/backend/compiled_contracts.json")

# Deployment function
def deploy_contract(contract_data, constructor_args=None, private_key=None, gas_price_gwei=0.001):
    """Deploy a contract and return tx hash and contract address"""
    if private_key is None:
        return None, None, "No private key provided"
    
    account = Account.from_key(private_key)
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    if balance == 0:
        return None, None, f"Account {account.address} has no balance. Please fund with test BNB."
    
    contract = w3.eth.contract(abi=contract_data["abi"], bytecode=contract_data["bytecode"])
    
    # Build constructor transaction
    if constructor_args:
        tx = contract.constructor(*constructor_args).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': w3.to_wei(gas_price_gwei, 'gwei'),
            'chainId': CHAIN_ID
        })
    else:
        tx = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': w3.to_wei(gas_price_gwei, 'gwei'),
            'chainId': CHAIN_ID
        })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    return tx_hash.hex(), receipt.contractAddress, None

print("\n" + "="*60)
print("DEPLOYMENT INSTRUCTIONS")
print("="*60)
print(f"""
1. Fund the deployer wallet with test BNB:
   Address: {deployer.address}
   
2. Get test BNB from:
   - BSC Testnet Faucet: https://testnet.bnbchain.org/faucet-smart
   - Then bridge to opBNB: https://opbnb-testnet-bridge.bnbchain.org/deposit

3. Once funded, run the deployment:
   python /app/backend/deploy_funded.py

4. Or provide your own funded wallet private key in .env:
   DEPLOYER_PRIVATE_KEY=0x...
""")

# Check if we have a funded wallet
env_private_key = os.environ.get("DEPLOYER_PRIVATE_KEY")
if env_private_key:
    print("\n🔑 Found DEPLOYER_PRIVATE_KEY in environment, attempting deployment...")
    
    try:
        account = Account.from_key(env_private_key)
        balance = w3.eth.get_balance(account.address)
        balance_bnb = w3.from_wei(balance, 'ether')
        print(f"Deployer: {account.address}")
        print(f"Balance: {balance_bnb} BNB")
        
        if balance > 0:
            print("\n📦 Deploying contracts...")
            
            # Deploy HealthAudit
            print("Deploying HealthAudit...")
            tx1, addr1, err1 = deploy_contract(health_audit, private_key=env_private_key)
            if err1:
                print(f"❌ HealthAudit deployment failed: {err1}")
            else:
                print(f"✅ HealthAudit deployed: {addr1}")
                print(f"   TX: {tx1}")
            
            # Deploy SimplePaymaster
            print("Deploying SimplePaymaster...")
            tx2, addr2, err2 = deploy_contract(paymaster, private_key=env_private_key)
            if err2:
                print(f"❌ SimplePaymaster deployment failed: {err2}")
            else:
                print(f"✅ SimplePaymaster deployed: {addr2}")
                print(f"   TX: {tx2}")
            
            # Deploy PatientWalletFactory with deployer as default guardian
            print("Deploying PatientWalletFactory...")
            tx3, addr3, err3 = deploy_contract(
                wallet_factory, 
                constructor_args=[account.address],  # default guardian
                private_key=env_private_key
            )
            if err3:
                print(f"❌ PatientWalletFactory deployment failed: {err3}")
            else:
                print(f"✅ PatientWalletFactory deployed: {addr3}")
                print(f"   TX: {tx3}")
            
            # Save deployment results
            if addr1 and addr2 and addr3:
                deployment_result = {
                    "network": "opBNB Testnet",
                    "chain_id": CHAIN_ID,
                    "explorer": "https://testnet.opbnbscan.com",
                    "deployer": account.address,
                    "contracts": {
                        "HealthAudit": {
                            "address": addr1,
                            "tx_hash": tx1
                        },
                        "SimplePaymaster": {
                            "address": addr2,
                            "tx_hash": tx2
                        },
                        "PatientWalletFactory": {
                            "address": addr3,
                            "tx_hash": tx3
                        }
                    }
                }
                
                with open("/app/backend/deployment_result.json", "w") as f:
                    json.dump(deployment_result, f, indent=2)
                
                print("\n" + "="*60)
                print("🎉 DEPLOYMENT SUCCESSFUL!")
                print("="*60)
                print(f"HealthAudit: {addr1}")
                print(f"SimplePaymaster: {addr2}")
                print(f"PatientWalletFactory: {addr3}")
                print(f"\nView on Explorer:")
                print(f"https://testnet.opbnbscan.com/address/{addr1}")
                print(f"https://testnet.opbnbscan.com/address/{addr2}")
                print(f"https://testnet.opbnbscan.com/address/{addr3}")
        else:
            print(f"❌ Account has no balance. Please fund: {account.address}")
    except Exception as e:
        print(f"❌ Deployment error: {e}")
else:
    print("\n⚠️  No DEPLOYER_PRIVATE_KEY found. Contracts compiled but not deployed.")
    print("Set DEPLOYER_PRIVATE_KEY environment variable with a funded wallet to deploy.")
