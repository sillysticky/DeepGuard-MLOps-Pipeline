# DagsHub & MLflow Setup Guide

> **Purpose**: Step-by-step instructions for setting up DagsHub and MLflow integration for experiment tracking and model registry.

---

## 📋 Prerequisites

- Python 3.8+ installed
- Git installed and configured
- DagsHub account (free tier available)
- Kaggle account (for dataset access)

---

## 🚀 Step 1: Create DagsHub Repository

### 1.1 Sign Up / Login

1. Go to [dagshub.com](https://dagshub.com)
2. Sign up with GitHub, GitLab, or email
3. Verify your email address

### 1.2 Create New Repository

1. Click **"New Repository"** or **"+"** button
2. Fill in repository details:
   - **Name**: `DeepGuard-MLOps-Pipeline`
   - **Description**: AI-generated image detection with MLOps
   - **Visibility**: Public or Private
3. Click **"Create Repository"**

### 1.3 Get Your Credentials

1. Go to your repository settings
2. Navigate to **"Integrations"** → **"MLflow"**
3. Note down:
   - **Tracking URI**: `https://dagshub.com/<username>/<repo>.mlflow`
   - **Username**: Your DagsHub username
   - **Token**: Generate an access token if needed

---

## 🔧 Step 2: Configure Local Environment

### 2.1 Create `.env` File

Create a `.env` file in the project root (this file is gitignored):

```bash
# DagsHub Configuration
DAGSHUB_USERNAME=your_dagshub_username
DAGSHUB_TOKEN=your_dagshub_token

# MLflow Configuration
MLFLOW_TRACKING_URI=https://dagshub.com/your_username/DeepGuard-MLOps-Pipeline.mlflow
MLFLOW_TRACKING_USERNAME=your_dagshub_username
MLFLOW_TRACKING_PASSWORD=your_dagshub_token

# Kaggle Configuration (for dataset download)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

### 2.2 Update params.yaml

Ensure your `params.yaml` has the correct MLflow configuration:

```yaml
mlflow:
  # Your DagsHub username
  dagshub_username: "your_username"
  
  # Repository name on DagsHub
  dagshub_repo: "DeepGuard-MLOps-Pipeline"
  
  # MLflow experiment name
  experiment_name: "DeepGuard-Model-Training"
  
  # Registered model name in MLflow
  registered_model_name: "DeepGuard-Classifier"
```

---

## 🔗 Step 3: Connect Git Remote

### 3.1 Add DagsHub as Remote

```powershell
# Add DagsHub remote
git remote add dagshub https://dagshub.com/your_username/DeepGuard-MLOps-Pipeline.git

# Verify remotes
git remote -v
```

### 3.2 Push to DagsHub

```powershell
# Push main branch
git push dagshub main

# Push DVC tracked data (if using DagsHub storage)
dvc remote add dagshub https://dagshub.com/your_username/DeepGuard-MLOps-Pipeline.dvc
dvc push -r dagshub
```

---

## ⚙️ Step 4: Configure DVC Remote (Optional)

If you want to use DagsHub for DVC storage:

### 4.1 Add DVC Remote

```powershell
# Add DagsHub as DVC remote
dvc remote add -d dagshub https://dagshub.com/your_username/DeepGuard-MLOps-Pipeline.dvc

# Set credentials
dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user your_dagshub_username
dvc remote modify dagshub --local password your_dagshub_token
```

### 4.2 Push Data to DagsHub

```powershell
dvc push
```

---

## 🧪 Step 5: Verify MLflow Connection

### 5.1 Test Connection Script

Create a test script or run in Python:

```python
import os
import mlflow
import dagshub

# Initialize DagsHub
dagshub.init(
    repo_owner="your_username",
    repo_name="DeepGuard-MLOps-Pipeline",
    mlflow=True
)

# Test logging
with mlflow.start_run(run_name="test-connection"):
    mlflow.log_param("test_param", "hello")
    mlflow.log_metric("test_metric", 1.0)
    print("✅ MLflow connection successful!")
```

### 5.2 View in DagsHub

1. Go to your DagsHub repository
2. Click on **"Experiments"** tab
3. You should see your test run

---

## 📊 Step 6: Using MLflow Tracking

### Logging Parameters

```python
import mlflow

mlflow.log_param("learning_rate", 0.0001)
mlflow.log_param("batch_size", 32)
mlflow.log_param("architecture", "XceptionTransfer")
```

### Logging Metrics

```python
mlflow.log_metric("accuracy", 0.95)
mlflow.log_metric("loss", 0.05)
mlflow.log_metric("val_accuracy", 0.93)
```

### Logging Artifacts

```python
# Log model
mlflow.keras.log_model(model, "model")

# Log figures
mlflow.log_artifact("reports/figures/confusion_matrix.png")

# Log entire directory
mlflow.log_artifacts("reports/figures", "figures")
```

---

## 📦 Step 7: Model Registry

### Register a Model

```python
# During training
mlflow.keras.log_model(
    model,
    "model",
    registered_model_name="DeepGuard-Classifier"
)
```

### Transition Model Stages

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition to staging
client.transition_model_version_stage(
    name="DeepGuard-Classifier",
    version=1,
    stage="Staging"
)

# Transition to production
client.transition_model_version_stage(
    name="DeepGuard-Classifier",
    version=1,
    stage="Production"
)
```

### Load Registered Model

```python
import mlflow.keras

# Load by version
model = mlflow.keras.load_model("models:/DeepGuard-Classifier/1")

# Load by stage
model = mlflow.keras.load_model("models:/DeepGuard-Classifier/Production")
```

---

## 🔍 Step 8: DagsHub Dashboard Features

### Experiments View

- Compare runs side-by-side
- Filter by parameters or metrics
- Download artifacts

### Data Tab

- View DVC tracked files
- Browse data versions
- See file changes between commits

### Repository View

- Code with syntax highlighting
- Commit history
- Branch management

---

## ❗ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Check DAGSHUB_TOKEN is valid |
| `Cannot connect to MLflow` | Verify MLFLOW_TRACKING_URI format |
| `DVC push fails` | Ensure DVC remote credentials are set |
| `Experiment not found` | Run `dagshub.init()` before logging |

### Reset MLflow Credentials

```powershell
# Clear cached credentials
$env:MLFLOW_TRACKING_USERNAME = "your_username"
$env:MLFLOW_TRACKING_PASSWORD = "your_token"
```

### Verify Environment Variables

```powershell
# Check if variables are set
echo $env:DAGSHUB_USERNAME
echo $env:MLFLOW_TRACKING_URI
```

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| DagsHub Docs | [docs.dagshub.com](https://docs.dagshub.com) |
| MLflow Docs | [mlflow.org/docs](https://mlflow.org/docs/latest/index.html) |
| DVC Docs | [dvc.org/doc](https://dvc.org/doc) |
| Kaggle API | [github.com/Kaggle/kaggle-api](https://github.com/Kaggle/kaggle-api) |

---

## 📚 Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System design overview
- [Quickstart](QUICKSTART.md) - Running the pipeline from scratch
