"""
Module 3 FeatureKnowledgeBase Expansion Script
================================================
Adds ~200 new curated entries covering:
  - All 15 classmate project topics (algorithms, techniques, domains used)
  - Common undergraduate CS/AI project vocabulary
  - Deduplicates against existing entries (case-insensitive name + alias match)
Run from the repo root:
  python datasets/feature_kb/expand_kb.py
"""

import json
from pathlib import Path

KB_PATH = Path(__file__).parent / "AcadEval_FeatureKnowledgeBase.json"

# ---------------------------------------------------------------------------
# New entries  (name, category, aliases, first_seen_year, description)
# Category must be one of: Algorithm | Technology | Framework | Library
#                          Dataset | Application | Hardware | Metric
# ---------------------------------------------------------------------------
NEW_ENTRIES = [
    # ── Core ML algorithms missing from KB ──────────────────────────────────
    {
        "name": "Convolutional Neural Network",
        "category": "Algorithm",
        "aliases": ["CNN", "ConvNet", "Conv2D"],
        "first_seen_year": 1989,
        "description": "Deep neural network architecture using convolutional layers for spatial feature extraction.",
    },
    {
        "name": "Graph Neural Network",
        "category": "Algorithm",
        "aliases": ["GNN", "Graph Net"],
        "first_seen_year": 2009,
        "description": "Neural network that operates on graph-structured data via message passing.",
    },
    {
        "name": "Heterogeneous Graph Neural Network",
        "category": "Algorithm",
        "aliases": ["HetGNN", "HGNN", "Heterogeneous GNN"],
        "first_seen_year": 2019,
        "description": "GNN variant that handles graphs with multiple node/edge types.",
    },
    {
        "name": "Graph Transformer",
        "category": "Algorithm",
        "aliases": ["GT", "Graphormer"],
        "first_seen_year": 2020,
        "description": "Transformer architecture adapted for graph-structured inputs.",
    },
    {
        "name": "Transformer",
        "category": "Algorithm",
        "aliases": ["Attention Mechanism", "Multi-Head Attention", "Self-Attention"],
        "first_seen_year": 2017,
        "description": "Self-attention based sequence model (Vaswani et al., Attention Is All You Need).",
    },
    {
        "name": "Federated Learning",
        "category": "Algorithm",
        "aliases": ["FL", "Federated ML", "FedAvg", "FedProx"],
        "first_seen_year": 2016,
        "description": "Distributed ML training where data never leaves the client device.",
    },
    {
        "name": "Transfer Learning",
        "category": "Algorithm",
        "aliases": ["Fine-tuning", "Domain Adaptation", "Pre-trained Model"],
        "first_seen_year": 1993,
        "description": "Reusing a model trained on one task as a starting point for another.",
    },
    {
        "name": "Reinforcement Learning",
        "category": "Algorithm",
        "aliases": ["RL", "Deep RL", "Model-Free RL"],
        "first_seen_year": 1992,
        "description": "Learning by interaction with an environment to maximize cumulative reward.",
    },
    {
        "name": "Generative Adversarial Network",
        "category": "Algorithm",
        "aliases": ["GAN", "cGAN", "DCGAN", "StyleGAN", "CycleGAN"],
        "first_seen_year": 2014,
        "description": "Generator–discriminator framework for synthesizing realistic data.",
    },
    {
        "name": "Variational Autoencoder",
        "category": "Algorithm",
        "aliases": ["VAE", "VQ-VAE"],
        "first_seen_year": 2013,
        "description": "Generative latent variable model that learns a structured embedding space.",
    },
    {
        "name": "Anomaly Detection",
        "category": "Algorithm",
        "aliases": ["Outlier Detection", "Novelty Detection", "One-Class Classification"],
        "first_seen_year": 1980,
        "description": "Identifies data points significantly different from the expected distribution.",
    },
    {
        "name": "Logistic Regression",
        "category": "Algorithm",
        "aliases": ["LR", "Logit Regression"],
        "first_seen_year": 1958,
        "description": "Linear model for binary or multiclass classification using sigmoid output.",
    },
    {
        "name": "Decision Tree",
        "category": "Algorithm",
        "aliases": ["DT", "Classification Tree", "Regression Tree", "CART"],
        "first_seen_year": 1986,
        "description": "Hierarchical rule-based classifier splitting data on feature thresholds.",
    },
    {
        "name": "Naive Bayes",
        "category": "Algorithm",
        "aliases": ["NB", "Gaussian Naive Bayes", "Multinomial NB"],
        "first_seen_year": 1960,
        "description": "Probabilistic classifier based on Bayes theorem with feature independence assumption.",
    },
    {
        "name": "K-Nearest Neighbor",
        "category": "Algorithm",
        "aliases": ["KNN", "k-NN", "kNN"],
        "first_seen_year": 1967,
        "description": "Instance-based learning classifying by majority vote of k nearest neighbors.",
    },
    {
        "name": "Gradient Descent",
        "category": "Algorithm",
        "aliases": ["SGD", "Adam", "AdaGrad", "RMSProp", "AdamW"],
        "first_seen_year": 1847,
        "description": "Iterative optimization algorithm minimizing a loss function.",
    },
    {
        "name": "SMOTE",
        "category": "Algorithm",
        "aliases": ["Synthetic Minority Oversampling Technique", "ADASYN"],
        "first_seen_year": 2002,
        "description": "Oversampling technique to handle class imbalance via synthetic sample generation.",
    },
    {
        "name": "Neural Architecture Search",
        "category": "Algorithm",
        "aliases": ["NAS", "AutoML", "Efficient NAS", "DARTS"],
        "first_seen_year": 2016,
        "description": "Automated search for optimal neural network architectures.",
    },
    {
        "name": "EfficientNet",
        "category": "Algorithm",
        "aliases": ["EfficientNetV2", "EfficientDet"],
        "first_seen_year": 2019,
        "description": "Compound-scaled CNN family achieving high accuracy with fewer parameters.",
    },
    {
        "name": "MobileNet",
        "category": "Algorithm",
        "aliases": ["MobileNetV2", "MobileNetV3", "MobileViT"],
        "first_seen_year": 2017,
        "description": "Lightweight depthwise-separable CNN optimized for mobile/edge deployment.",
    },
    {
        "name": "FaceNet",
        "category": "Algorithm",
        "aliases": ["Face Embedding", "ArcFace", "CosFace"],
        "first_seen_year": 2015,
        "description": "Deep embedding model for face recognition using triplet loss.",
    },
    {
        "name": "DeepFace",
        "category": "Algorithm",
        "aliases": ["Face Verification", "InsightFace"],
        "first_seen_year": 2014,
        "description": "Deep learning based face identification system (Meta).",
    },
    {
        "name": "Named Entity Recognition",
        "category": "Algorithm",
        "aliases": ["NER", "Entity Extraction", "Information Extraction"],
        "first_seen_year": 1996,
        "description": "NLP task identifying named entities (persons, organizations, etc.) in text.",
    },
    {
        "name": "Text Classification",
        "category": "Algorithm",
        "aliases": ["Document Classification", "Sentiment Classification"],
        "first_seen_year": 1992,
        "description": "Categorizing text into predefined classes.",
    },
    {
        "name": "Object Detection",
        "category": "Algorithm",
        "aliases": ["Bounding Box Detection", "Faster R-CNN", "SSD"],
        "first_seen_year": 2001,
        "description": "Localizing and classifying multiple objects within an image.",
    },
    {
        "name": "Semantic Segmentation",
        "category": "Algorithm",
        "aliases": ["Pixel Classification", "Scene Parsing"],
        "first_seen_year": 2015,
        "description": "Assigning a class label to every pixel in an image.",
    },
    {
        "name": "Action Recognition",
        "category": "Algorithm",
        "aliases": ["Activity Recognition", "Gesture Recognition", "Video Classification"],
        "first_seen_year": 2001,
        "description": "Classifying human actions or activities from video sequences.",
    },
    {
        "name": "Pose Estimation",
        "category": "Algorithm",
        "aliases": ["Human Pose Estimation", "Skeleton Detection", "OpenPose", "HRNet"],
        "first_seen_year": 2014,
        "description": "Detecting and localizing body keypoints for human pose analysis.",
    },
    {
        "name": "Optical Flow",
        "category": "Algorithm",
        "aliases": ["Dense Optical Flow", "FlowNet", "RAFT"],
        "first_seen_year": 1981,
        "description": "Estimating per-pixel motion between consecutive video frames.",
    },
    {
        "name": "Causal Inference",
        "category": "Algorithm",
        "aliases": ["Causal AI", "Do-Calculus", "Structural Causal Model"],
        "first_seen_year": 2000,
        "description": "Reasoning about cause-effect relationships beyond correlation.",
    },
    {
        "name": "Counterfactual Explanation",
        "category": "Algorithm",
        "aliases": ["Counterfactual AI", "Contrastive Explanation", "DiCE"],
        "first_seen_year": 2017,
        "description": "Explaining model decisions by describing minimal input changes to flip the outcome.",
    },
    {
        "name": "Quantum Machine Learning",
        "category": "Algorithm",
        "aliases": ["QML", "Quantum Deep Learning", "Quantum Neural Network"],
        "first_seen_year": 2014,
        "description": "Applying quantum computing to accelerate or enhance ML algorithms.",
    },
    {
        "name": "Variational Quantum Circuit",
        "category": "Algorithm",
        "aliases": ["VQC", "Quantum Variational Eigensolver", "QAOA"],
        "first_seen_year": 2014,
        "description": "Parameterized quantum circuit trained with classical optimization.",
    },
    {
        "name": "Diffusion Model",
        "category": "Algorithm",
        "aliases": ["DDPM", "Score Matching", "DDIM"],
        "first_seen_year": 2020,
        "description": "Generative model that learns to reverse a noise-addition process.",
    },
    {
        "name": "Recurrent Neural Network",
        "category": "Algorithm",
        "aliases": ["RNN", "Sequence Model", "Encoder-Decoder"],
        "first_seen_year": 1986,
        "description": "Neural network with temporal feedback connections for sequential data.",
    },
    {
        "name": "Grad-CAM",
        "category": "Algorithm",
        "aliases": ["Gradient-weighted Class Activation Map", "GradCAM", "Grad-CAM++"],
        "first_seen_year": 2016,
        "description": "Visual explanation technique highlighting image regions driving CNN predictions.",
    },
    {
        "name": "Sentence-BERT",
        "category": "Algorithm",
        "aliases": ["SBERT", "Sentence Transformers", "all-MiniLM-L6-v2"],
        "first_seen_year": 2019,
        "description": "BERT variant producing semantically meaningful sentence embeddings.",
    },
    {
        "name": "Word2Vec",
        "category": "Algorithm",
        "aliases": ["Word Embeddings", "GloVe", "FastText"],
        "first_seen_year": 2013,
        "description": "Shallow neural network producing dense word vector representations.",
    },
    {
        "name": "Bayesian Optimization",
        "category": "Algorithm",
        "aliases": ["Hyperparameter Optimization", "Optuna", "Hyperopt"],
        "first_seen_year": 1998,
        "description": "Probabilistic black-box optimization for hyperparameter tuning.",
    },
    {
        "name": "Mean Shift",
        "category": "Algorithm",
        "aliases": ["Mean Shift Clustering", "Bandwidth Estimation"],
        "first_seen_year": 1995,
        "description": "Non-parametric clustering algorithm seeking density mode.",
    },

    # ── Application domains (what these projects ARE about) ──────────────────
    {
        "name": "Phishing Detection",
        "category": "Application",
        "aliases": ["Scam Website Detection", "Malicious URL Detection", "Blacklist-free Detection"],
        "first_seen_year": 2004,
        "description": "Classifying URLs or emails as phishing/legitimate using ML features.",
    },
    {
        "name": "Network Intrusion Detection",
        "category": "Application",
        "aliases": ["IDS", "NIDS", "Intrusion Prevention System", "IPS", "Intrusion Detection"],
        "first_seen_year": 1987,
        "description": "Monitoring network traffic to identify malicious activity.",
    },
    {
        "name": "Landslide Detection",
        "category": "Application",
        "aliases": ["Landslide Alert System", "Slope Stability Monitoring"],
        "first_seen_year": 2005,
        "description": "Using remote sensing and ML for landslide risk detection and early warning.",
    },
    {
        "name": "Emotion Recognition",
        "category": "Application",
        "aliases": ["Facial Emotion Recognition", "Affective Computing", "Sentiment Analysis"],
        "first_seen_year": 1997,
        "description": "Identifying human emotional states from facial, vocal, or physiological signals.",
    },
    {
        "name": "Chatbot",
        "category": "Application",
        "aliases": ["Conversational AI", "Dialogue System", "Virtual Assistant", "LLM Chatbot"],
        "first_seen_year": 1966,
        "description": "AI system engaging in human-like text or voice dialogue.",
    },
    {
        "name": "Herbal Traceability",
        "category": "Application",
        "aliases": ["Botanical Traceability", "Drug Authentication", "Supply Chain Traceability"],
        "first_seen_year": 2010,
        "description": "Blockchain-based tracking of herbal/pharmaceutical products from source to consumer.",
    },
    {
        "name": "Dysgraphia Detection",
        "category": "Application",
        "aliases": ["Handwriting Disorder Detection", "Learning Disability Detection", "Handwriting Analysis"],
        "first_seen_year": 2012,
        "description": "Automated identification of dysgraphia through handwriting pattern analysis.",
    },
    {
        "name": "Sports Analytics",
        "category": "Application",
        "aliases": ["Sports AI", "Game Analysis", "Player Tracking"],
        "first_seen_year": 2003,
        "description": "Using AI/ML to analyze athlete performance and game events.",
    },
    {
        "name": "Heart Attack Detection",
        "category": "Application",
        "aliases": ["Myocardial Infarction Detection", "Cardiac Event Detection", "Neurocardiac Monitoring"],
        "first_seen_year": 1995,
        "description": "Real-time ECG/PPG analysis for early detection of cardiac events.",
    },
    {
        "name": "Supply Chain Optimization",
        "category": "Application",
        "aliases": ["Supply Chain Management", "Logistics Optimization", "Inventory Optimization"],
        "first_seen_year": 1985,
        "description": "Using ML/RL to minimize cost and improve efficiency in supply chains.",
    },
    {
        "name": "Academic Project Evaluation",
        "category": "Application",
        "aliases": ["Project Assessment Tool", "Academic Evaluation Support"],
        "first_seen_year": 2010,
        "description": "AI-based system for evaluating and scoring academic project submissions.",
    },
    {
        "name": "Decision Support System",
        "category": "Application",
        "aliases": ["DSS", "Clinical Decision Support", "AI Decision Support"],
        "first_seen_year": 1970,
        "description": "AI system providing analytical recommendations for human decision-making.",
    },
    {
        "name": "Medical Imaging",
        "category": "Application",
        "aliases": ["Radiology AI", "Medical Image Analysis", "Clinical Imaging"],
        "first_seen_year": 1990,
        "description": "Applying ML to analyze medical images (X-ray, MRI, CT, ultrasound).",
    },
    {
        "name": "Privacy Preserving Machine Learning",
        "category": "Application",
        "aliases": ["PPML", "Privacy-secure AI", "Secure ML"],
        "first_seen_year": 2010,
        "description": "ML techniques that protect individual data privacy (FL, DP, HE).",
    },
    {
        "name": "Video Analytics",
        "category": "Application",
        "aliases": ["Video Intelligence", "Video Surveillance AI", "Smart CCTV"],
        "first_seen_year": 2003,
        "description": "Automated analysis of video streams for events, objects, and behavior.",
    },
    {
        "name": "Edge AI",
        "category": "Application",
        "aliases": ["On-device AI", "Edge Inference", "TinyML"],
        "first_seen_year": 2017,
        "description": "Running AI inference at the network edge without cloud roundtrips.",
    },
    {
        "name": "Explainable AI",
        "category": "Application",
        "aliases": ["XAI", "Model Interpretability", "AI Transparency"],
        "first_seen_year": 2016,
        "description": "Methods and tools to make ML model decisions understandable to humans.",
    },

    # ── Technologies ─────────────────────────────────────────────────────────
    {
        "name": "Blockchain",
        "category": "Technology",
        "aliases": ["Distributed Ledger", "DLT", "Web3"],
        "first_seen_year": 2008,
        "description": "Decentralized immutable ledger securing transactions via cryptographic hashing.",
    },
    {
        "name": "Smart Contract",
        "category": "Technology",
        "aliases": ["Self-executing Contract", "Solidity Contract", "ERC-20"],
        "first_seen_year": 1994,
        "description": "Self-executing code stored on a blockchain that enforces contract terms.",
    },
    {
        "name": "IPFS",
        "category": "Technology",
        "aliases": ["InterPlanetary File System", "Content Addressing", "Filecoin"],
        "first_seen_year": 2014,
        "description": "Peer-to-peer distributed file system using content-addressed storage.",
    },
    {
        "name": "Differential Privacy",
        "category": "Technology",
        "aliases": ["DP", "Epsilon-Delta Privacy", "Noise Injection"],
        "first_seen_year": 2006,
        "description": "Mathematical framework guaranteeing individual records cannot be re-identified.",
    },
    {
        "name": "Homomorphic Encryption",
        "category": "Technology",
        "aliases": ["HE", "FHE", "Fully Homomorphic Encryption", "CKKS", "BFV"],
        "first_seen_year": 2009,
        "description": "Encryption scheme allowing computation on ciphertext without decryption.",
    },
    {
        "name": "TensorRT",
        "category": "Technology",
        "aliases": ["NVIDIA TensorRT", "TRT"],
        "first_seen_year": 2017,
        "description": "NVIDIA SDK for high-performance deep learning inference on GPU.",
    },
    {
        "name": "ONNX Runtime",
        "category": "Technology",
        "aliases": ["ORT", "ONNX Inference"],
        "first_seen_year": 2018,
        "description": "High-performance inference engine for ONNX models across hardware backends.",
    },
    {
        "name": "NVIDIA DeepStream",
        "category": "Technology",
        "aliases": ["DeepStream SDK", "DeepStream"],
        "first_seen_year": 2018,
        "description": "NVIDIA SDK for AI-powered video analytics pipelines on Jetson/GPU.",
    },
    {
        "name": "Edge Computing",
        "category": "Technology",
        "aliases": ["Fog Computing", "Multi-access Edge Computing", "MEC"],
        "first_seen_year": 2009,
        "description": "Distributed computing paradigm that processes data near the source.",
    },
    {
        "name": "Quantum Computing",
        "category": "Technology",
        "aliases": ["Quantum Hardware", "Qiskit", "Cirq", "PennyLane"],
        "first_seen_year": 1981,
        "description": "Computing using quantum-mechanical phenomena like superposition and entanglement.",
    },
    {
        "name": "Remote Sensing",
        "category": "Technology",
        "aliases": ["Satellite Imagery", "SAR", "Synthetic Aperture Radar", "Earth Observation"],
        "first_seen_year": 1960,
        "description": "Acquiring information about the Earth's surface without physical contact.",
    },
    {
        "name": "Wearable Sensor",
        "category": "Technology",
        "aliases": ["Wearable Device", "Biosensor", "IoT Sensor", "ECG Sensor", "PPG Sensor"],
        "first_seen_year": 1998,
        "description": "Body-worn sensor collecting physiological or motion data.",
    },
    {
        "name": "GDPR",
        "category": "Technology",
        "aliases": ["General Data Protection Regulation", "Data Privacy Regulation", "CCPA"],
        "first_seen_year": 2016,
        "description": "EU regulation governing personal data protection and privacy.",
    },
    {
        "name": "Secure Aggregation",
        "category": "Technology",
        "aliases": ["SecAgg", "Privacy-preserving Aggregation"],
        "first_seen_year": 2017,
        "description": "Cryptographic protocol aggregating model updates in FL without exposing individuals.",
    },
    {
        "name": "Grafana",
        "category": "Technology",
        "aliases": ["Grafana Dashboard", "Prometheus"],
        "first_seen_year": 2014,
        "description": "Open-source analytics and monitoring visualization platform.",
    },
    {
        "name": "Elasticsearch",
        "category": "Technology",
        "aliases": ["Elastic Search", "ELK Stack", "OpenSearch"],
        "first_seen_year": 2010,
        "description": "Distributed search and analytics engine for log and data analysis.",
    },
    {
        "name": "Whisper API",
        "category": "Technology",
        "aliases": ["OpenAI Whisper API", "Speech-to-Text API"],
        "first_seen_year": 2022,
        "description": "Cloud API for automatic speech recognition using OpenAI Whisper model.",
    },
    {
        "name": "Firebase",
        "category": "Technology",
        "aliases": ["Firebase Realtime DB", "Firestore", "Firebase Auth"],
        "first_seen_year": 2012,
        "description": "Google's mobile and web application development platform with BaaS features.",
    },
    {
        "name": "MongoDB",
        "category": "Technology",
        "aliases": ["Mongo", "NoSQL Database", "Document Database"],
        "first_seen_year": 2009,
        "description": "Document-oriented NoSQL database storing data in flexible JSON-like BSON format.",
    },
    {
        "name": "WebRTC",
        "category": "Technology",
        "aliases": ["Real-Time Communication", "WebSocket", "Peer-to-Peer"],
        "first_seen_year": 2011,
        "description": "Browser API enabling real-time audio/video/data peer-to-peer communication.",
    },

    # ── Hardware ─────────────────────────────────────────────────────────────
    {
        "name": "Coral Edge TPU",
        "category": "Hardware",
        "aliases": ["Google Coral", "Coral Dev Board", "Coral USB Accelerator"],
        "first_seen_year": 2019,
        "description": "Google's ASIC for accelerating TensorFlow Lite inference at the edge.",
    },
    {
        "name": "FPGA",
        "category": "Hardware",
        "aliases": ["Field Programmable Gate Array", "Xilinx FPGA", "Intel FPGA", "Altera"],
        "first_seen_year": 1985,
        "description": "Reconfigurable hardware for custom digital logic acceleration.",
    },
    {
        "name": "Arduino",
        "category": "Hardware",
        "aliases": ["Arduino Uno", "Arduino Nano", "Arduino Mega"],
        "first_seen_year": 2005,
        "description": "Open-source microcontroller platform widely used in IoT prototyping.",
    },
    {
        "name": "IMU Sensor",
        "category": "Hardware",
        "aliases": ["Inertial Measurement Unit", "Accelerometer", "Gyroscope", "MPU-6050"],
        "first_seen_year": 1954,
        "description": "Sensor measuring acceleration, angular velocity, and magnetic field.",
    },
    {
        "name": "Ultrasonic Sensor",
        "category": "Hardware",
        "aliases": ["HC-SR04", "Sonar Sensor", "Proximity Sensor"],
        "first_seen_year": 1940,
        "description": "Sensor using sound waves to measure distance.",
    },

    # ── Libraries ─────────────────────────────────────────────────────────────
    {
        "name": "Pandas",
        "category": "Library",
        "aliases": ["pandas", "DataFrame", "Python Data Analysis"],
        "first_seen_year": 2008,
        "description": "Python library for data manipulation and analysis with DataFrame abstraction.",
    },
    {
        "name": "NumPy",
        "category": "Library",
        "aliases": ["numpy", "np"],
        "first_seen_year": 2006,
        "description": "Python library for numerical computation with multi-dimensional arrays.",
    },
    {
        "name": "Matplotlib",
        "category": "Library",
        "aliases": ["pyplot", "Seaborn", "Plotly"],
        "first_seen_year": 2003,
        "description": "Python 2D/3D plotting library for data visualization.",
    },
    {
        "name": "NetworkX",
        "category": "Library",
        "aliases": ["networkx"],
        "first_seen_year": 2004,
        "description": "Python library for creation and analysis of complex networks and graphs.",
    },
    {
        "name": "NLTK",
        "category": "Library",
        "aliases": ["Natural Language Toolkit", "nltk"],
        "first_seen_year": 2001,
        "description": "Python platform for building NLP programs with text corpora.",
    },
    {
        "name": "Dlib",
        "category": "Library",
        "aliases": ["dlib"],
        "first_seen_year": 2009,
        "description": "C++ ML toolkit with Python bindings for face detection and landmark prediction.",
    },
    {
        "name": "Librosa",
        "category": "Library",
        "aliases": ["librosa", "Audio Feature Extraction"],
        "first_seen_year": 2015,
        "description": "Python library for music and audio analysis.",
    },
    {
        "name": "Streamlit",
        "category": "Library",
        "aliases": ["streamlit", "Streamlit App"],
        "first_seen_year": 2019,
        "description": "Python framework for rapidly building interactive ML/data apps.",
    },
    {
        "name": "Gradio",
        "category": "Library",
        "aliases": ["gradio"],
        "first_seen_year": 2019,
        "description": "Python library for building ML demo web interfaces in minutes.",
    },

    # ── Frameworks ───────────────────────────────────────────────────────────
    {
        "name": "Detectron2",
        "category": "Framework",
        "aliases": ["Facebook Detectron2", "detectron2"],
        "first_seen_year": 2019,
        "description": "Meta's modular object detection and segmentation research platform.",
    },
    {
        "name": "MMDetection",
        "category": "Framework",
        "aliases": ["mmdet", "OpenMMLab"],
        "first_seen_year": 2019,
        "description": "OpenMMLab's detection toolbox supporting 100+ detection algorithms.",
    },
    {
        "name": "Hugging Face PEFT",
        "category": "Framework",
        "aliases": ["PEFT", "LoRA PEFT", "Parameter Efficient Fine-Tuning"],
        "first_seen_year": 2023,
        "description": "Hugging Face library for parameter-efficient fine-tuning (LoRA, IA3, etc.).",
    },

    # ── Datasets ─────────────────────────────────────────────────────────────
    {
        "name": "PhiUSIIL",
        "category": "Dataset",
        "aliases": ["Phishing URL Dataset", "UCI Phishing Dataset"],
        "first_seen_year": 2012,
        "description": "Benchmark dataset of phishing and legitimate URLs for ML classification.",
    },
    {
        "name": "MNIST",
        "category": "Dataset",
        "aliases": ["Modified NIST", "Handwritten Digits Dataset"],
        "first_seen_year": 1998,
        "description": "70,000 handwritten digit images widely used for classification benchmarks.",
    },
    {
        "name": "UCF-101",
        "category": "Dataset",
        "aliases": ["UCF101", "Action Recognition Dataset"],
        "first_seen_year": 2012,
        "description": "101-class human action recognition dataset from YouTube videos.",
    },
    {
        "name": "HMDB-51",
        "category": "Dataset",
        "aliases": ["HMDB51", "Human Motion Database"],
        "first_seen_year": 2011,
        "description": "51-class action recognition benchmark from movie/web video clips.",
    },
    {
        "name": "NSL-KDD",
        "category": "Dataset",
        "aliases": ["NSL KDD", "KDD Cup 99 Updated", "Network Intrusion Dataset"],
        "first_seen_year": 2009,
        "description": "Benchmark dataset for network intrusion detection research.",
    },
    {
        "name": "UNSW-NB15",
        "category": "Dataset",
        "aliases": ["UNSW NB15", "Cyber Attack Dataset"],
        "first_seen_year": 2015,
        "description": "Network traffic dataset with 9 attack categories for IDS evaluation.",
    },
    {
        "name": "PhysioNet",
        "category": "Dataset",
        "aliases": ["MIT-BIH", "ECG Dataset", "PTB-XL", "PhysioBank"],
        "first_seen_year": 2000,
        "description": "Repository of physiological signal datasets for biomedical research.",
    },
    {
        "name": "ISIC Dataset",
        "category": "Dataset",
        "aliases": ["ISIC", "Skin Lesion Dataset", "Dermoscopy Dataset"],
        "first_seen_year": 2016,
        "description": "International Skin Imaging Collaboration dataset for melanoma classification.",
    },
    {
        "name": "Thyroid Ultrasound Dataset",
        "category": "Dataset",
        "aliases": ["TN3K", "DDTI", "Thyroid Dataset"],
        "first_seen_year": 2010,
        "description": "Ultrasound image dataset for thyroid nodule detection/classification.",
    },
    {
        "name": "Open Images",
        "category": "Dataset",
        "aliases": ["Google Open Images", "OID"],
        "first_seen_year": 2016,
        "description": "Large-scale dataset with 9M images, 600 object classes with bounding boxes.",
    },
    {
        "name": "CIFAR-10",
        "category": "Dataset",
        "aliases": ["CIFAR10", "CIFAR-100"],
        "first_seen_year": 2009,
        "description": "60,000 32x32 images in 10 object classes for image classification benchmarks.",
    },

    # ── Metrics ───────────────────────────────────────────────────────────────
    {
        "name": "F1-Score",
        "category": "Metric",
        "aliases": ["F1", "F-Measure", "F1 Score", "Macro F1", "Micro F1"],
        "first_seen_year": 1992,
        "description": "Harmonic mean of precision and recall for classification evaluation.",
    },
    {
        "name": "Accuracy",
        "category": "Metric",
        "aliases": ["Classification Accuracy", "Top-1 Accuracy", "Top-5 Accuracy"],
        "first_seen_year": 1955,
        "description": "Proportion of correct predictions to total predictions.",
    },
    {
        "name": "Precision",
        "category": "Metric",
        "aliases": ["Positive Predictive Value", "PPV"],
        "first_seen_year": 1955,
        "description": "Ratio of true positives to all predicted positives.",
    },
    {
        "name": "Recall",
        "category": "Metric",
        "aliases": ["Sensitivity", "True Positive Rate", "TPR"],
        "first_seen_year": 1955,
        "description": "Ratio of true positives to all actual positives.",
    },
    {
        "name": "AUC-ROC",
        "category": "Metric",
        "aliases": ["ROC Curve", "AUC", "AUROC"],
        "first_seen_year": 1975,
        "description": "Area under the receiver operating characteristic curve.",
    },
    {
        "name": "Mean Average Precision",
        "category": "Metric",
        "aliases": ["mAP", "mAP@50", "mAP@0.5:0.95"],
        "first_seen_year": 2006,
        "description": "Average detection accuracy over multiple IoU thresholds used in COCO benchmark.",
    },
    {
        "name": "BLEU Score",
        "category": "Metric",
        "aliases": ["BLEU", "Bilingual Evaluation Understudy"],
        "first_seen_year": 2002,
        "description": "N-gram overlap metric for evaluating machine translation quality.",
    },
    {
        "name": "ROUGE",
        "category": "Metric",
        "aliases": ["ROUGE-L", "ROUGE-1", "ROUGE-2"],
        "first_seen_year": 2004,
        "description": "Recall-oriented metric set for automatic summarization evaluation.",
    },
    {
        "name": "Intersection over Union",
        "category": "Metric",
        "aliases": ["IoU", "Jaccard Index", "mIoU"],
        "first_seen_year": 1901,
        "description": "Overlap measure between predicted and ground truth bounding boxes/masks.",
    },
    {
        "name": "Mean Squared Error",
        "category": "Metric",
        "aliases": ["MSE", "RMSE", "Root Mean Squared Error", "MAE"],
        "first_seen_year": 1900,
        "description": "Average squared difference between predictions and actual values.",
    },
    {
        "name": "Perplexity",
        "category": "Metric",
        "aliases": ["PPL", "Language Model Perplexity"],
        "first_seen_year": 1977,
        "description": "Measure of how well a language model predicts a text sample.",
    },
    {
        "name": "FID Score",
        "category": "Metric",
        "aliases": ["Frechet Inception Distance", "FID"],
        "first_seen_year": 2017,
        "description": "Quality metric for generative models comparing feature distributions.",
    },
    {
        "name": "Latency",
        "category": "Metric",
        "aliases": ["Inference Latency", "Response Time", "FPS"],
        "first_seen_year": 1950,
        "description": "Time taken for a model to process one input and return an output.",
    },
    {
        "name": "Specificity",
        "category": "Metric",
        "aliases": ["True Negative Rate", "TNR"],
        "first_seen_year": 1955,
        "description": "Proportion of true negatives correctly identified.",
    },
]


