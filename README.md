# 🐳 Movie Platform: Containerized Microservices

**Platform:** Docker
**Orchestration:** Docker Compose
**Language:** Python 3.10

A containerized implementation of a **Movie Streaming Platform**.
This project migrates services from **Virtual Machines** to **Docker Containers**, orchestrated with **Docker Compose**, all running on a **single Linux host**.

---

## 🏗 System Architecture

All services run as **isolated containers** connected through a user-defined Docker bridge network:

**`app_network`**

### Services Overview

**API Gateway**

* Container: `api-gateway-app`
* Internal Port: 3000
* Exposed Port: **3000 (Host)**
* Role: Entry point for clients. Routes HTTP requests to Inventory and sends async messages to RabbitMQ.

**Inventory API**

* Container: `inventory-app`
* Internal Port: 8080
* Role: Internal REST API managing movie metadata.

**Inventory Database**

* Container: `inventory-db`
* Port: 5432
* Role: PostgreSQL database storing movie inventory data.

**Billing Worker**

* Container: `billing-app`
* Role: Background service consuming billing jobs from the message queue.

**Billing Database**

* Container: `billing-db`
* Port: 5432
* Role: PostgreSQL database storing billing and order records.

**Message Broker**

* Container: `rabbit-queue`
* Port: 5672
* Role: RabbitMQ broker enabling asynchronous communication between services.

---

## 🚀 Prerequisites

* **Vagrant & VirtualBox**
  Used to provision a clean Linux VM acting as the Docker host.

* **Docker & Docker Compose**
  Installed automatically inside the VM during provisioning.

---

## 🛠 Installation & Setup

### Step 1: Provision the Docker Host

A Ubuntu VM (`docker-vm`) is created using Vagrant.

```
cd play-with-containers
vagrant up
vagrant ssh docker-vm
```

---

### Step 2: Build & Start Containers

Inside the VM, Docker Compose builds the images and starts all services.

```
cd /app
docker compose up -d --build
```

**Flags Explained:**

* `--build` → Forces rebuilding of custom images (gateway, inventory, billing)
* `-d` → Runs containers in detached (background) mode

---

### Step 3: Verify Running Containers

```
docker compose ps
```

All **6 containers** should be running.

---

## 📡 Usage

The **API Gateway** is exposed on your host machine at:

**[http://localhost:3000](http://localhost:3000)**

---

### Create a Movie (Synchronous)

```
curl -X POST http://localhost:3000/api/movies \
-H "Content-Type: application/json" \
-d '{"title": "Docker Inception", "description": "Containers within Containers"}'
```

---

### Submit an Order (Asynchronous)

```
curl -X POST http://localhost:3000/api/billing \
-H "Content-Type: application/json" \
-d '{"user_id": "DOCKER_USER", "number_of_items": "5", "total_amount": "50.00"}'
```

The request is processed asynchronously via RabbitMQ.

---

## 💾 Data Persistence & Volumes

Persistent storage is handled using **Docker Volumes**.

* **inventory-data** → Stores Inventory PostgreSQL data
* **billing-data** → Stores Billing PostgreSQL data
* **gateway-logs** → Stores API Gateway access logs

Data survives container restarts and rebuilds.

### Reset Everything

```
docker compose down -v
```

---

## 🧠 Design Decisions

**Debian vs Alpine**
We use `python:3.10-slim-bullseye` instead of Alpine to ensure smooth compatibility with `psycopg2` without complex compilation steps.

**Robust Startup Handling**
The Billing service implements a retry loop to avoid crash-loops while waiting for the database to become ready.

**Security**
Database credentials are injected via a `.env` file and are never hardcoded into Dockerfiles.

---

## 👤 Author

**Cliff Doyle**
