# Operations & Supply Chain Optimizer

> A business optimization tool that helps operations teams minimize delivery costs and right-size staffing using real Operations Research methods — Vehicle Routing Optimization and Queueing Theory.

Built as a portfolio project demonstrating applied Operations Research for business decision-making.

---

## What Problem Does This Solve?

Operations teams make two costly decisions every day, usually by gut feeling instead of data:

1. **"What order should we visit these delivery stops in?"** — inefficient routing wastes fuel, time, and money
2. **"How many staff do we need today?"** — overstaffing wastes payroll, understaffing creates long wait times and lost customers

This tool answers both questions with real optimization math — not guesswork.

---

## Features

### Route Optimization
- Upload delivery locations (CSV) or use sample data
- Solves the Vehicle Routing Problem (VRP) using Google OR-Tools
- Supports multiple vehicles with capacity constraints
- Shows the optimized route on an interactive map
- Reports exact distance saved vs. an unoptimized route

### Staffing Calculator
- Input arrival rate and service rate
- Uses M/M/s queueing theory (Erlang-C) — the same math used in call centre and bank staffing
- Recommends the minimum staff needed to hit your target wait time
- Visual chart showing the trade-off between staff count and wait time

### What-If Scenario Analysis
- Test "what happens if demand increases 20%?"
- Instantly see if current staffing can handle it
- Get a specific recommendation: how many more staff are needed
- Correctly flags system overload when demand exceeds capacity

---

## The Math Behind It

### Route Optimization
Solves the Vehicle Routing Problem (VRP): minimizes total distance across all vehicles, respects capacity constraints, uses geodesic distance for real-world accuracy, solved with OR-Tools' Guided Local Search metaheuristic.

### Staffing Calculator — M/M/s Queueing Model
Uses the Erlang-C formula, the industry-standard model for call centres, bank tellers, and customer service:
---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python main.py
# API: http://localhost:8002  |  Docs: http://localhost:8002/docs
```

### Frontend
```bash
cd frontend
npm install
npm start
# http://localhost:3000
```

---

## Project Structure
---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | System status |
| `/route/optimize` | POST | Optimize delivery route(s) |
| `/staffing/calculate` | POST | Calculate optimal staffing |
| `/scenario/whatif` | POST | Compare current vs projected demand scenario |

---

## Example Use Case

A local delivery business has 6 stops from their warehouse, and their service line receives 40 calls/hour with each staff member handling 12 calls/hour.

1. **Route tab** — uploads 6 delivery addresses, gets an optimized route saving 9%+ distance
2. **Staffing tab** — enters 40 arrivals/hr, 12 service/hr, tool recommends 4 staff for under 5-minute wait
3. **What-If tab** — tests a 20% holiday demand spike, tool warns current staffing would be overwhelmed and recommends additional staff

---

## Roadmap

- Multi-depot routing support
- Time-window delivery constraints
- Export optimized route as PDF/GPX
- Historical demand upload for automatic rate estimation
- Cost-based optimization (fuel, wages)

---

## Author

**Andrew Nelson Enoh** — MSc Industrial Data Science, Montanuniversität Leoben
[GitHub](https://github.com/optilinkboyz) · nelsonenoh@gmail.com