def load_existing() -> list[dict]:
    if KB_PATH.exists():
        return json.loads(KB_PATH.read_text(encoding="utf-8"))
    return []


def build_name_set(data: list[dict]) -> set[str]:
    """Return lower-cased set of all names + aliases in existing KB."""
    result = set()
    for e in data:
        result.add(e["name"].lower().strip())
        for a in e.get("aliases", []):
            if a:
                result.add(a.lower().strip())
    return result


def main():
    existing = load_existing()
    known = build_name_set(existing)

    added = 0
    skipped = 0
    for entry in NEW_ENTRIES:
        name_lower = entry["name"].lower().strip()
        if name_lower in known:
            print(f"  SKIP (exists): {entry['name']}")
            skipped += 1
            continue

        # Check if any alias already in KB
        alias_conflict = next(
            (a for a in entry.get("aliases", []) if a.lower().strip() in known), None
        )
        if alias_conflict:
            print(f"  SKIP (alias match '{alias_conflict}'): {entry['name']}")
            skipped += 1
            continue

        existing.append(entry)
        # Update known set so we don't add duplicates within this batch
        known.add(name_lower)
        for a in entry.get("aliases", []):
            if a:
                known.add(a.lower().strip())
        print(f"  ADD [{entry['category']}]: {entry['name']}")
        added += 1

    KB_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'=' * 50}")
    print(f"Added   : {added}")
    print(f"Skipped : {skipped} (already existed)")
    print(f"Total   : {len(existing)} entries in KB")
    print(f"Saved   : {KB_PATH}")

    # Category summary
    cats: dict[str, int] = {}
    for e in existing:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print("\nCategory breakdown:")
    for k, v in sorted(cats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
