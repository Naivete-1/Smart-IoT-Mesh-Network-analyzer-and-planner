 # Smart IoT Mesh Network Analyzer and Planner

**Graduation Project — 2026**

A web-based IoT mesh network analysis and planning platform designed to **design, visualize, analyze, monitor, and optimize IoT mesh networks**.

The system combines network-analysis algorithms, real-time visualization, performance monitoring, hardware/network discovery, MQTT communication, and machine-learning-based signal prediction into a single engineering platform.

---

## 📌 Project Overview

IoT mesh networks can become difficult to design and maintain as the number of connected devices increases. Poor node placement, weak wireless signals, failed nodes, and inefficient routing can negatively affect network performance.

The **Smart IoT Mesh Network Analyzer and Planner** was developed to provide an interactive environment for designing and evaluating IoT mesh networks before and during deployment.

The platform allows users to:

* Create and visualize IoT network topologies
* Define different types of network nodes
* Establish and analyze multi-hop connections
* Visualize wireless signal coverage
* Identify weak signal areas
* Monitor network performance
* Test connectivity between devices
* Simulate network failures
* Automatically determine alternative routes
* Detect devices on a local network
* Import and export network configurations
* Integrate with IoT hardware and MQTT
* Predict signal behaviour using machine learning

---

## 🎯 Project Objectives

The main objectives of the project were to:

1. Develop an interactive platform for IoT mesh network planning.
2. Visualize network topology and device relationships.
3. Analyze connectivity and multi-hop communication paths.
4. Evaluate wireless signal coverage and identify weak areas.
5. Monitor network performance using latency, bandwidth, and packet-loss information.
6. Simulate node failures and evaluate network resilience.
7. Provide tools for network and IP-device discovery.
8. Support communication with IoT hardware.
9. Explore machine learning for wireless signal prediction.
10. Provide an extensible platform for future IoT network experimentation.

---

## ✨ Key Features

### 🌐 Mesh Network Design

Users can create and organize IoT devices within an interactive network environment.

Supported node types include:

* **Gateway**
* **Repeater / Node**
* **End Device**

Nodes can be positioned on the network canvas and connected to create a mesh topology.

### 🔀 Multi-Hop Routing

The system supports multi-hop path finding using a **Breadth-First Search (BFS)** approach.

This allows communication paths to be determined through intermediate nodes rather than requiring every device to connect directly to the gateway.

### 📡 Signal Coverage Analysis

The platform provides wireless signal visualization and identifies areas of different signal quality.

Signal conditions can be categorized as:

* Excellent
* Good
* Fair
* Weak

This can help identify potential coverage problems and improve node-placement decisions.

### 📊 Network Performance Monitoring

The system provides network performance information such as:

* Bandwidth
* Latency
* Packet loss
* Connectivity status

These metrics can be used to evaluate the health and performance of the network.

### 🔍 IP & Device Detection

The platform provides tools for checking network connectivity and discovering devices.

Users can:

* Test a specific IP address
* Ping devices
* Scan a local network
* Discover connected devices

Example:

```text
192.168.1.1
```

### 🚨 Network Failure Simulation

The platform can simulate node failures by removing a device from the network.

The system can then analyze the remaining topology and determine whether traffic can be rerouted through an alternative path.

This provides a simple way of evaluating **mesh-network resilience and fault tolerance**.

### 📡 Hardware Integration

The project includes support for integrating the software with IoT/network hardware.

The documented hardware environment includes:

* Wi-Fi router
* ESP32
* Arduino-based hardware

The hardware bridge can be used to connect the software platform with physical network/IoT components where supported by the implementation.

### 📨 MQTT Integration

MQTT functionality is included for IoT communication between the application and connected devices.

This provides a lightweight communication mechanism suitable for IoT environments.

### 🤖 Machine Learning Signal Prediction

The project includes a machine-learning component for wireless signal prediction.

The prediction component is designed to assist with analyzing signal behaviour and identifying potential coverage conditions.

The implementation uses a **Random Forest-based prediction model**.

### 💾 Network Data Management

Network configurations can be exported and imported using structured data files.

This allows network designs to be saved, reused, and tested without recreating the topology manually.

---

## 🏗️ System Architecture

The system is organized into several layers.

```text
┌───────────────────────────────────────────┐
│              CLIENT LAYER                 │
│       HTML • CSS • JavaScript             │
│       Tailwind • Chart.js                 │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│                API LAYER                  │
│          Flask REST API                   │
│       Flask-SocketIO / WebSockets         │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│           APPLICATION LAYER               │
│                                           │
│  Mesh Analyzer                            │
│  Hardware Bridge                          │
│  MQTT Handler                             │
│  ML Signal Predictor                      │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│               DATA LAYER                  │
│                 SQLite                    │
│             JSON Network Data             │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│             HARDWARE LAYER                │
│          Wi-Fi Router / IoT Devices       │
└───────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend

* Python
* Flask
* Flask-SocketIO
* Flask-CORS
* NetworkX
* SQLite
* MQTT
* Machine Learning / Random Forest

### Frontend

* HTML5
* CSS3
* JavaScript (ES6+)
* Tailwind CSS
* Chart.js
* Lucide Icons

### Networking

* TCP/IP networking concepts
* IP addressing
* Ping / connectivity testing
* Mesh routing
* Multi-hop communication
* Network topology analysis
* Wireless signal analysis

### Hardware / IoT

* Wi-Fi Router
* ESP32
* Arduino-based hardware
* MQTT communication

---

## 📁 Project Structure

```text
Smart-IoT-Mesh-Network-Analyzer/
│
├── backend/
│   ├── app.py
│   ├── mesh_analyzer.py
│   ├── hardware_bridge.py
│   ├── mqtt_handler.py
│   ├── database.py
│   ├── ml_predictor.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── dashboard.js
│   └── components/
│
├── Hardware/
│   ├── Wi-Fi Router
│   ├── ESP32
│   └── Arduino Mega
│
├── tests/
│   └── network.json
│
└── README.md
```

> The exact structure should match the files included in the final repository.

---

## 🔄 System Workflow

The general workflow of the platform is:

```text
Design Network
      ↓
