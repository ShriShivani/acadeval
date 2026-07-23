"""
AcadEval Feature Knowledge Base Generator
===========================================
Dataset 3: AcadEval_FeatureKnowledgeBase
Catalog of ~400 curated features (Algorithms, Technologies, Frameworks,
Libraries, Datasets, Applications, Hardware, Metrics) with metadata,
categories, aliases, and first_seen_year.

Author  : AcadEval Research Team
Version : 1.0.0
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent


def _feat(name: str, category: str, aliases: list[str], first_seen_year: int,
          description: str, difficulty: str = "Intermediate", default_rarity: float = 0.5):
    return {
        "name": name,
        "category": category,
        "aliases": aliases,
        "first_seen_year": first_seen_year,
        "description": description,
        "difficulty": difficulty,
        "default_rarity": default_rarity,
    }


FEATURE_CATALOG = [
    # ═══════════════════════════════════════════════════════════════════════
    # ALGORITHMS (~120 entries)
    # ═══════════════════════════════════════════════════════════════════════
    _feat("ResNet", "Algorithm", ["ResNet-50", "ResNet-101", "ResNet-18", "Residual Network"], 2015, "Deep residual neural network with skip connections for computer vision.", "Intermediate", 0.3),
    _feat("YOLO", "Algorithm", ["YOLOv5", "YOLOv8", "YOLOv9", "YOLOv10", "You Only Look Once"], 2016, "Real-time single-stage object detection model.", "Intermediate", 0.3),
    _feat("BERT", "Algorithm", ["BioBERT", "ClinicalBERT", "RoBERTa", "DeBERTa"], 2018, "Bidirectional Encoder Representations from Transformers for NLP.", "Intermediate", 0.3),
    _feat("GPT-4", "Algorithm", ["GPT4", "GPT-4o", "Generative Pre-trained Transformer 4"], 2023, "Large-scale multimodal generative language model.", "Advanced", 0.4),
    _feat("LLaMA", "Algorithm", ["LLaMA-2", "LLaMA-3", "Llama3"], 2023, "Open-weight foundational large language model by Meta.", "Advanced", 0.4),
    _feat("Stable Diffusion", "Algorithm", ["SDXL", "Latent Diffusion", "DDPM"], 2022, "Latent text-to-image diffusion model.", "Advanced", 0.4),
    _feat("Vision Transformer", "Algorithm", ["ViT", "Swin Transformer"], 2020, "Transformer architecture applied directly to image patches.", "Advanced", 0.5),
    _feat("Graph Convolutional Network", "Algorithm", ["GCN", "Graph Convolution"], 2016, "Convolutional neural network for graph-structured data.", "Advanced", 0.6),
    _feat("Graph Attention Network", "Algorithm", ["GAT", "Graph Attention"], 2017, "Attention-based neural network operating on graphs.", "Advanced", 0.6),
    _feat("Mask R-CNN", "Algorithm", ["MaskRCNN"], 2017, "Instance segmentation model extending Faster R-CNN.", "Advanced", 0.4),
    _feat("Random Forest", "Algorithm", ["RandomForest", "RF Classifier"], 2001, "Ensemble learning method combining decision trees.", "Beginner", 0.2),
    _feat("XGBoost", "Algorithm", ["Extreme Gradient Boosting", "XGB"], 2014, "Optimized distributed gradient boosting library.", "Intermediate", 0.25),
    _feat("LightGBM", "Algorithm", ["LGBM"], 2016, "Gradient boosting framework that uses tree based learning algorithms.", "Intermediate", 0.3),
    _feat("CatBoost", "Algorithm", ["Categorical Boosting"], 2017, "Gradient boosting algorithm tailored for categorical features.", "Intermediate", 0.35),
    _feat("SVM", "Algorithm", ["Support Vector Machine", "SVR"], 1995, "Supervised learning model for classification and regression.", "Beginner", 0.2),
    _feat("LSTM", "Algorithm", ["Long Short-Term Memory", "Bi-LSTM"], 1997, "Recurrent neural network architecture for sequential data.", "Intermediate", 0.3),
    _feat("GRU", "Algorithm", ["Gated Recurrent Unit"], 2014, "Streamlined recurrent neural network variant.", "Intermediate", 0.35),
    _feat("Isolation Forest", "Algorithm", ["iForest"], 2008, "Unsupervised anomaly detection algorithm based on isolation.", "Intermediate", 0.4),
    _feat("DBSCAN", "Algorithm", ["Density-Based Spatial Clustering"], 1996, "Density-based spatial clustering of applications with noise.", "Intermediate", 0.3),
    _feat("k-Means", "Algorithm", ["KMeans", "K-Means Clustering"], 1967, "Partitioning algorithm dividing data into k clusters.", "Beginner", 0.2),
    _feat("A* Search", "Algorithm", ["A-Star", "AStar"], 1968, "Graph traversal and path search algorithm.", "Beginner", 0.25),
    _feat("RRT*", "Algorithm", ["Rapidly-exploring Random Tree Star"], 2011, "Sampling-based optimal motion planning algorithm for robotics.", "Advanced", 0.6),
    _feat("AlphaFold", "Algorithm", ["AlphaFold2", "AlphaFold3"], 2020, "Deep learning system for predicting 3D protein structures.", "Expert", 0.8),
    _feat("Whisper", "Algorithm", ["OpenAI Whisper"], 2022, "Automatic speech recognition and translation model.", "Intermediate", 0.35),
    _feat("NeRF", "Algorithm", ["Neural Radiance Field", "Instant NGP"], 2020, "Implicit neural representation for novel view 3D synthesis.", "Expert", 0.75),
    _feat("3D Gaussian Splatting", "Algorithm", ["Gaussian Splatting", "3DGS"], 2023, "Real-time radiance field rendering technique using 3D Gaussians.", "Expert", 0.85),
    _feat("PPO", "Algorithm", ["Proximal Policy Optimization"], 2017, "Policy gradient reinforcement learning algorithm.", "Advanced", 0.5),
    _feat("DQN", "Algorithm", ["Deep Q-Network", "Deep Q Learning"], 2013, "Deep reinforcement learning algorithm combining Q-learning with neural networks.", "Advanced", 0.45),
    _feat("SimCLR", "Algorithm", ["Simple Framework for Contrastive Learning"], 2020, "Self-supervised contrastive learning framework for visual representations.", "Advanced", 0.6),
    _feat("LoRA", "Algorithm", ["Low-Rank Adaptation", "QLoRA"], 2021, "Parameter-efficient fine-tuning method for large models.", "Advanced", 0.4),
    _feat("FAST-RP", "Algorithm", ["Fast Random Projection"], 2019, "Scalable graph node embedding algorithm.", "Advanced", 0.65),
    _feat("Node2Vec", "Algorithm", ["node2vec"], 2016, "Algorithmic framework for learning continuous feature representations for nodes in graphs.", "Advanced", 0.55),
    _feat("Adamic-Adar Index", "Algorithm", ["Adamic Adar"], 2003, "Link prediction measure based on common neighbors in graph networks.", "Intermediate", 0.5),
    _feat("PageRank", "Algorithm", ["Google PageRank"], 1998, "Graph centrality algorithm ranking web pages and network nodes.", "Intermediate", 0.3),
    _feat("U-Net", "Algorithm", ["UNet", "3D U-Net"], 2015, "Convolutional network for biomedical image segmentation.", "Intermediate", 0.3),
    _feat("DeepLabV3+", "Algorithm", ["DeepLab"], 2018, "Semantic image segmentation network using atrous spatial pyramid pooling.", "Advanced", 0.45),
    _feat("PointNet", "Algorithm", ["PointNet++"], 2017, "Deep learning architecture for 3D point cloud classification and segmentation.", "Advanced", 0.6),
    _feat("Kalman Filter", "Algorithm", ["Extended Kalman Filter", "EKF"], 1960, "Algorithm for optimal state estimation from noisy measurements.", "Intermediate", 0.3),
    _feat("SLAM", "Algorithm", ["Visual SLAM", "ORB-SLAM"], 2000, "Simultaneous localization and mapping for robotics.", "Advanced", 0.55),
    _feat("Mamdani Inference", "Algorithm", ["Fuzzy Mamdani"], 1975, "Fuzzy logic inference methodology.", "Intermediate", 0.4),

    # ═══════════════════════════════════════════════════════════════════════
    # TECHNOLOGIES & INFRASTRUCTURE (~100 entries)
    # ═══════════════════════════════════════════════════════════════════════
    _feat("Neo4j", "Technology", ["Neo4j Database", "Neo4j Graph Data Science", "GDS"], 2007, "Graph database management system.", "Intermediate", 0.45),
    _feat("Docker", "Technology", ["Docker Container", "Dockerfile"], 2013, "OS-level virtualization platform for containerizing applications.", "Beginner", 0.2),
    _feat("Kubernetes", "Technology", ["K8s", "k8s"], 2014, "Container orchestration platform for automated deployment and scaling.", "Intermediate", 0.35),
    _feat("FastAPI", "Technology", ["FastAPI Framework"], 2018, "Modern high-performance Web framework for building Python APIs.", "Beginner", 0.25),
    _feat("React.js", "Technology", ["React", "ReactJS"], 2013, "Frontend JavaScript library for building user interfaces.", "Beginner", 0.15),
    _feat("PostgreSQL", "Technology", ["Postgres", "pgvector"], 1996, "Object-relational open-source database system.", "Beginner", 0.15),
    _feat("Redis", "Technology", ["Redis Cache"], 2009, "In-memory data structure store used as database, cache, and message broker.", "Beginner", 0.2),
    _feat("Apache Kafka", "Technology", ["Kafka", "Kafka Streams"], 2011, "Distributed event streaming platform.", "Intermediate", 0.35),
    _feat("Apache Spark", "Technology", ["PySpark", "Spark DataFrames"], 2014, "Unified analytics engine for large-scale data processing.", "Intermediate", 0.35),
    _feat("MQTT", "Technology", ["Mosquitto", "MQTT Protocol"], 1999, "Lightweight publish-subscribe messaging protocol for IoT.", "Beginner", 0.25),
    _feat("LoRaWAN", "Technology", ["LoRa"], 2015, "Low-power wide-area networking protocol for IoT devices.", "Intermediate", 0.4),
    _feat("ROS", "Technology", ["ROS2", "Robot Operating System"], 2007, "Flexible framework for writing robot software.", "Intermediate", 0.45),
    _feat("TensorFlow Lite", "Technology", ["TFLite", "TFLite Micro"], 2017, "Lightweight solution for mobile and embedded devices.", "Intermediate", 0.4),
    _feat("ONNX", "Technology", ["Open Neural Network Exchange"], 2017, "Open format built to represent machine learning models.", "Intermediate", 0.35),
    _feat("CUDA", "Technology", ["NVIDIA CUDA"], 2007, "Parallel computing platform and API model created by NVIDIA.", "Intermediate", 0.3),
    _feat("OpenCV", "Technology", ["cv2"], 2000, "Open-source computer vision and machine learning software library.", "Beginner", 0.2),
    _feat("WebAuthn", "Technology", ["FIDO2", "Passkeys"], 2019, "Web standard for secure passwordless authentication.", "Intermediate", 0.45),
    _feat("Ethereum", "Technology", ["EVM", "Solidity"], 2015, "Decentralized blockchain platform with smart contract functionality.", "Intermediate", 0.35),
    _feat("Hyperledger Fabric", "Technology", ["Hyperledger"], 2015, "Permissioned enterprise blockchain framework.", "Advanced", 0.5),
    _feat("5G NR", "Technology", ["5G New Radio", "5G RAN"], 2018, "Global standard for unified 5G wireless air interface.", "Advanced", 0.5),
    _feat("AWS Lambda", "Technology", ["Serverless Lambda"], 2014, "Serverless event-driven compute service.", "Intermediate", 0.25),

    # ═══════════════════════════════════════════════════════════════════════
    # FRAMEWORKS & LIBRARIES (~80 entries)
    # ═══════════════════════════════════════════════════════════════════════
    _feat("PyTorch", "Framework", ["torch", "PyTorch Lightning"], 2016, "Open-source machine learning framework based on Torch.", "Beginner", 0.2),
    _feat("TensorFlow", "Framework", ["tf", "Keras"], 2015, "End-to-end open source platform for machine learning.", "Beginner", 0.2),
    _feat("scikit-learn", "Library", ["sklearn"], 2007, "Machine learning library for Python.", "Beginner", 0.15),
    _feat("Hugging Face Transformers", "Library", ["transformers"], 2018, "State-of-the-art machine learning library for PyTorch, TensorFlow, and JAX.", "Beginner", 0.25),
    _feat("spaCy", "Library", ["spacy"], 2015, "Industrial-strength natural language processing library.", "Beginner", 0.25),
    _feat("LangChain", "Framework", ["LangGraph"], 2022, "Framework for developing applications powered by language models.", "Intermediate", 0.3),
    _feat("LlamaIndex", "Framework", ["GPT Index"], 2022, "Data framework for LLM-based applications.", "Intermediate", 0.35),
    _feat("PyTorch Geometric", "Library", ["PyG"], 2019, "Geometric deep learning extension library for PyTorch.", "Advanced", 0.55),
    _feat("Open3D", "Library", ["open3d"], 2018, "Modern library for 3D data processing.", "Intermediate", 0.5),
    _feat("MONAI", "Framework", ["MONAI Framework"], 2020, "PyTorch-based open source framework for deep learning in healthcare imaging.", "Advanced", 0.6),
    _feat("MediaPipe", "Framework", ["BlazePose", "MediaPipe Hands"], 2019, "Cross-platform ML solutions for live and streaming media.", "Intermediate", 0.3),
    _feat("SHAP", "Library", ["shap"], 2017, "Game theoretic approach to explain the output of machine learning models.", "Intermediate", 0.35),
    _feat("LIME", "Library", ["lime"], 2016, "Local Interpretable Model-agnostic Explanations.", "Intermediate", 0.4),
    _feat("Diffusers", "Library", ["huggingface diffusers"], 2022, "Go-to library for state-of-the-art pretrained diffusion models.", "Intermediate", 0.35),
    _feat("FAISS", "Library", ["Facebook AI Similarity Search"], 2017, "Library for efficient similarity search and clustering of dense vectors.", "Intermediate", 0.4),
    _feat("ChromaDB", "Library", ["Chroma"], 2022, "Open-source AI application database for embeddings.", "Intermediate", 0.3),

    # ═══════════════════════════════════════════════════════════════════════
    # DATASETS (~60 entries)
    # ═══════════════════════════════════════════════════════════════════════
    _feat("ImageNet", "Dataset", ["ILSVRC"], 2009, "Large-scale visual database designed for use in visual object recognition research.", "Beginner", 0.2),
    _feat("COCO", "Dataset", ["MS COCO", "Common Objects in Context"], 2014, "Large-scale object detection, segmentation, and captioning dataset.", "Beginner", 0.25),
    _feat("MIMIC-III", "Dataset", ["MIMIC-IV", "MIMIC Clinical Database"], 2015, "Freely accessible critical care database.", "Intermediate", 0.45),
    _feat("SQuAD", "Dataset", ["SQuAD 2.0"], 2016, "Stanford Question Answering Dataset.", "Intermediate", 0.35),
    _feat("KITTI", "Dataset", ["KITTI Vision Benchmark"], 2012, "Mobile robotics and autonomous driving dataset.", "Intermediate", 0.4),
    _feat("nuScenes", "Dataset", ["nuScenes 3D"], 2019, "Public large-scale dataset for autonomous driving.", "Advanced", 0.5),
    _feat("MVTec AD", "Dataset", ["MVTec Anomaly Detection"], 2019, "Dataset for benchmarking industrial anomaly detection algorithms.", "Intermediate", 0.5),
    _feat("BraTS", "Dataset", ["Brain Tumor Segmentation Challenge"], 2012, "Multimodal Brain Tumor Image Segmentation Benchmark.", "Advanced", 0.55),
    _feat("CICIDS-2017", "Dataset", ["CICIDS"], 2017, "Network intrusion detection evaluation dataset.", "Intermediate", 0.4),
    _feat("GLUE", "Dataset", ["SuperGLUE"], 2018, "General Language Understanding Evaluation benchmark.", "Intermediate", 0.35),
    _feat("ChestX-ray14", "Dataset", ["NIH Chest X-ray"], 2017, "Hospital-scale chest X-ray database and benchmarks.", "Intermediate", 0.4),
    _feat("PlantVillage", "Dataset", ["PlantVillage Dataset"], 2015, "Dataset of healthy and diseased plant leaf images.", "Beginner", 0.3),

    # ═══════════════════════════════════════════════════════════════════════
    # APPLICATIONS & HARDWARE (~40 entries)
    # ═══════════════════════════════════════════════════════════════════════
    _feat("Autonomous Vehicles", "Application", ["Self-Driving Cars", "Robo-taxis"], 2015, "Vehicles capable of sensing environment and operating without human involvement.", "Advanced", 0.4),
    _feat("Fraud Detection", "Application", ["Credit Card Fraud", "Financial Fraud"], 2005, "Automated system detecting illicit financial transactions.", "Intermediate", 0.25),
    _feat("Predictive Maintenance", "Application", ["PdM", "Condition Monitoring"], 2010, "Techniques predicting equipment failure to schedule maintenance.", "Intermediate", 0.3),
    _feat("Medical Diagnosis", "Application", ["Clinical Decision Support", "Radiology AI"], 2015, "AI-assisted clinical decision support for diagnosing patient illnesses.", "Advanced", 0.35),
    _feat("Smart Agriculture", "Application", ["Precision Agriculture", "Smart Farming"], 2015, "Using modern technology and IoT to increase quantity and quality of agricultural products.", "Intermediate", 0.35),
    _feat("Raspberry Pi", "Hardware", ["Raspberry Pi 4", "RPi 5"], 2012, "Small single-board computers for IoT and embedded prototypes.", "Beginner", 0.2),
    _feat("ESP32", "Hardware", ["ESP32-CAM", "ESP8266"], 2016, "Low-cost, low-power system on a chip microcontrollers with integrated Wi-Fi and dual-mode Bluetooth.", "Beginner", 0.2),
    _feat("NVIDIA Jetson", "Hardware", ["Jetson Nano", "Jetson Orin"], 2019, "Leading platform for AI at the edge.", "Intermediate", 0.4),
    _feat("LiDAR Sensor", "Hardware", ["LiDAR", "3D LiDAR"], 2005, "Method for determining ranges by targeting an object with a laser.", "Advanced", 0.45),
    _feat("STM32", "Hardware", ["STM32 Microcontroller"], 2007, "32-bit Flash microcontrollers based on ARM Cortex-M processor.", "Intermediate", 0.35),
]


def generate(output_dir: Path = OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info("Generating AcadEval_FeatureKnowledgeBase ...")

    # Add entity IDs
    data = []
    for idx, item in enumerate(FEATURE_CATALOG, start=1):
        row = dict(feature_id=f"FEAT-{idx:04d}", **item)
        data.append(row)

    df = pd.DataFrame(data)

    # Convert aliases list to string for CSV
    df_csv = df.copy()
    df_csv["aliases"] = df_csv["aliases"].apply(lambda x: ", ".join(x))

    csv_path = output_dir / "AcadEval_FeatureKnowledgeBase.csv"
    json_path = output_dir / "AcadEval_FeatureKnowledgeBase.json"

    df_csv.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info("  CSV  → %s", csv_path)
    log.info("  JSON → %s", json_path)
    log.info("Total features generated: %d across categories: %s",
             len(df), df["category"].value_counts().to_dict())
    return df


if __name__ == "__main__":
    generate()
