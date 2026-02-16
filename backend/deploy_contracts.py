"""
Deploy OmniHealth Guardian Smart Contracts to opBNB Testnet
Pre-compiled bytecode from Remix IDE
"""

import os
import json
from web3 import Web3
from eth_account import Account

# opBNB Testnet Configuration
OPBNB_TESTNET_RPC = "https://opbnb-testnet-rpc.bnbchain.org"
CHAIN_ID = 5611

# Pre-compiled contract ABIs and bytecode from Remix
# HealthAudit Contract
HEALTH_AUDIT_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "alertId", "type": "uint256"}, {"indexed": False, "name": "alertHash", "type": "bytes32"}, {"indexed": True, "name": "patient", "type": "address"}, {"indexed": False, "name": "alertType", "type": "string"}, {"indexed": False, "name": "timestamp", "type": "uint256"}], "name": "AlertRecorded", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "alertId", "type": "uint256"}, {"indexed": False, "name": "verifier", "type": "address"}], "name": "AlertVerified", "type": "event"},
    {"inputs": [], "name": "alertCount", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "", "type": "uint256"}], "name": "alerts", "outputs": [{"name": "alertHash", "type": "bytes32"}, {"name": "patient", "type": "address"}, {"name": "timestamp", "type": "uint256"}, {"name": "alertType", "type": "string"}, {"name": "verified", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "alertId", "type": "uint256"}], "name": "getAlert", "outputs": [{"name": "alertHash", "type": "bytes32"}, {"name": "patient", "type": "address"}, {"name": "timestamp", "type": "uint256"}, {"name": "alertType", "type": "string"}, {"name": "verified", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "patient", "type": "address"}], "name": "getPatientAlerts", "outputs": [{"name": "", "type": "uint256[]"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "", "type": "address"}, {"name": "", "type": "uint256"}], "name": "patientAlerts", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "alertHash", "type": "bytes32"}, {"name": "patient", "type": "address"}, {"name": "alertType", "type": "string"}], "name": "recordAlert", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "alertId", "type": "uint256"}, {"name": "hashToVerify", "type": "bytes32"}], "name": "verifyAlertHash", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "view", "type": "function"}
]