Add IoT Devices
      ↓
Create Connections
      ↓
Analyze Topology
      ↓
Evaluate Signal Coverage
      ↓
Monitor Performance
      ↓
Test Connectivity
      ↓
Simulate Failures
      ↓
Find Alternative Routes
      ↓
Export / Save Network
```

---

## 🚀 Getting Started

### Requirements

* Python 3.8+
* Modern web browser
* Git
* Optional: Arduino IDE
* Optional: compatible IoT/network hardware

### 1. Clone the Repository

```bash
git clone https://github.com/Naivete-1/Smart-IoT-Mesh-Network-Analyzer.git
cd Smart-IoT-Mesh-Network-Analyzer
```

### 2. Create a Virtual Environment

```bash
cd backend
python -m venv venv
```

### 3. Activate the Environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Backend

```bash
python app.py
```

The backend is configured to run on:

```text
http://0.0.0.0:5000
```

### 6. Open the Frontend

Open:

```text
frontend/index.html
```

in a modern web browser, or use a local development server such as VS Code Live Server.

---

## 🧪 Using the Application

### Add Devices

Select a device type:

* Gateway
* Repeater / Node
* End Device

Add the device to the network canvas and position it as required.

### Create Connections

Devices can be connected based on the network topology and communication range.

The resulting mesh can then be analyzed by the application.

### Analyze Coverage

Switch to the coverage view to visualize signal conditions and identify weaker areas.

### Test Connectivity

Select a source and destination device and perform a ping test.

The application can display connectivity and round-trip-time information.

### Simulate a Failure

Remove a node from the topology to simulate a network failure.

The system can then analyze the remaining network and determine whether an alternative route exists.

### Export a Network

Network configurations can be exported for later reuse.

Previously saved configurations can also be imported into the application.

---

## 🔌 API Endpoints

| Method | Endpoint                  | Description                     |
| ------ | ------------------------- | ------------------------------- |
| GET    | `/api/network/status`     | Retrieve current network status |
| POST   | `/api/network/analyze`    | Analyze network topology        |
| GET    | `/api/hardware/discover`  | Discover IoT devices            |
| POST   | `/api/hardware/connect`   | Connect to hardware             |
| GET    | `/api/router/device/<ip>` | Test connectivity to an IP      |
| POST   | `/api/router/scan`        | Scan the network                |
| POST   | `/api/export/report`      | Generate/export a report        |

---

## 🧪 Testing

The project includes testing support for the backend.

From the `backend` directory:

```bash
python -m pytest test/ -v
```

Network test data can be provided through:

```text
tests/network.json
```

---

## 🧠 Engineering Concepts Demonstrated

This project combines several areas of computer engineering and software development:

* IoT networking
* Mesh network architecture
* Graph theory
* BFS path finding
* Network topology analysis
* Wireless signal analysis
* IP networking
* Connectivity testing
* Fault tolerance
* Network performance monitoring
* REST API development
* WebSocket communication
* MQTT
* Database management
* Machine learning
* Interactive data visualization
* Hardware/software integration
* Frontend and backend development

---

## 🎓 Academic Context

**Project:** Smart IoT Mesh Network Analyzer and Planner
**Project Type:** Graduation / Final-Year Project
**Year:** 2026
**Degree:** BSc Computer Engineering

The project was developed as a practical application of computer engineering concepts involving **networking, IoT, software development, algorithms, databases, and intelligent network analysis**.

---

## 📸 Screenshots

Screenshots of the application interface and network-analysis features can be added here.

Recommended examples include:

* Main dashboard
* Mesh topology
* Signal coverage analysis
* Network performance dashboard
* IP detection
* Failure simulation
* Network routing

Example:

```markdown
![Application Dashboard](screenshots/dashboard.png)
```

---

## 🔮 Future Improvements

Potential future development includes:

* Advanced automated node-placement optimization
* More sophisticated wireless propagation models
* Real-time physical sensor data integration
* Additional machine-learning models
* Expanded network security analysis
* Improved mobile responsiveness
* Advanced network-performance analytics
* Automated network optimization recommendations

---

## 👩‍💻 Author

**Naivete Thandiwe Makobe**

BSc Computer Engineering — 2026

Areas of interest:

* Software Development
* Networking
* IoT
* Computer Engineering
* Artificial Intelligence
* IT Systems

---

## ⭐ Project Highlights

This project demonstrates the ability to develop a complete engineering application that connects:

**Frontend → Backend → Network Algorithms → Database → IoT Communication → Machine Learning → Physical Network Environment**

It combines theoretical computer-engineering concepts with a practical software platform for **IoT mesh network planning, analysis, and optimization**.
