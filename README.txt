# MedVault - Intelligent Medical Inventory and Redistribution System

MedVault is a real-world, DSA-powered simulation of a medicine inventory and redistribution system designed for hospitals, warehouses, and clinics. It supports intelligent routing, optimized stock fulfillment, and batch-level medicine tracking based on expiry, quality, and urgency.

## Overview

MedVault manages and redistributes medicines between facilities based on supply, demand, and logistical efficiency. It supports real-time routing, dynamic facility updates, and handles real-world constraints such as blocked batches, reserved stock, and partial fulfillment.

## Key Features

- Multi-factor medicine batch prioritization using expiry, quality score, and flags (reserved/blocked)
- Greedy-based partial fulfillment from multiple sources when a single source is insufficient
- Dijkstra-based shortest path algorithm for delivery routing
- Dynamic graph management allowing runtime addition of new locations and routes
- Alert system for low stock, near-expiry batches, and flagged (reserved/blocked) inventory

## Data Structures and Algorithms Used

- **MinHeap (via custom class ordering):** for batch priority sorting
- **Hash Maps (`defaultdict`):** for efficient inventory lookup and categorization
- **Dijkstra’s Algorithm:** for computing shortest delivery paths
- **Greedy Aggregation Logic:** for optimal source selection and partial fulfillment
- **Graph (Adjacency List):** to represent the facility network dynamically

## Project Modules

- `medicine.py` – Defines the `Medicine` class and implements batch priority logic
- `inventory.py` – Manages stock at multiple locations, supports deduction and batch selection
- `graph_routes.py` – Implements a modular, expandable graph with Dijkstra’s algorithm
- `redistribution.py` – Handles smart fulfillment decisions across the network
- `alerts.py` – Generates real-time alerts for expiry, low stock, and special flags
- `main.py` – Demo script showcasing the full functionality of the system

## Example Scenarios Handled

1. A warehouse has only partial stock of a required medicine. MedVault automatically combines from multiple sources.
2. A new clinic is added during an emergency. MedVault routes deliveries immediately without requiring reinitialization.
3. Some batches are reserved for ICU or flagged due to recalls. MedVault deprioritizes or blocks them as per configuration.
4. The shortest and most efficient delivery path is always selected using Dijkstra’s algorithm.
5. Facilities receive alerts on stock nearing expiry or falling below threshold.

## How to Run

1. Clone the repository or place all `.py` files in the same directory.
2. Make sure you are using Python 3.8 or later.
3. Run the demo:
   ```bash
   python main.py
