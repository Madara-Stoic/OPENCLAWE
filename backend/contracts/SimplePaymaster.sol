// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SimplePaymaster
 * @dev Sponsors gas fees for critical medical alerts
 * Part of OmniHealth Guardian Account Abstraction system
 */
contract SimplePaymaster {
    address public owner;
    mapping(address => bool) public whitelistedCallers;
    uint256 public totalSponsored;
    
    event GasSponsored(address indexed user, uint256 amount, string reason);
    event CallerWhitelisted(address indexed caller);
    event CallerRemoved(address indexed caller);
    event FundsDeposited(address indexed from, uint256 amount);
    event FundsWithdrawn(address indexed to, uint256 amount);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Deposit funds for gas sponsorship
     */
    function deposit() external payable {
        emit FundsDeposited(msg.sender, msg.value);
    }
    
    /**
     * @dev Whitelist a caller (e.g., HealthAudit contract)
     */
    function whitelistCaller(address caller) external onlyOwner {
        whitelistedCallers[caller] = true;
        emit CallerWhitelisted(caller);
    }
    
    /**
     * @dev Remove caller from whitelist
     */
    function removeCaller(address caller) external onlyOwner {
        whitelistedCallers[caller] = false;
        emit CallerRemoved(caller);
    }
    
    /**
     * @dev Sponsor gas for a transaction (simplified version)
     * In production, this would integrate with ERC-4337 EntryPoint
     */
    function sponsorGas(address user, uint256 gasAmount, string memory reason) external {
        require(whitelistedCallers[msg.sender] || msg.sender == owner, "Not authorized");
        require(address(this).balance >= gasAmount, "Insufficient funds");
        
        totalSponsored += gasAmount;
        emit GasSponsored(user, gasAmount, reason);
    }
    
    /**
     * @dev Withdraw funds (owner only)
     */
    function withdraw(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Insufficient balance");
        payable(owner).transfer(amount);
        emit FundsWithdrawn(owner, amount);
    }
    
    /**
     * @dev Get contract balance
     */
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
    
    receive() external payable {
        emit FundsDeposited(msg.sender, msg.value);
    }
}
