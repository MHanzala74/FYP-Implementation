// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * ASTRA — ThreatLog Smart Contract
 * Stores each detected threat immutably on the blockchain.
 * BS CS AWKUM 2022-26
 */
contract ThreatLog {

    // ── Struct: a single threat record ─────────────────────────────────
    struct ThreatRecord {
        uint256 timestamp;          // Unix timestamp
        string  threatType;         // "dos", "ddos", "bruteforce", etc.
        string  severity;           // "none", "medium", "high", "critical"
        string  rfPrediction;       // Random Forest result
        string  xgbPrediction;      // XGBoost result
        uint256 rfConfidence;       // RF confidence * 10000 (e.g. 9876 = 98.76%)
        uint256 xgbConfidence;      // XGB confidence * 10000
        string  recommendedAction;  // Automated response suggestion
        bool    isThreat;           // True if it is a threat
    }

    // ── Storage ─────────────────────────────────────────────────────
    ThreatRecord[] public records;
    address public owner;

    // ── Events (for frontend/logs) ──────────────────────────────
    event ThreatLogged(
        uint256 indexed recordId,
        uint256 timestamp,
        string  threatType,
        string  severity,
        bool    isThreat
    );

    // ── Constructor ─────────────────────────────────────────────────
    constructor() {
        owner = msg.sender;
    }

    // ── Log a threat ─────────────────────────────────────────────────
    function logThreat(
        string memory _threatType,
        string memory _severity,
        string memory _rfPrediction,
        string memory _xgbPrediction,
        uint256 _rfConfidence,
        uint256 _xgbConfidence,
        string memory _recommendedAction,
        bool _isThreat
    ) public returns (uint256) {

        ThreatRecord memory rec = ThreatRecord({
            timestamp:         block.timestamp,
            threatType:        _threatType,
            severity:          _severity,
            rfPrediction:      _rfPrediction,
            xgbPrediction:     _xgbPrediction,
            rfConfidence:      _rfConfidence,
            xgbConfidence:     _xgbConfidence,
            recommendedAction: _recommendedAction,
            isThreat:          _isThreat
        });

        records.push(rec);
        uint256 recordId = records.length - 1;

        emit ThreatLogged(recordId, block.timestamp, _threatType, _severity, _isThreat);
        return recordId;
    }

    // ── Get a single record ────────────────────────────────────────────
    function getRecord(uint256 _id) public view returns (ThreatRecord memory) {
        require(_id < records.length, "Record does not exist");
        return records[_id];
    }

    // ── Get total record count ────────────────────────────────────────
    function getTotalRecords() public view returns (uint256) {
        return records.length;
    }

    // ── Get count of only threat records ──────────────────────────────
    function getThreatCount() public view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < records.length; i++) {
            if (records[i].isThreat) count++;
        }
        return count;
    }
}