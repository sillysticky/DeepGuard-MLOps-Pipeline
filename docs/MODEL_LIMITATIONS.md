# DeepGuard Model Limitations Analysis

## Summary

The DeepGuard model achieves **88.35% accuracy** on the test dataset from the "140k Real and Fake Faces" dataset, but has **significant limitations** when applied to real-world scenarios.

---

## Training Data Analysis

| Aspect | Details |
|--------|---------|
| **Dataset** | 140k Real and Fake Faces (Kaggle) |
| **Real Images** | 70,000 Flickr faces (FFHQ-style) |
| **Fake Images** | 70,000 StyleGAN-generated faces |
| **Image Size** | 256x256, resized to 128x128 for training |
| **Time Period** | GAN-era faces (~2019-2020) |

---

## Model Performance

### ✅ Works Well On:
- **StyleGAN/StyleGAN2 generated faces** - The exact type the model was trained on
- **GAN-based face generators** - Similar architecture to training data
- **Flickr-style real photos** - Similar to training distribution

### ❌ Fails On:
| Image Type | Prediction Result | Reason |
|------------|------------------|--------|
| **Stable Diffusion faces** | Predicts as REAL | Different artifact patterns |
| **Midjourney faces** | Predicts as REAL | Diffusion-based, not GAN-based |
| **DALL-E faces** | Predicts as REAL | Different generation technology |
| **Modern AI art** | Predicts as REAL | Out-of-distribution |

---

## Technical Explanation

### Why the Model Fails on Modern AI Images

1. **Training Distribution Mismatch**
   - Model learned to detect **GAN-specific artifacts** (checkerboard patterns, frequency domain anomalies)
   - Modern **diffusion models** (Stable Diffusion, Midjourney, DALL-E) produce completely different artifacts
   
2. **Out-of-Distribution (OOD) Problem**
   - When an image doesn't match what the model saw during training, it defaults to "REAL"
   - This is because the model outputs a confidence score, and unfamiliar images produce uncertain predictions

3. **Technology Evolution**
   - GANs (2018-2020): ProGAN, StyleGAN, StyleGAN2
   - Diffusion Models (2022+): DALL-E 2/3, Midjourney, Stable Diffusion
   - The model is essentially 3-4 years behind current AI technology

---

## Tested Examples

### User's Modern AI Images (Expected: FAKE)
| Image | Prediction | Confidence | Actual |
|-------|------------|------------|--------|
| uploaded_image_0 | REAL | 99.99% | FAKE ❌ |
| uploaded_image_1 | REAL | 99.99% | FAKE ❌ |

### Training Dataset Images (Expected: Correct)
| Image Source | Accuracy |
|--------------|----------|
| test/FAKE (StyleGAN) | ~88% ✅ |
| test/REAL (Flickr) | ~88% ✅ |

---

## Recommendations

### For Practical Deployment:

1. **Be Transparent**: Display disclaimer that model is trained on StyleGAN faces only
2. **Multi-Model Approach**: Combine with other detectors (frequency analysis, metadata check)
3. **Confidence Threshold**: Flag predictions with low confidence for manual review

### For Improved Detection:

1. **Retrain on Modern Data**: Use datasets with Stable Diffusion, Midjourney, DALL-E images
2. **Use Newer Models**: CLIP-based detectors, AI Image Detector by Hive, etc.
3. **Ensemble Methods**: Combine multiple detection approaches

---

## Conclusion

**The DeepGuard model is a valid proof-of-concept for MLOps pipelines**, demonstrating:
- DVC pipeline implementation
- MLflow experiment tracking
- Model registration and versioning
- Flask/Gradio deployment

However, for **production-level AI detection**, the model would need retraining on modern AI-generated images.