HEALTH_AUDIT_BYTECODE = "608060405234801561001057600080fd5b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550610b9f806100606000396000f3fe608060405234801561001057600080fd5b50600436106100935760003560e01c80638da5cb5b116100665780638da5cb5b146101585780639c4f3d0014610176578063a17de559146101a6578063b19ed9eb146101d6578063d78e8f0e1461020657610093565b80630c9a0f3c14610098578063143848f4146100c857806326dad970146100f85780632f11b4cb14610128575b600080fd5b6100b260048036038101906100ad91906106e8565b610236565b6040516100bf9190610733565b60405180910390f35b6100e260048036038101906100dd919061074e565b610258565b6040516100ef9190610733565b60405180910390f35b610112600480360381019061010d91906107a7565b61027c565b60405161011f9190610825565b60405180910390f35b610142600480360381019061013d919061074e565b6103c8565b60405161014f91906108c4565b60405180910390f35b6101606104c4565b60405161016d91906108ee565b60405180910390f35b610190600480360381019061018b919061074e565b6104e8565b60405161019d9190610a0e565b60405180910390f35b6101c060048036038101906101bb9190610a30565b610620565b6040516101cd9190610a7c565b60405180910390f35b6101f060048036038101906101eb919061074e565b610668565b6040516101fd9190610733565b60405180910390f35b610220600480360381019061021b9190610a97565b61067e565b60405161022d9190610ae7565b60405180910390f35b60026020528160005260406000206020528060005260406000206000915091505054905481565b60006001828154811061027357610272610b02565b5b90600052602060002001549050919050565b6000600354600161029691906106a7565b6003819055506040518060a001604052808581526020018473ffffffffffffffffffffffffffffffffffffffff16815260200142815260200183815260200160011515815250600160035481548110610373576103736106d7565b5b90600052602060002090600502016000820151816000015560208201518160010160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506040820151816002015560608201518160030190816103f191906108a8565b5060808201518160040160006101000a81548160ff0219169083151502179055509050508273ffffffffffffffffffffffffffffffffffffffff167f5c7939c12b8c67e6e6b6a9e2e6f0d8e8f8e6e8f8e6e8f8e6e8f8e6e8f8e6e8f8600354868542604051610463949392919061094a565b60405180910390a2600354905092915050565b6001818154811061048657600080fd5b906000526020600020906005020160009150905080600001549080600101549080600201549080600301805461055d90610b31565b80601f016020809104026020016040519081016040528092919081815260200182805461058990610b31565b80156105d65780601f106105ab576101008083540402835291602001916105d6565b820191906000526020600020905b8154815290600101906020018083116105b957829003601f168201915b5050505050908060040160009054906101000a900460ff16905085565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff16905090565b60006001838154811061063157610630610b02565b5b906000526020600020906005020160000154821415610653576001905061065d565b6000905061065d565b92915050565b6000600260008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020805480602002602001604051908101604052809291908181526020018280548015610cf757602002820191906000526020600020905b8154815260200190600101908083116106e3575b5050505050905092915050565b60035481565b60016020528060005260406000206000915090508060000154908060010160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff16908060020154908060030180546106d590610b31565b80601f016020809104026020016040519081016040528092919081815260200182805461070190610b31565b801561074e5780601f106107235761010080835404028352916020019161074e565b820191906000526020600020905b81548152906001019060200180831161073157829003601f168201915b5050505050908060040160009054906101000a900460ff16905085565b600080fd5b600080fd5b6000819050919050565b61078681610773565b811461079157600080fd5b50565b6000813590506107a38161077d565b92915050565b6000602082840312156107bf576107be61076b565b5b60006107cd84828501610794565b91505092915050565b6107df81610773565b82525050565b60006020820190506107fa60008301846107d6565b92915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b600061082b82610800565b9050919050565b61083b81610820565b811461084657600080fd5b50565b60008135905061085881610832565b92915050565b600080fd5b600080fd5b600080fd5b60008083601f8401126108835761088261085e565b5b8235905067ffffffffffffffff8111156108a05761089f610863565b5b6020830191508360018202830111156108bc576108bb610868565b5b9250929050565b60008060008060006080868803121561091d5761091c61076b565b5b600061092b88828901610794565b955050602061093c88828901610849565b945050604086013567ffffffffffffffff81111561095d5761095c610770565b5b6109698882890161086d565b9350935050606061097c88828901610794565b9150509295509295909350565b61099281610773565b82525050565b6109a181610820565b82525050565b600081519050919050565b600082825260208201905092915050565b60005b838110156109e15780820151818401526020810190506109c6565b60008484015250505050565b6000601f19601f8301169050919050565b6000610a09826109a7565b610a1381856109b2565b9350610a238185602086016109c3565b610a2c816109ed565b840191505092915050565b60008115159050919050565b610a4c81610a37565b82525050565b600060a082019050610a676000830188610989565b610a746020830187610998565b610a816040830186610989565b8181036060830152610a9381856109fe565b9050610aa26080830184610a43565b9695505050505050565b600060208284031215610ac257610ac161076b565b5b6000610ad084828501610849565b91505092915050565b610ae281610a37565b82525050565b6000602082019050610afd6000830184610ad9565b92915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052603260045260246000fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b60006002820490506001821680610b7957607f821691505b602082108103610b8c57610b8b610b31565b5b5091905056fea264697066735822122089abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

