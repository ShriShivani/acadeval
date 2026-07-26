"""
Seed Database with Demo Accounts and Initial Sample Projects
============================================================
Creates standard demo accounts and populates sample projects with evaluation
reports, knowledge graph nodes, and citations so the dashboard is immediately
rich with data upon login.
"""

import logging
import uuid
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.project import Project, SubmissionType, PipelineStatus
from app.models.evaluation import EvaluationReport
from app.utils.auth import hash_password

log = logging.getLogger(__name__)

DEMO_USERS = [
    {
        "name": "Priya Sharma",
        "email": "priya@college.edu",
        "role": UserRole.student,
        "department": "Computer Science & Engineering",
        "roll_no": "CS2021001",
    },
    {
        "name": "Dr. Meera Krishnan",
        "email": "meera@college.edu",
        "role": UserRole.guide,
        "department": "Computer Science & Engineering",
    },
    {
        "name": "Prof. Suresh Rajan",
        "email": "suresh@college.edu",
        "role": UserRole.reviewer,
        "department": "Computer Science & Engineering",
    },
    {
        "name": "Dr. K. V. Ramanathan",
        "email": "hod@college.edu",
        "role": UserRole.hod,
        "department": "Computer Science & Engineering",
    },
]

DEMO_PROJECTS = [
    {
        "title": "AI-Powered Plant Crop Disease Detection",
        "domain": "Artificial Intelligence / Machine Learning",
        "submission_type": SubmissionType.document,
        "abstract": "This project proposes a hybrid deep learning model combining Convolutional Neural Networks (CNN) and Vision Transformers (ViT) to detect crop diseases from leaf images. We train on the PlantVillage dataset using PyTorch and FastAPI backend.",
        "extracted_entities": {
            "algorithms": ["CNN", "Vision Transformer", "ResNet50"],
            "technologies": ["FastAPI", "Python", "Docker"],
            "frameworks": ["PyTorch"],
            "libraries": ["NumPy", "OpenCV"],
            "datasets": ["PlantVillage Dataset"],
            "applications": ["Agricultural AI System"],
            "hardware": ["NVIDIA RTX GPU"],
            "metrics": ["Accuracy", "F1-Score"]
        },
        "score": 8.8,
        "grade": "A",
        "novelty": 82.5,
        "verdict": "Novel"
    },
    {
        "title": "Real-Time Brain-Computer Interface using OpenBCI EEG Signals",
        "domain": "Biomedical Engineering / Signal Processing",
        "submission_type": SubmissionType.document,
        "abstract": "We develop a low-cost motor imagery Brain-Computer Interface (BCI) system using an 8-channel OpenBCI Cyton headset. Feature extraction uses Common Spatial Patterns (CSP) and classification via Support Vector Machines (SVM).",
        "extracted_entities": {
            "algorithms": ["Support Vector Machine", "Common Spatial Patterns", "Bandpass Filter"],
            "technologies": ["Python", "FastAPI", "OpenBCI Cyton"],
            "frameworks": ["Scikit-Learn"],
            "libraries": ["MNE-Python", "SciPy"],
            "datasets": ["BCI Competition IV Dataset"],
            "applications": ["Assistive Technology"],
            "hardware": ["OpenBCI Headset"],
            "metrics": ["Classification Accuracy"]
        },
        "score": 9.1,
        "grade": "A+",
        "novelty": 89.0,
        "verdict": "Highly Novel"
    },
    {
        "title": "Blockchain-Based Academic Credential Verification System",
        "domain": "Cybersecurity & Blockchain",
        "submission_type": SubmissionType.abstract,
        "abstract": "A decentralized verification platform leveraging Ethereum smart contracts and IPFS for issuing and validating university transcripts and diplomas without central authority risks.",
        "extracted_entities": {
            "algorithms": ["SHA-256", "ECDSA"],
            "technologies": ["Ethereum", "IPFS", "Solidity", "Node.js"],
            "frameworks": ["Hardhat", "React"],
            "libraries": ["Ethers.js"],
            "datasets": ["University Testnet Ledger"],
            "applications": ["Credential Verification"],
            "hardware": ["Cloud Server"],
            "metrics": ["Transaction Latency", "Gas Cost"]
        },
        "score": 7.6,
        "grade": "B",
        "novelty": 68.0,
        "verdict": "Somewhat Novel"
    },
    {
        "title": "Federated Learning for Privacy-Preserving Healthcare Analytics",
        "domain": "Healthcare AI / Privacy",
        "submission_type": SubmissionType.document,
        "abstract": "We implement a decentralized privacy-preserving federated learning framework using Flower and PyTorch to train hospital diagnostic models without centralizing sensitive patient EHR records.",
        "extracted_entities": {
            "algorithms": ["Federated Averaging", "Differential Privacy", "ResNet18"],
            "technologies": ["Python", "Docker", "Flower FL"],
            "frameworks": ["PyTorch"],
            "libraries": ["Opacus", "NumPy"],
            "datasets": ["MIMIC-III EHR Dataset"],
            "applications": ["Clinical Diagnostics"],
            "hardware": ["Edge Server Nodes"],
            "metrics": ["ROC-AUC", "Privacy Budget Epsilon"]
        },
        "score": 9.3,
        "grade": "A+",
        "novelty": 92.0,
        "verdict": "Highly Novel"
    },
    {
        "title": "Autonomous UAV Navigation Using Deep Reinforcement Learning",
        "domain": "Robotics & Embedded Systems",
        "submission_type": SubmissionType.document,
        "abstract": "This project presents a Deep Q-Network (DQN) path planning algorithm for autonomous drone obstacle avoidance in GPS-denied indoor environments using ROS2 and AirSim simulation.",
        "extracted_entities": {
            "algorithms": ["Deep Q-Network", "PPO", "SLAM"],
            "technologies": ["ROS2", "Python", "AirSim"],
            "frameworks": ["PyTorch"],
            "libraries": ["OpenCV", "Gymnasium"],
            "datasets": ["AirSim Synthetic Environment"],
            "applications": ["Autonomous Robotics"],
            "hardware": ["NVIDIA Jetson Orin Nano"],
            "metrics": ["Success Rate", "Trajectory Smoothness"]
        },
        "score": 8.4,
        "grade": "A",
        "novelty": 81.0,
        "verdict": "Novel"
    },
    {
        "title": "Multimodal Sentiment Analysis of Code-Switched Hinglish Speech",
        "domain": "Natural Language Processing",
        "submission_type": SubmissionType.document,
        "abstract": "We combine Whisper ASR audio embeddings with fine-tuned RoBERTa text representations to classify emotional valence and sentiment in code-switched Hindi-English conversational speech.",
        "extracted_entities": {
            "algorithms": ["Whisper", "RoBERTa", "Attention Fusion"],
            "technologies": ["Python", "FastAPI"],
            "frameworks": ["PyTorch"],
            "libraries": ["Hugging Face Transformers", "librosa"],
            "datasets": ["MUSt-C Speech Dataset"],
            "applications": ["Conversational AI"],
            "hardware": ["NVIDIA A100 GPU"],
            "metrics": ["Weighted F1-Score", "WER"]
        },
        "score": 8.9,
        "grade": "A",
        "novelty": 86.5,
        "verdict": "Novel"
    },
    {
        "title": "IoT Smart Energy Grid Anomaly Detection Using Graph Neural Networks",
        "domain": "Internet of Things & Smart Energy",
        "submission_type": SubmissionType.document,
        "abstract": "A spatio-temporal Graph Neural Network (ST-GNN) deployed on MQTT telemetry data streams to detect unauthorized power tapping and grid voltage anomalies in real time.",
        "extracted_entities": {
            "algorithms": ["GCN", "LSTM", "Isolation Forest"],
            "technologies": ["MQTT", "InfluxDB", "Grafana"],
            "frameworks": ["PyTorch Geometric"],
            "libraries": ["NetworkX", "Pandas"],
            "datasets": ["UK-DALE Energy Dataset"],
            "applications": ["Smart Grid Monitoring"],
            "hardware": ["Raspberry Pi 4"],
            "metrics": ["Detection Latency", "Precision-Recall AUC"]
        },
        "score": 8.1,
        "grade": "A",
        "novelty": 79.5,
        "verdict": "Novel"
    }
]


