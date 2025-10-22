# IT_Thesis_Group-8

Project Overview
This repository contains the complete analysis workflow developed for the phylogeographic mapping of the Pink Cockatoo across Northern Australia. The study integrates ecoacoustics, spatial ecology, and machine learning to analyze regional vocal patterns using spectrogram-based deep learning (CNN/CRNN) and dimensionality reduction (PCA/UMAP).
 
Environment Setup
Python Environment
Python ≥ 3.10
TensorFlow ≥ 2.11
Works on Windows 

Model Architecture
Lightweight CNN
Spectrograms are used as input to a compact CNN built in TensorFlow/Keras.
Architecture summary:
Input: 128×128×3 spectrogram images
Three Conv2D blocks: (Conv → ReLU → MaxPooling)
Flatten layer
Dense layer: 128 neurons, ReLU
Dropout: 0.5
Output layer: Softmax (number of IBRA classes)
Training setup:
Optimizer: Adam
Loss: Categorical Cross-Entropy
Early stopping: on validation loss
Parameters: ~200K
Dataset: 698 spectrograms

├── README.md
├── requirements.txt
├── config.yml
├── data/
│   ├── pink_cockatoo_dataset.csv
│   └── spectrograms/
├── notebooks/
│   ├── 01_eda_features.ipynb
│   ├── 02_train_cnn.ipynb
│   ├── 03_train_crnn.ipynb
│   ├── 04_dimensionality_reduction.ipynb
│   └── 05_visualization_and_mapping.ipynb
├── src/
│   ├── data_loader.py
│   ├── feature_extraction.py
│   ├── models.py
│   ├── train.py
│   ├── evaluate.py
│   └── visualizations.py
└── results/
    ├── figures/
    ├── metrics/
    ├── confusion_matrix.png
    └── umap_clusters.png

Execution Steps
Step 1: Data Loading & Preprocessing
Loads CSV and spectrograms
Handles missing values and validates coordinates

Step 2: Feature Extraction

Computes spectrogram features

Extracts acoustic metrics (e.g., bandwidth, peak frequency)



 
Step 3: Model Training
Trains lightweight CNN
Saves best checkpoint as model_cnn.h5
Step 4: Evaluation & Metrics
python src/evaluate.py --config config.yml

 Generates accuracy, F1-score, and confusion matrix
 
Step 5: Dimensionality Reduction
python src/visualizations.py --task umap

       .Performs PCA and UMAP
        Saves 2D embeddings for bioregional clustering
 
Step 6: Temporal & Spatial Mapping
Produces diel heatmaps, seasonal plots, and NT region maps
Exports final results to result/thesis_outputs.xlsx

Outputs
Model: model_cnn.h5
Metrics: cnn_classification_report.txt
Visuals:
pca_plot.png, umap_clusters.png
temporal_calls_by_region.png
diel_heatmap_cnn.png
spatial_nt_map.png
  