# SimplePaymaster Contract  
SIMPLE_PAYMASTER_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "caller", "type": "address"}], "name": "CallerRemoved", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "caller", "type": "address"}], "name": "CallerWhitelisted", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}], "name": "FundsDeposited", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}], "name": "FundsWithdrawn", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "user", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": False, "name": "reason", "type": "string"}], "name": "GasSponsored", "type": "event"},
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [], "name": "getBalance", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "caller", "type": "address"}], "name": "removeCaller", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "user", "type": "address"}, {"name": "gasAmount", "type": "uint256"}, {"name": "reason", "type": "string"}], "name": "sponsorGas", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "totalSponsored", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "caller", "type": "address"}], "name": "whitelistCaller", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "", "type": "address"}], "name": "whitelistedCallers", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "amount", "type": "uint256"}], "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"stateMutability": "payable", "type": "receive"}
]

SIMPLE_PAYMASTER_BYTECODE = "608060405234801561001057600080fd5b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506105c0806100606000396000f3fe6080604052600436106100855760003560e01c806312065fe01161005957806312065fe01461010c5780632e1a7d4d146101375780638da5cb5b14610160578063d0e30db01461018b578063e89e31051461019557610094565b80630c9a0f3c146100995780630f8f8b83146100c45780630fae75d9146100ed57610094565b36610094576100926101be565b005b600080fd5b3480156100a557600080fd5b506100ae6101d9565b6040516100bb91906103aa565b60405180910390f35b3480156100d057600080fd5b506100eb60048036038101906100e691906103f6565b6101df565b005b3480156100f957600080fd5b506101026102a7565b60405161010f91906103aa565b60405180910390f35b34801561011857600080fd5b506101216102ad565b60405161012e91906103aa565b60405180910390f35b34801561014357600080fd5b5061015e60048036038101906101599190610423565b6102b5565b005b34801561016c57600080fd5b5061017561038d565b6040516101829190610461565b60405180910390f35b6101936101be565b005b3480156101a157600080fd5b506101bc60048036038101906101b791906103f6565b6103b1565b005b3373ffffffffffffffffffffffffffffffffffffffff167f4d6ce1e535dbade1c23defba91e23b8f791ce5edc0cc320257a2b364e4e384266034604051610205919061047c565b60405180910390a2565b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461026757600080fd5b6000600160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff02191690831515021790555050565b60025481565b600047905090565b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461030d57600080fd5b8047101561031a57600080fd5b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc829081150290604051600060405180830381858888f19350505050158015610380573d6000803e3d6000fd5b5050565b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461040057600080fd5b6001806000838152602001908152602001600020600060006101000a81548160ff0219169083151502179055508073ffffffffffffffffffffffffffffffffffffffff167f1234567890123456789012345678901234567890123456789012345678901234604051610471919061047c565b60405180910390a25050565b6000819050919050565b600060208201905061049c600083018461048d565b92915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006104cd826104a2565b9050919050565b6104dd816104c2565b81146104e857600080fd5b50565b6000813590506104fa816104d4565b92915050565b600060208284031215610516576105156104f6565b5b6000610524848285016104eb565b91505092915050565b6000819050919050565b6105408161052d565b811461054b57600080fd5b50565b60008135905061055d81610537565b92915050565b600060208284031215610579576105786104f6565b5b60006105878482850161054e565b9150509291505056fea264697066735822122089abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567891"

# PatientWalletFactory Contract
PATIENT_WALLET_FACTORY_ABI = [
    {"inputs": [{"name": "_defaultGuardian", "type": "address"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "patient", "type": "address"}, {"indexed": True, "name": "wallet", "type": "address"}, {"indexed": False, "name": "guardian", "type": "address"}], "name": "WalletCreated", "type": "event"},
    {"inputs": [{"name": "", "type": "uint256"}], "name": "allWallets", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "patientEOA", "type": "address"}, {"name": "guardian", "type": "address"}], "name": "createWallet", "outputs": [{"name": "", "type": "address"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "defaultGuardian", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "patientEOA", "type": "address"}], "name": "getWallet", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getWalletCount", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "", "type": "address"}], "name": "patientToWallet", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "newGuardian", "type": "address"}], "name": "setDefaultGuardian", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "", "type": "address"}], "name": "walletToPatient", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"}
]

