# DeepGuard MLOps Pipeline Documentation

Welcome to the DeepGuard documentation! This guide will help you understand, set up, and run the AI-generated image detection pipeline.

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [**QUICKSTART.md**](QUICKSTART.md) | Get running in 30 minutes |
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | System design & project structure |
| [**SETUP.md**](SETUP.md) | DagsHub & MLflow configuration |

---

## 🚀 Quick Links

### First Time Setup
```powershell
git clone https://github.com/YOUR_USERNAME/DeepGuard-MLOps-Pipeline.git
cd DeepGuard-MLOps-Pipeline
pip install -r requirements.txt
dvc repro
```

### Run Web App
```powershell
python flask_app/app.py
# Open http://localhost:5000
```

### View Pipeline
```powershell
dvc dag
```

---

## 🏗️ Project Overview

**DeepGuard** is a production-grade MLOps pipeline for detecting AI-generated images. It demonstrates:

- ✅ **Data Versioning** with DVC
- ✅ **Experiment Tracking** with MLflow/DagsHub
- ✅ **Reproducible Pipelines** with DVC stages
- ✅ **Model Registry** for version control
- ✅ **Web Application** for real-time inference

---

## 📊 Pipeline Stages

```
Data Ingestion → Preprocessing → Feature Engineering → Model Building → Evaluation → Registration
```

---

## 🔧 Configuration

All parameters are centralized in `params.yaml`:
- Model architecture selection
- Training hyperparameters
- Data processing settings
- MLflow configuration

---

## 📈 Model Performance

Current model (XceptionTransfer) achieves:
- **Accuracy**: ~95%
- **F1-Score**: ~0.95
- **ROC-AUC**: ~0.98

*Note: Performance may vary based on dataset and training parameters.*

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- Create an issue on GitHub
- Check the troubleshooting sections in each doc
- Review DagsHub experiment logs
