# Prometheus & Grafana Monitoring Guide

A comprehensive guide to setting up monitoring for your applications using Prometheus and Grafana on AWS.

---

## Table of Contents

1. [Key Concepts](#key-concepts)
2. [Prometheus Setup](#prometheus-setup)
3. [Grafana Setup](#grafana-setup)
4. [Connecting Prometheus to Grafana](#connecting-prometheus-to-grafana)
5. [Creating Dashboards](#creating-dashboards)
6. [Cleanup](#cleanup)
7. [Cost Reference](#cost-reference)
8. [Troubleshooting](#troubleshooting)

---

## Key Concepts

### What is Prometheus?

**Prometheus** is an open-source monitoring and alerting system. It collects metrics from your applications.

| Feature | Description |
|---------|-------------|
| **Time-series database** | Stores metrics with timestamps |
| **Pull-based** | Scrapes metrics from endpoints |
| **PromQL** | Query language for metrics |
| **Alerting** | Triggers alerts based on rules |

### What is Grafana?

**Grafana** is an open-source visualization tool. It creates beautiful dashboards from metrics data.

| Feature | Description |
|---------|-------------|
| **Dashboards** | Visual representation of metrics |
| **Data sources** | Connects to Prometheus, databases, etc. |
| **Alerts** | Visual alerts and notifications |
| **Plugins** | Extensible with plugins |

### How They Work Together

```
Your Flask App                Prometheus               Grafana
     |                            |                        |
     | /metrics endpoint          |                        |
     |<------ Scrapes every 15s --|                        |
     |                            |                        |
     |                            | Stores time-series     |
     |                            |                        |
     |                            |<----- Queries data ----|
     |                            |                        |
     |                            |----> Returns metrics -->|
     |                            |                        |
     |                            |                   Displays
     |                            |                   Dashboard
```

### Flask Metrics Endpoint

For Prometheus to scrape your Flask app, you need a `/metrics` endpoint:

```python
# Add to flask_app/app.py
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Define metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total Flask Requests')
PREDICTION_COUNT = Counter('predictions_total', 'Total Predictions Made')

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
```

---

## Prometheus Setup

### Step 1: Launch EC2 Instance

**AWS Console** → **EC2** → **Launch Instance**

| Setting | Value |
|---------|-------|
| Name | `prometheus-server` |
| AMI | Ubuntu Server 22.04 LTS |
| Instance Type | t3.medium |
| Key Pair | Create or select existing |
| Storage | 20 GB gp3 |

**Security Group Rules:**

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Your IP | SSH access |
| Custom TCP | 9090 | 0.0.0.0/0 | Prometheus UI |

### Step 2: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

Or use **EC2 Instance Connect** from AWS Console.

### Step 3: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 4: Download Prometheus

```bash
# Download latest Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz

# Extract
tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz

# Rename for convenience
mv prometheus-2.46.0.linux-amd64 prometheus
```

### Step 5: Move Files

```bash
sudo mv prometheus /etc/prometheus
sudo mv /etc/prometheus/prometheus /usr/local/bin/
```

### Step 6: Configure Prometheus

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add this configuration:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "flask-app"
    static_configs:
      - targets: ["YOUR_APP_URL:5000"]  # Replace with your app URL
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

### Step 7: Start Prometheus

```bash
/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml &
```

### Step 8: Verify Prometheus

Open browser: `http://<EC2-PUBLIC-IP>:9090`

You should see the Prometheus UI.

---

## Grafana Setup

### Step 1: Launch EC2 Instance

**AWS Console** → **EC2** → **Launch Instance**

| Setting | Value |
|---------|-------|
| Name | `grafana-server` |
| AMI | Ubuntu Server 22.04 LTS |
| Instance Type | t3.medium |
| Key Pair | Same as Prometheus |
| Storage | 20 GB gp3 |

**Security Group Rules:**

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Your IP | SSH access |
| Custom TCP | 3000 | 0.0.0.0/0 | Grafana UI |

### Step 2: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@<GRAFANA-EC2-IP>
```

### Step 3: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 4: Download and Install Grafana

```bash
# Download Grafana
wget https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb

# Install
sudo apt install ./grafana_10.1.5_amd64.deb -y
```

### Step 5: Start Grafana

```bash
# Start service
sudo systemctl start grafana-server

# Enable on boot
sudo systemctl enable grafana-server

# Check status
sudo systemctl status grafana-server
```

### Step 6: Access Grafana

Open browser: `http://<GRAFANA-EC2-IP>:3000`

**Default Login:**
- Username: `admin`
- Password: `admin`

You'll be prompted to change the password.

---

## Connecting Prometheus to Grafana

### Step 1: Add Data Source

1. Go to **Configuration** (gear icon) → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**

### Step 2: Configure Connection

| Setting | Value |
|---------|-------|
| Name | Prometheus |
| URL | `http://<PROMETHEUS-EC2-IP>:9090` |
| Access | Server (default) |

### Step 3: Save & Test

Click **Save & Test**. You should see "Data source is working".

---

## Creating Dashboards

### Step 1: Create New Dashboard

1. Click **+** → **Dashboard**
2. Click **Add visualization**
3. Select **Prometheus** data source

### Step 2: Add Panels

**Example Panel - Request Rate:**

```promql
rate(flask_requests_total[5m])
```

**Example Panel - Prediction Count:**

```promql
predictions_total
```

### Step 3: Save Dashboard

Click **Save dashboard** and give it a name.

### Recommended Dashboard Panels

| Panel Type | Query | Title |
|------------|-------|-------|
| **Gauge** | `up` | Service Status |
| **Stat** | `prometheus_http_requests_total` | Total Requests |
| **Time Series** | `process_resident_memory_bytes / 1024 / 1024` | Memory Usage (MB) |
| **Time Series** | `rate(prometheus_http_requests_total[5m])` | Request Rate |

### PromQL Quick Reference

| Query | What it shows |
|-------|---------------|
| `up` | Target status (1=up, 0=down) |
| `rate(metric[5m])` | Per-second rate over 5 minutes |
| `increase(metric[1h])` | Total increase over 1 hour |
| `sum(metric)` | Sum of all instances |
| `avg(metric)` | Average across instances |
| `max(metric)` | Maximum value |
| `histogram_quantile(0.95, metric)` | 95th percentile |

---

## Cleanup

### IMPORTANT: Delete EC2 Instances After Demo

EC2 instances cost money every hour. Always delete when done:

### Step 1: Terminate Prometheus EC2

**AWS Console** → **EC2** → **Instances**
1. Select `prometheus-server`
2. **Instance State** → **Terminate instance**

### Step 2: Terminate Grafana EC2

1. Select `grafana-server`
2. **Instance State** → **Terminate instance**

### Step 3: Verify Termination

Check that both instances show "Terminated" status.

---

## Cost Reference

| Resource | Cost | Notes |
|----------|------|-------|
| EC2 t3.medium (Prometheus) | ~$0.04/hour | ~$1/day |
| EC2 t3.medium (Grafana) | ~$0.04/hour | ~$1/day |
| **Total** | **~$0.08/hour** | **~$2/day** |

### Cost-Saving Tips

1. Use t3.micro for testing (~$0.01/hour)
2. Stop instances when not in use
3. Terminate after demo - do not leave running overnight

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't access Prometheus UI | Security group | Add port 9090 inbound rule |
| Can't access Grafana UI | Security group | Add port 3000 inbound rule |
| Prometheus not scraping | Wrong target URL | Check prometheus.yml configuration |
| Grafana can't connect | Prometheus not running | Restart Prometheus service |

### Verify Prometheus is Running

```bash
ps aux | grep prometheus
```

### Verify Grafana is Running

```bash
sudo systemctl status grafana-server
```

### Check Prometheus Targets

Open: `http://<PROMETHEUS-IP>:9090/targets`

All targets should show "UP".

---

## Quick Reference Commands

```bash
# Prometheus
/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml &

# Grafana
sudo systemctl start grafana-server
sudo systemctl status grafana-server
sudo systemctl stop grafana-server
```

---

## Related Documentation

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Flask Prometheus Client](https://github.com/prometheus/client_python)