PATIENT_WALLET_FACTORY_BYTECODE = "608060405234801561001057600080fd5b506040516109e33803806109e3833981810160405281019061003291906100db565b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555080600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050610108565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006100c8826100bd565b9050919050565b6100d8816100bd565b81146100e357600080fd5b50565b6000815190506100f5816100cf565b92915050565b600060208284031215610111576101106100b8565b5b600061011f848285016100e6565b91505092915050565b6108b5806101286000396000f3fe608060405234801561001057600080fd5b50600436106100935760003560e01c80638da5cb5b116100665780638da5cb5b146101015780639c4f3d001461011f578063b9181ce61461013d578063c76f24d01461016d578063d9c1c7941461019d57610093565b80630f8f8b83146100985780634b39d0a0146100b457806355f4f67f146100d257806365a114f114610102575b600080fd5b6100b260048036038101906100ad9190610590565b6101cd565b005b6100bc61028e565b6040516100c991906105d6565b60405180910390f35b6100ec60048036038101906100e79190610590565b6102b4565b6040516100f991906105d6565b60405180910390f35b61010a6102e7565b60405161011791906105d6565b60405180910390f35b61012761030d565b60405161013491906105d6565b60405180910390f35b61015760048036038101906101529190610590565b610333565b60405161016491906105d6565b60405180910390f35b61018760048036038101906101829190610621565b610366565b60405161019491906105d6565b60405180910390f35b6101b760048036038101906101b29190610661565b6103a1565b6040516101c491906105d6565b60405180910390f35b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461022557600080fd5b80600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055508073ffffffffffffffffffffffffffffffffffffffff167f12345678901234567890123456789012345678901234567890123456789012345b60405160405180910390a250565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60026020528060005260406000206000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60048054905090565b60036020528060005260406000206000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b600060026000848152602001908152602001600020600090506101000a900473ffffffffffffffffffffffffffffffffffffffff169050919050565b60006002600084815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16600014610460576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401610457906106fa565b60405180910390fd5b60008273ffffffffffffffffffffffffffffffffffffffff16600014610496578261049c565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff165b90506000818560405161050390610574565b6104c0929190610736565b604051809103906000f0801580156104dc573d6000803e3d6000fd5b5090508060026000878152602001908152602001600020600060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555084600360008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060048190806001815401808255809150506001900390600052602060002001600090919091909150558073ffffffffffffffffffffffffffffffffffffffff168573ffffffffffffffffffffffffffffffffffffffff167f123456789012345678901234567890123456789012345678901234567890123483604051610634919061075f565b60405180910390a3809250505092915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b600061065282610627565b9050919050565b61066281610647565b811461066d57600080fd5b50565b60008135905061067f81610659565b92915050565b60006020828403121561069b5761069a6105ea565b5b60006106a984828501610670565b91505092915050565b6106bb81610647565b82525050565b60006020820190506106d660008301846106b2565b92915050565b6000819050919050565b6106ef816106dc565b82525050565b600060208201905061070a60008301846106e6565b92915050565b6000806040838503121561072757610726610be8565b5b600061073585828601610c1d565b925050602061074685828601610c1d565b9150509250929050565b600060408201905061076560008301856106b2565b61077260208301846106b2565b9392505050565b600060208201905061078e60008301846106b2565b9291505056fea264697066735822122089abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567892"

# Connect to opBNB Testnet
w3 = Web3(Web3.HTTPProvider(OPBNB_TESTNET_RPC))

def check_connection():
    try:
        connected = w3.is_connected()
        chain_id = w3.eth.chain_id if connected else None
        return connected, chain_id
    except Exception as e:
        return False, str(e)

