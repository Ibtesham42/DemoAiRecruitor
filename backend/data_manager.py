import json
import os
from typing import Dict

# Define the path to the positions file
POSITIONS_FILE = "data/positions/positions.json"

def load_positions() -> Dict:
    """Load position configurations from JSON file"""
    if not os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(default_positions(), f)
    
    with open(POSITIONS_FILE, 'r') as f:
        return json.load(f)

def save_positions(positions: Dict):
    """Save position configurations to JSON file"""
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def default_positions() -> Dict:
    """Return default position configurations"""
    return {
        "Data Scientist": {
            "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
            "preferred_skills": ["TensorFlow", "PyTorch", "Big Data", "Cloud Computing"],
            "technical": [
                ["Explain bias-variance tradeoff", ["bias", "variance", "overfitting"]],
                ["Handle missing data techniques", ["imputation", "deletion", "modeling"]],
                ["Cross-validation methods", ["k-fold", "stratified", "time-series"]]
            ],
            "behavioral": [
                ["Describe complex data analysis project", ["process", "tools", "results"]],
                ["Stay updated with DS trends", ["courses", "research", "experiments"]],
                ["Handle tight deadlines", ["prioritization", "communication", "tools"]]
            ],
            "experience_threshold": 2
        },
        "Software Engineer": {
            "required_skills": ["Java", "Python", "System Design", "Algorithms", "Databases"],
            "preferred_skills": ["Microservices", "AWS", "Docker", "Kubernetes"],
            "technical": [
                ["SOLID principles explanation", ["single responsibility", "open-closed", "interface"]],
                ["Database optimization strategies", ["indexing", "normalization", "sharding"]],
                ["REST API best practices", ["stateless", "versioning", "documentation"]],
                ["Debugging complex systems", ["logging", "testing", "monitoring"]]
            ],
            "behavioral": [
                ["Handle conflicting requirements", ["communication", "prioritization", "documentation"]],
                ["Code review process", ["checklist", "automation", "feedback"]],
                ["Manage technical debt", ["refactoring", "documentation", "tooling"]]
            ],
            "experience_threshold": 3
        }
    }