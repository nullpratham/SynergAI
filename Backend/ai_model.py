"""
SynergAI — Custom AI Matching Model
====================================
A neural network trained to understand team composition.
It doesn't just match similar people — it matches COMPLEMENTARY ones.

A Backend dev needs a Frontend dev, not another Backend dev.
An ML Engineer needs a Data person and someone to deploy.

The model learns these relationships from training data.
"""

import os
import json
import pickle
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

SKILLS = [
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#", "Ruby", "Swift", "Kotlin", "PHP", "SQL",
    # Frontend
    "React", "Angular", "Vue.js", "Next.js", "Svelte", "TailwindCSS", "Bootstrap", "HTML5", "CSS3",
    # Backend
    "Node.js", "Django", "Flask", "Express.js", "Spring Boot", "Gin", "ASP.NET", "FastAPI",
    # Cloud & Infra
    "AWS", "Azure", "GCP", "Terraform", "CloudFormation", "Serverless", "Docker", "Kubernetes", "Jenkins", "GitHub Actions",
    # Data & AI
    "PyTorch", "TensorFlow", "Scikit-learn", "Spark", "Kafka", "dbt", "Pandas", "NumPy", "OpenCV", "LangChain", "OpenAI API",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch",
    # Mobile & UI
    "React Native", "Flutter", "SwiftUI", "Jetpack Compose", "Figma", "Adobe XD"
]

ROLES = [
    "AI & Machine Learning Engineer",
    "DevOps / DevSecOps Engineer",
    "Cloud Architect",
    "Data Engineer",
    "Data Scientist",
    "Site Reliability Engineer (SRE)",
    "Cybersecurity Engineer",
    "Full-Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "UI/UX Designer",
    "Project Manager",
    "Mobile App Developer",
    "Blockchain Developer",
    "QA Automation Engineer"
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), "ai_models")
MODEL_PATH = os.path.join(MODEL_DIR, "match_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")


# ──────────────────────────────────────────────
# Feature Encoding
# ──────────────────────────────────────────────

def encode_skills(skills_str):
    """Convert comma-separated skills string to a one-hot vector."""
    vec = np.zeros(len(SKILLS))
    if not skills_str:
        return vec
    user_skills = [s.strip().lower() for s in skills_str.split(",")]
    for i, skill in enumerate(SKILLS):
        if skill.lower() in user_skills:
            vec[i] = 1.0
    return vec


def encode_role(role_str):
    """Convert role string to a one-hot vector."""
    vec = np.zeros(len(ROLES))
    if not role_str:
        return vec
    role_lower = role_str.strip().lower()
    for i, role in enumerate(ROLES):
        if role.lower() == role_lower:
            vec[i] = 1.0
            break
    return vec


def encode_user(user_dict):
    """Encode a user's profile into a feature vector."""
    skills_vec = encode_skills(user_dict.get("skills", ""))
    role_vec = encode_role(user_dict.get("role", ""))
    return np.concatenate([skills_vec, role_vec])


def encode_pair(user_a, user_b):
    """Encode a pair of users into a single feature vector for the model."""
    vec_a = encode_user(user_a)
    vec_b = encode_user(user_b)

    skills_a = encode_skills(user_a.get("skills", ""))
    skills_b = encode_skills(user_b.get("skills", ""))

    # Interaction features
    skill_overlap = np.sum(skills_a * skills_b)
    skill_complement = np.sum(skills_b * (1 - skills_a))
    total_skills = np.sum(skills_a) + np.sum(skills_b)

    role_a = encode_role(user_a.get("role", ""))
    role_b = encode_role(user_b.get("role", ""))
    same_role = float(np.dot(role_a, role_b) > 0)

    interaction = np.array([
        skill_overlap,
        skill_complement,
        total_skills,
        same_role,
        1.0 - same_role
    ])

    return np.concatenate([vec_a, vec_b, interaction])


# ──────────────────────────────────────────────
# Complementarity Rules (domain knowledge)
# ──────────────────────────────────────────────