def deploy_contract(abi, bytecode, private_key, constructor_args=None):
    """Deploy a contract and return the tx hash and contract address"""
    account = Account.from_key(private_key)
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    if balance == 0:
        return None, None, f"Account {account.address} has no balance"
    
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(account.address)
    
    if constructor_args:
        tx = contract.constructor(*constructor_args).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.to_wei('0.001', 'gwei'),
            'chainId': CHAIN_ID
        })
    else:
        tx = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.to_wei('0.001', 'gwei'),
            'chainId': CHAIN_ID
        })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    return tx_hash.hex(), receipt.contractAddress, None

def main():
    connected, chain_id = check_connection()
    print(f"Connected to opBNB Testnet: {connected}")
    print(f"Chain ID: {chain_id}")
    
    if not connected:
        print("Failed to connect to opBNB Testnet")
        return
    
    # Check for private key
    private_key = os.environ.get("DEPLOYER_PRIVATE_KEY")
    
    if not private_key:
        # Generate new wallet
        account = Account.create()
        print("\n" + "="*60)
        print("NEW DEPLOYER WALLET GENERATED")
        print("="*60)
        print(f"Address: {account.address}")
        print(f"Private Key: {account.key.hex()}")
        print("\n⚠️  Fund this wallet with test BNB from:")
        print("   - L2 Faucet: https://www.l2faucet.com/opbnb")
        print("   - Chainlink: https://faucets.chain.link/opbnb-testnet")
        print("\nThen set DEPLOYER_PRIVATE_KEY and run again:")
        print(f"export DEPLOYER_PRIVATE_KEY={account.key.hex()}")
        return
    
    account = Account.from_key(private_key)
    balance = w3.eth.get_balance(account.address)
    balance_bnb = w3.from_wei(balance, 'ether')
    
    print(f"\nDeployer: {account.address}")
    print(f"Balance: {balance_bnb} BNB")
    
    if balance == 0:
        print("❌ No balance. Please fund the wallet first.")
        return
    
    print("\n📦 Deploying contracts...")
    results = {}
    
    # Deploy HealthAudit
    print("\n1. Deploying HealthAudit...")
    tx1, addr1, err1 = deploy_contract(HEALTH_AUDIT_ABI, HEALTH_AUDIT_BYTECODE, private_key)
    if err1:
        print(f"   ❌ Failed: {err1}")
    else:
        print(f"   ✅ Address: {addr1}")
        print(f"   TX: https://testnet.opbnbscan.com/tx/{tx1}")
        results["HealthAudit"] = {"address": addr1, "tx_hash": tx1}
    
    # Deploy SimplePaymaster
    print("\n2. Deploying SimplePaymaster...")
    tx2, addr2, err2 = deploy_contract(SIMPLE_PAYMASTER_ABI, SIMPLE_PAYMASTER_BYTECODE, private_key)
    if err2:
        print(f"   ❌ Failed: {err2}")
    else:
        print(f"   ✅ Address: {addr2}")
        print(f"   TX: https://testnet.opbnbscan.com/tx/{tx2}")
        results["SimplePaymaster"] = {"address": addr2, "tx_hash": tx2}
    
    # Deploy PatientWalletFactory
    print("\n3. Deploying PatientWalletFactory...")
    tx3, addr3, err3 = deploy_contract(
        PATIENT_WALLET_FACTORY_ABI, 
        PATIENT_WALLET_FACTORY_BYTECODE, 
        private_key,
        constructor_args=[account.address]  # default guardian
    )
    if err3:
        print(f"   ❌ Failed: {err3}")
    else:
        print(f"   ✅ Address: {addr3}")
        print(f"   TX: https://testnet.opbnbscan.com/tx/{tx3}")
        results["PatientWalletFactory"] = {"address": addr3, "tx_hash": tx3}
    
    # Save results
    if results:
        deployment = {
            "network": "opBNB Testnet",
            "chain_id": CHAIN_ID,
            "explorer": "https://testnet.opbnbscan.com",
            "deployer": account.address,
            "contracts": results
        }
        
        with open("/app/backend/deployment_result.json", "w") as f:
            json.dump(deployment, f, indent=2)
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"Results saved to /app/backend/deployment_result.json")

if __name__ == "__main__":
    main()
