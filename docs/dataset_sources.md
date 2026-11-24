# Dataset Sources, Licenses & Provenance

## 1. Overview
MetroGraph Analytics strictly adheres to open academic data standards. The system forbids runtime web scraping, unverified API calls, and live OpenStreetMap tile downloading.

---

## 2. Ingested Datasets

### A. Delhi Metro Network Dataset (Normalized)
- **Directory**: `data/metro/`
- **Source**: Delhi Metro Rail Corporation (DMRC) open data releases aggregated by the open transit data community.
- **Reference Repository**: `https://raw.githubusercontent.com/heyamay/Delhi-Metro-Network-Analysis/main/Delhi-Metro-Network.csv`
- **Access Date**: November 20, 2026
- **License**: Open Data Commons Open Database License (ODbL) / Public Community Transit Data
- **Coverage**: National Capital Region (NCR), Delhi, Noida, Greater Noida, Gurgaon
- **Scale**: 260 stations, 13 lines, 273 connections, 285 station-line memberships
- **Weight Provenance**:
  - Distances: Successive differences from start-of-line station coordinates (`published` and `derived`).
  - Travel Times: Modeled at 35 km/h commercial average operating speed with 1.0 min station dwell time.
  - Inter-line Transfers: Noida Sector 51 (Aqua Line) to Noida Sector 52 (Blue Line) includes a 300-meter dedicated pedestrian link.

### B. Synthetic Sample Network (Phase 1 Baseline)
- **Directory**: `data/sample/`
- **Source**: MetroGraph Academic Project Team
- **License**: MIT Open Source Academic License
- **Purpose**: Offline unit testing, schematic baseline, and regression verification.
- **Scale**: 12 stations, 3 lines, 14 connections, 4 interchange hubs.

---

## 3. Data Integrity & Provenance Tracking
Each dataset maintains a `metadata.json` containing:
- Source URL and organization
- Access date and versioning
- Geographic bounding
- Data limitations and modeling assumptions
- SHA-256 fingerprint for cache invalidation
