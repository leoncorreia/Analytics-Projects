# 🚢 Resilience: Distributed Supply Chain Simulator

A real-time distributed systems simulation that visualizes global logistics, cascading failures, and self-healing routing algorithms.

![Supply Chain Simulation Screenshot](./image_8e2c59.jpg)

## 💡 Concept

This project applies the actor model to global trade by simulating a distributed network where:

* Nodes represent major global ports with active or inactive states.
* Edges are shipping lanes weighted by Haversine distance.
* Agents are autonomous ships that compute optimal paths using Dijkstra’s algorithm.

The system demonstrates resilience engineering. When a user blocks a port (simulating a strike or disaster), the backend broadcasts that failure. All affected agents immediately recalculate their routes and avoid the disruption.

---

## 🛠 Tech Stack

### Backend (Simulation Engine)

* Go (Golang)
* Goroutines for independent agent behavior
* Channels for state management
* WebSockets (Gorilla) for real-time state streaming at 60Hz
* Custom Dijkstra implementation for routing

### Frontend (Visualization Layer)

* React + Vite
* Deck.gl for large-scale WebGL rendering
* MapLibre GL with a CartoDB Dark Matter basemap
* Layers for ship icons, geodesic arcs, and interactive ports

---

## 🚀 Features

* Real-time physics with dozens of concurrent agents
* Click any white port to toggle a blockade and trigger instant rerouting
* Directional ship icons and 3D route arcs
* Live heads-up display showing active agents and port status

---

## 📦 How to Run

### 1. Start the Backend (Go)

The backend computes movement, routing, and state transitions.

```bash
cd supply-chain-simulation
go run .
```

You should see logs confirming agents are initialized and WebSocket updates are streaming.

---

### 2. Start the Frontend (React)

This renders the visualization layer.

```bash
cd frontend
npm install
npm run dev
```

Open the localhost link shown in the terminal (typically `http://localhost:5173`).

---

## 🧠 Distributed Systems Concepts

### State Management

The backend maintains the complete source of truth for the graph.
The frontend is a renderer that reflects server state without owning logic.

### Backpressure and Flow

Each agent ticks independently. If computation slows, the system naturally experiences backpressure.

### Event Propagation

A blockade event is broadcast system-wide. Agents adjust asynchronously and recompute their paths.

---

## 🔮 Future Improvements

### Latency Simulation

Introduce network delay to experiment with stale route data.

### Capacity Limits

Add queueing at ports to model congestion and backpressure.

### Persistent Database

Log trip history, events, and efficiency metrics in SQLite or PostgreSQL.
