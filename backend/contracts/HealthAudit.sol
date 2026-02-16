// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HealthAudit
 * @dev Stores critical medical alert hashes on-chain for tamper-proof audit trail
 * Deployed on opBNB for OmniHealth Guardian
 */
contract HealthAudit {
    address public owner;
    
    struct AlertRecord {
        bytes32 alertHash;      // SHA-256 hash of the alert data
        address patient;        // Patient's smart wallet address
        uint256 timestamp;      // Block timestamp
        string alertType;       // Type: "critical_glucose", "irregular_heartbeat", etc.
        bool verified;          // Verification status
    }
    
    // Mapping from alert ID to AlertRecord
    mapping(uint256 => AlertRecord) public alerts;
    uint256 public alertCount;
    
    // Mapping from patient address to their alert IDs
    mapping(address => uint256[]) public patientAlerts;
    
    // Events
    event AlertRecorded(
        uint256 indexed alertId,
        bytes32 alertHash,
        address indexed patient,
        string alertType,
        uint256 timestamp
    );
    
    event AlertVerified(uint256 indexed alertId, address verifier);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Record a new critical alert on-chain
     * @param alertHash SHA-256 hash of the alert data
     * @param patient Patient's smart wallet address
     * @param alertType Type of alert (e.g., "high_glucose", "low_battery")
     */
    function recordAlert(
        bytes32 alertHash,
        address patient,
        string memory alertType
    ) external returns (uint256) {
        alertCount++;
        
        alerts[alertCount] = AlertRecord({
            alertHash: alertHash,
            patient: patient,
            timestamp: block.timestamp,
            alertType: alertType,
            verified: true
        });
        
        patientAlerts[patient].push(alertCount);
        
        emit AlertRecorded(alertCount, alertHash, patient, alertType, block.timestamp);
        
        return alertCount;
    }
    
    /**
     * @dev Get alert details by ID
     */
    function getAlert(uint256 alertId) external view returns (
        bytes32 alertHash,
        address patient,
        uint256 timestamp,
        string memory alertType,
        bool verified
    ) {
        AlertRecord storage alert = alerts[alertId];
        return (
            alert.alertHash,
            alert.patient,
            alert.timestamp,
            alert.alertType,
            alert.verified
        );
    }
    
    /**
     * @dev Get all alert IDs for a patient
     */
    function getPatientAlerts(address patient) external view returns (uint256[] memory) {
        return patientAlerts[patient];
    }
    
    /**
     * @dev Verify an alert hash matches stored hash
     */
    function verifyAlertHash(uint256 alertId, bytes32 hashToVerify) external view returns (bool) {
        return alerts[alertId].alertHash == hashToVerify;
    }
}
