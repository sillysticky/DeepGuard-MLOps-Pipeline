# DeepGuard Pipeline Quickstart Guide

This guide provides step-by-step instructions to get the DeepGuard MLOps pipeline running from scratch in under 30 minutes.

---

## Quick Setup (5 minutes)

### 1. Clone Repository

```powershell
git clone https://github.com/HarshTomar1234/DeepGuard-MLOps-Pipeline.git
cd DeepGuard-MLOps-Pipeline
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv atlas

# Activate (Windows)
.\atlas\Scripts\Activate

# Activate (Linux/Mac)
source atlas/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Credentials

Create a `.env` file in the project root:

```bash
DAGSHUB_USERNAME=your_dagshub_username
DAGSHUB_TOKEN=your_dagshub_token
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

---

## Run Full Pipeline (20 minutes)

### Option A: Run All Stages at Once

```powershell
dvc repro
```

This executes all 6 stages automatically. DVC tracks dependencies and only re-runs stages when inputs change.

### Option B: Run Stages Individually

```powershell
# Stage 1: Download dataset from Kaggle
dvc repro data_ingestion

# Stage 2: Preprocess images (resize, normalize, split)
dvc repro data_preprocessing

# Stage 3: Apply data augmentation
dvc repro feature_engineering

# Stage 4: Train CNN model
dvc repro model_building

# Stage 5: Evaluate and generate metrics
dvc repro model_evaluation

# Stage 6: Register model to MLflow
dvc repro model_registration
```

---

## View Pipeline DAG

```powershell
dvc dag
```

Expected output:
```
+----------------+
| data_ingestion |
+----------------+
        *
        *
        *
+-------------------+
| data_preprocessing |
+-------------------+
        *
        *
        *
+---------------------+
| feature_engineering |
+---------------------+
        *
        *
        *
+----------------+
| model_building |
+----------------+
        *
        *
        *
+------------------+
| model_evaluation |
+------------------+
        *
        *
        *
+--------------------+
| model_registration |
+--------------------+
```

---

## Run Flask Web Application

After training, launch the web app:

```powershell
python flask_app/app.py
```

Open browser at: http://localhost:5000

### Test the App

1. Upload an image (JPEG, PNG)
2. Click "Analyze Image"
3. View prediction: Real or AI-Generated

---

## Run with Docker

```powershell
# Build the image
docker build -t deepguard-app:latest .

# Run the container
docker run -p 8888:5000 deepguard-app:latest
```

Open browser at: http://localhost:8888

---

## View Results

### Check Metrics

```powershell
type reports\metrics.json
```

Example output:
```json
{
  "accuracy": 0.95,
  "precision": 0.94,
  "recall": 0.96,
  "f1_score": 0.95,
  "roc_auc": 0.98
}
```

### View Experiment on DagsHub

1. Go to your DagsHub repository
2. Click "Experiments" tab
3. Compare runs and view artifacts

### View Generated Figures

Check `reports/figures/` for:
- confusion_matrix.png - Model predictions vs actual
- roc_curve.png - ROC curve with AUC score
- training_history.png - Loss and accuracy over epochs

---

## Configuration

### Modify Hyperparameters

Edit `params.yaml` to change:

```yaml
# Model architecture
model:
  architecture: "XceptionTransfer"  # Options: SimpleCNN, DeeperCNN, XceptionTransfer
  input_shape: [128, 128, 3]

# Training settings
training:
  epochs: 30
  batch_size: 32
  learning_rate: 0.0001
  early_stopping_patience: 7

# Data settings
preprocessing:
  image_size: 128
  sample_size: 10000    # null = use all data
  validation_split: 0.2
```

After changing params, run:
```powershell
dvc repro
```

DVC automatically detects parameter changes and re-runs affected stages.

---

## Run Individual Modules

### Test Data Ingestion

```powershell
python -m src.data.data_ingestion
```

### Test Preprocessing

```powershell
python -m src.data.data_preprocessing
```

### Test Model Building

```powershell
python -m src.model.model_building
```

### Test Evaluation

```powershell
python -m src.model.model_evaluation
```

---

## Compare Experiments

### List All Experiments

```python
import mlflow

experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"{exp.name}: {exp.experiment_id}")
```

### Compare Runs

```python
runs = mlflow.search_runs(experiment_names=["DeepGuard-Model-Training"])
print(runs[["run_id", "metrics.accuracy", "params.architecture"]])
```

---

## Update Data and Retrain

### Pull Latest Data

```powershell
dvc pull
```

### Force Re-run a Stage

```powershell
dvc repro -f model_building
```

### Reproduce Entire Pipeline

```powershell
dvc repro -f
```

---

## Export Model for Deployment

### Save Model Locally

```powershell
# Model is saved at models/best_model.keras
copy models\best_model.keras deployment\
```

### Load Model for Inference

```python
from tensorflow.keras.models import load_model

model = load_model("models/best_model.keras")
```

### Load from MLflow Registry

```python
import mlflow.keras

model = mlflow.keras.load_model("models:/DeepGuard-Classifier/Production")
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| kagglehub error | Check KAGGLE_USERNAME and KAGGLE_KEY in `.env` |
| OOM during training | Reduce batch_size or sample_size in params.yaml |
| MLflow connection failed | Verify DagsHub credentials and tracking URI |
| dvc repro does nothing | Parameters/dependencies unchanged; use `dvc repro -f` |
| ModuleNotFoundError | Run `pip install -e .` to install local package |

---

## Next Steps

1. Explore Notebooks: Check `notebooks/` for detailed analysis
2. Customize Architecture: Add new models in `src/model/model_building.py`
3. Deploy to Cloud: Use the Docker image with AWS EKS or similar
4. Set Up CI/CD: GitHub Actions workflow included in `.github/workflows/`

---

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System design overview
- [Setup Guide](SETUP.md) - DagsHub/MLflow configuration
