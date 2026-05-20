# Dual-Ledger Automated Toll Evasion Detection & Blockchain Audit Framework 🛣️⛓️

A smart-infrastructure transportation analytics system designed to detect and log highway toll road evasion across distributed camera feeds. The platform uses a hybrid architecture combining computer vision text extraction with modern data persistence and decentralized cryptographic consensus.

The framework tracks vehicles across an **Entry Camera**, a **Payment Booth Camera**, and an **Exit Camera**. By cross-referencing recognized license plate strings using string distance similarity matrices, it isolates vehicles that skipped payment. Violations are saved to a dual-ledger pipeline: high-scale document storage (**MongoDB**) and an immutable decentralized architecture (**Ethereum/Ganache**).

---

## 🛠️ System Architecture & Tech Stack

*   **ANPR Processing Core:** Powered by **EasyOCR** (leveraging a localized deep learning text detection engine) combined with regex-driven validation rules optimized for Indian Standard registration plates.
*   **Cross-Camera Analytics:** Processes distinct video feeds concurrently, applying a string-matching algorithm (`difflib.SequenceMatcher`) to catch discrepancies between entry gates, transaction logs, and exit gates.
*   **Localized Persistence Layer:** Logs complete incident telemetry histories, status flags, and timestamps within **MongoDB**.
*   **Decentralized Ledger Notary:** Connects natively via **Web3.py** to sign transactions offline, broadcasting cryptographic asset receipts straight into an Ethereum node.
*   **Auditor Web Interface:** A lightweight, non-blocking asynchronous **Flask API Web Server** featuring dynamic HTML polling updates and an authenticated server-side stream engine to compile secure CSV audit reports.

---

## 🔄 Core Data Pipeline

```text
  [Entry/Booth/Exit Videos]
             │
             ▼
     [EasyOCR Extraction]
             │
             ▼
  [SequenceMatcher Evaluation] ──(Match Found)──► [Clean Pass / Logged to CSV]
             │
       (Evasion Caught)
             │
             ▼
   ┌───────────────────┐
   │  Violation Event  │
   └─────────┬─────────┘
             ├────────────────────────────────────────┐
             ▼                                        ▼
 ┌───────────────────────┐                ┌───────────────────────┐
 │   Ethereum Blockchain │                │     MongoDB Server    │
 │ (Offline TX Signing)  │                │  (Incident Telemetry) │
 └───────────┬───────────┘                └───────────┬───────────┘
             │                                        │
             └──────────► [Linked via Block Hash] ◄───┘
                                      │
                                      ▼
                        [Flask Auditor Web Dashboard]
