// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title PatientWallet
 * @dev Simple smart contract wallet for patients
 */
contract PatientWallet {
    address public owner;
    address public guardian; // Can be a doctor or the platform
    bool public isActive;
    
    event TransactionExecuted(address indexed to, uint256 value, bytes data);
    event GuardianUpdated(address indexed newGuardian);
    event WalletDeactivated();
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier onlyOwnerOrGuardian() {
        require(msg.sender == owner || msg.sender == guardian, "Not authorized");
        _;
    }
    
    constructor(address _owner, address _guardian) {
        owner = _owner;
        guardian = _guardian;
        isActive = true;
    }
    
    function execute(address to, uint256 value, bytes calldata data) external onlyOwner returns (bytes memory) {
        require(isActive, "Wallet deactivated");
        (bool success, bytes memory result) = to.call{value: value}(data);
        require(success, "Transaction failed");
        emit TransactionExecuted(to, value, data);
        return result;
    }
    
    function updateGuardian(address newGuardian) external onlyOwnerOrGuardian {
        guardian = newGuardian;
        emit GuardianUpdated(newGuardian);
    }
    
    function deactivate() external onlyOwnerOrGuardian {
        isActive = false;
        emit WalletDeactivated();
    }
    
    receive() external payable {}
}

/**
 * @title PatientWalletFactory
 * @dev Factory for deploying patient smart contract wallets
 */
contract PatientWalletFactory {
    address public owner;
    address public defaultGuardian;
    
    mapping(address => address) public patientToWallet;
    mapping(address => address) public walletToPatient;
    address[] public allWallets;
    
    event WalletCreated(address indexed patient, address indexed wallet, address guardian);
    
    constructor(address _defaultGuardian) {
        owner = msg.sender;
        defaultGuardian = _defaultGuardian;
    }
    
    /**
     * @dev Create a new patient wallet
     * @param patientEOA The patient's externally owned account address
     * @param guardian Optional guardian address (uses default if zero)
     */
    function createWallet(address patientEOA, address guardian) external returns (address) {
        require(patientToWallet[patientEOA] == address(0), "Wallet already exists");
        
        address guardianAddr = guardian == address(0) ? defaultGuardian : guardian;
        
        PatientWallet wallet = new PatientWallet(patientEOA, guardianAddr);
        address walletAddr = address(wallet);
        
        patientToWallet[patientEOA] = walletAddr;
        walletToPatient[walletAddr] = patientEOA;
        allWallets.push(walletAddr);
        
        emit WalletCreated(patientEOA, walletAddr, guardianAddr);
        
        return walletAddr;
    }
    
    /**
     * @dev Get wallet address for a patient
     */
    function getWallet(address patientEOA) external view returns (address) {
        return patientToWallet[patientEOA];
    }
    
    /**
     * @dev Get total number of wallets created
     */
    function getWalletCount() external view returns (uint256) {
        return allWallets.length;
    }
    
    /**
     * @dev Update default guardian
     */
    function setDefaultGuardian(address newGuardian) external {
        require(msg.sender == owner, "Only owner");
        defaultGuardian = newGuardian;
    }
}