# Which roles complement each other (higher = better team fit)
ROLE_COMPLEMENT_SCORE = {
    ("Backend Developer",   "Frontend Developer"):  0.95,
    ("Backend Developer",   "UI/UX Designer"):      0.85,
    ("Backend Developer",   "DevOps / DevSecOps Engineer"): 0.90,
    ("Frontend Developer",  "UI/UX Designer"):      0.95,
    ("AI & Machine Learning Engineer", "Data Engineer"): 0.95,
    ("AI & Machine Learning Engineer", "Data Scientist"): 0.85,
    ("AI & Machine Learning Engineer", "DevOps / DevSecOps Engineer"): 0.85,
    ("Data Engineer",       "Data Scientist"):      0.90,
    ("Cybersecurity Engineer", "DevOps / DevSecOps Engineer"): 0.90,
    ("Full-Stack Developer","UI/UX Designer"):      0.85,
    ("Mobile App Developer","UI/UX Designer"):      0.90,
    ("Mobile App Developer","Backend Developer"):   0.85,
    ("Project Manager",     "Full-Stack Developer"): 0.80,
    ("Project Manager",     "Site Reliability Engineer (SRE)"): 0.75,
    ("QA Automation Engineer", "Backend Developer"): 0.80,
    ("QA Automation Engineer", "Frontend Developer"): 0.80,
    ("Blockchain Developer", "Cybersecurity Engineer"): 0.85,
    ("Cloud Architect",     "DevOps / DevSecOps Engineer"): 1.00,
}

# Same role = they compete, not complement
SAME_ROLE_PENALTY = 0.20


def get_role_complement_score(role_a, role_b):
    """Look up the complement score for two roles."""
    if not role_a or not role_b:
        return 0.5

    ra = role_a.strip()
    rb = role_b.strip()

    if ra == rb:
        return SAME_ROLE_PENALTY

    # Check both orderings
    key1 = (ra, rb)
    key2 = (rb, ra)

    if key1 in ROLE_COMPLEMENT_SCORE:
        return ROLE_COMPLEMENT_SCORE[key1]
    if key2 in ROLE_COMPLEMENT_SCORE:
        return ROLE_COMPLEMENT_SCORE[key2]

    return 0.50  # unknown pair


# ──────────────────────────────────────────────
# Training Data Generator
# ──────────────────────────────────────────────

def generate_training_data(n_samples=150000):
    """Generate synthetic training pairs with compatibility labels.
    
    The labels encode our domain knowledge:
    - Complementary roles score high
    - Same roles score low
    - Diverse skills across a pair score high
    - Some shared skills are good (communication overlap)
    """
    rng = np.random.RandomState(42)
    X = []
    y = []

    for _ in range(n_samples):
        # Random user A
        n_skills_a = rng.randint(1, 6)
        skills_a_idx = rng.choice(len(SKILLS), size=n_skills_a, replace=False)
        skills_a = ", ".join([SKILLS[i] for i in skills_a_idx])
        role_a = ROLES[rng.randint(0, len(ROLES))]

        # Random user B
        n_skills_b = rng.randint(1, 6)
        skills_b_idx = rng.choice(len(SKILLS), size=n_skills_b, replace=False)
        skills_b = ", ".join([SKILLS[i] for i in skills_b_idx])
        role_b = ROLES[rng.randint(0, len(ROLES))]

        user_a = {"skills": skills_a, "role": role_a}
        user_b = {"skills": skills_b, "role": role_b}

        # ── Calculate the "true" compatibility score ──
        # 1. Role complementarity (biggest factor: 40%)
        role_score = get_role_complement_score(role_a, role_b)

        # 2. Skill diversity (30%) — they should cover more ground together
        all_skills = set(skills_a_idx) | set(skills_b_idx)
        diversity = len(all_skills) / min(n_skills_a + n_skills_b, len(SKILLS))

        # 3. Some overlap is good (20%) — they can communicate
        overlap = len(set(skills_a_idx) & set(skills_b_idx))
        overlap_score = min(overlap / max(n_skills_a, 1), 0.5) * 2  # cap at 1.0

        # 4. Team balance (10%) — similar skill counts are good
        balance = 1.0 - abs(n_skills_a - n_skills_b) / max(n_skills_a, n_skills_b)

        # Weighted combination
        score = (
            0.40 * role_score +
            0.30 * diversity +
            0.20 * overlap_score +
            0.10 * balance
        )

        # Add some noise
        score += rng.normal(0, 0.05)
        score = np.clip(score, 0.0, 1.0)

        features = encode_pair(user_a, user_b)
        X.append(features)
        y.append(score)

    return np.array(X), np.array(y)