def seed_demo_data():
    db = SessionLocal()
    try:
        pass_hash = hash_password("demo123")
        created_users = 0
        user_map = {}

        # 1. Seed Users
        for udata in DEMO_USERS:
            existing = db.query(User).filter(User.email == udata["email"]).first()
            if not existing:
                user = User(
                    id=uuid.uuid4(),
                    email=udata["email"],
                    name=udata["name"],
                    role=udata["role"],
                    department=udata.get("department", "CSE"),
                    roll_no=udata.get("roll_no"),
                    password_hash=pass_hash,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                user_map[udata["role"].value] = user
                created_users += 1
            else:
                user_map[udata["role"].value] = existing

        student_user = user_map.get("student")
        guide_user = user_map.get("guide")

        # 2. Seed Projects & Evaluation Reports if empty
        created_projects = 0
        for pdata in DEMO_PROJECTS:
            existing_p = db.query(Project).filter(Project.title == pdata["title"]).first()
            if not existing_p and student_user:
                p_id = uuid.uuid4()
                project = Project(
                    id=p_id,
                    title=pdata["title"],
                    domain=pdata["domain"],
                    submission_type=pdata["submission_type"],
                    student_id=student_user.id,
                    assigned_guide_id=guide_user.id if guide_user else None,
                    pipeline_status=PipelineStatus.awaiting_review,
                    extracted_entities=pdata["extracted_entities"],
                )
                db.add(project)
                db.commit()

                # Add Evaluation Report
                eval_rep = EvaluationReport(
                    project_id=p_id,
                    overall_score=pdata["score"],
                    grade=pdata["grade"],
                    novelty_score=pdata["novelty"],
                    novelty_verdict=pdata["verdict"],
                    feasibility_score=8.5,
                    completeness_score=8.0,
                    technical_depth_score=8.7,
                    clarity_score=8.4,
                    similarity_risk_score=1.2,
                    publication_potential_score=8.8,
                    similarity_internal=4.2,
                    similarity_external=8.1,
                    is_duplicate=False,
                    strengths=["Clear technical methodology", "Strong experimental dataset"],
                    weaknesses=["Could expand on edge cases"],
                    improvement_roadmap=[
                        {"week": 1, "focus": "Literature Review", "actions": ["Compare against recent SOTA baselines"]},
                        {"week": 2, "focus": "Ablation Studies", "actions": ["Feature importance analysis"]},
                        {"week": 3, "focus": "Final Report", "actions": ["Finalize documentation and repo"]}
                    ],
                    badges=["Processed by AcadEval+"],
                    writing_quality={
                        "overall_rating": "Clear & Well-Structured",
                        "metrics": {"flesch_reading_ease": 62.5, "gunning_fog": 12.1},
                        "flags": []
                    },
                    citations={
                        "summary": {"reference_count": 18, "percent_verified": 88.9, "average_reference_age": 2.4},
                        "flags": [],
                        "references": []
                    }
                )
                db.add(eval_rep)
                db.commit()

                # Ingest into Knowledge Graph (Neo4j & PostgreSQL)
                try:
                    from app.services.graph_builder import ingest_project_to_relational_graph
                    ingest_project_to_relational_graph(
                        db=db,
                        project_id=str(p_id),
                        title=pdata["title"],
                        domain=pdata["domain"],
                        sub_domain="General",
                        extracted_entities=pdata["extracted_entities"]
                    )
                except Exception as e:
                    log.warning("Graph ingestion warning during seed: %s", e)

                created_projects += 1

        print(f"Seeding finished. {created_users} new users, {created_projects} sample projects added.")

    except Exception as exc:
        db.rollback()
        log.error("Failed to seed demo data: %s", exc)
        print("Failed to seed demo data:", exc)
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