# ──────────────────────────────────────────────
# Model Training
# ──────────────────────────────────────────────

def train_model():
    """Train the matching neural network and save it to disk."""
    print("🧠 Generating massive training data (150,000 samples)...")
    X, y = generate_training_data(n_samples=150000)

    print(f"   → {X.shape[0]} training samples, {X.shape[1]} features each")

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("🔧 Training deep neural network (512x256x128x64x32)...")
    model = MLPRegressor(
        hidden_layer_sizes=(512, 256, 128, 64, 32),
        activation="relu",
        solver="adam",
        max_iter=300,
        learning_rate="adaptive",
        learning_rate_init=0.001,
        early_stopping=True,
        validation_fraction=0.1,
        random_state=42,
        verbose=True
    )

    model.fit(X_scaled, y)

    # Save model and scaler
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    # Report
    train_score = model.score(X_scaled, y)
    print(f"✅ Model trained! R² score: {train_score:.4f}")
    print(f"   → Saved to {MODEL_PATH}")
    return model, scaler


# ──────────────────────────────────────────────
# Model Loading & Prediction
# ──────────────────────────────────────────────

_model_cache = {}

def load_model():
    """Load the trained model from disk (cached)."""
    if "model" not in _model_cache:
        if not os.path.exists(MODEL_PATH):
            print("⚠️  No trained model found. Training now...")
            model, scaler = train_model()
            _model_cache["model"] = model
            _model_cache["scaler"] = scaler
        else:
            with open(MODEL_PATH, "rb") as f:
                _model_cache["model"] = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                _model_cache["scaler"] = pickle.load(f)
    return _model_cache["model"], _model_cache["scaler"]


def predict_match_score(user_a, user_b):
    """Predict the compatibility score between two users (0-100)."""
    model, scaler = load_model()
    features = encode_pair(user_a, user_b).reshape(1, -1)
    features_scaled = scaler.transform(features)
    score = model.predict(features_scaled)[0]
    return int(np.clip(score * 100, 0, 100))


def get_ai_matches(current_user, other_users):
    """Rank all other users by AI-predicted compatibility."""
    matches = []
    for user in other_users:
        score = predict_match_score(current_user, user)
        matches.append({
            "id": user["id"],
            "name": user["name"],
            "skills": user.get("skills", "No skills listed"),
            "interests": user.get("interests", ""),
            "score": score,
            "role": user.get("role", "Student"),
            "university": user.get("university", "")
        })

    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


# ──────────────────────────────────────────────
# CLI: Train from command line
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  SynergAI Matching Model — Training")
    print("=" * 50)
    train_model()

    # Quick test
    print("\n🧪 Quick test predictions:")
    test_cases = [
        (
            {"skills": "Python, FastAPI, PostgreSQL", "role": "Backend Developer"},
            {"skills": "React, TailwindCSS, Figma", "role": "Frontend Developer"},
            "Backend + Frontend (should be HIGH)"
        ),
        (
            {"skills": "PyTorch, TensorFlow, Pandas", "role": "AI & Machine Learning Engineer"},
            {"skills": "Docker, Kubernetes, AWS", "role": "DevOps / DevSecOps Engineer"},
            "AI + DevOps (should be HIGH)"
        ),
        (
            {"skills": "Python, SQL, Spark", "role": "Data Engineer"},
            {"skills": "Scikit-learn, Pandas, NumPy", "role": "Data Scientist"},
            "Data Eng + Data Sci (should be HIGH)"
        ),
    ]

    for user_a, user_b, label in test_cases:
        score = predict_match_score(user_a, user_b)
        print(f"   {label}: {score}%")
