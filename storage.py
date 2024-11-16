# storage.py
import json
import os
from typing import Dict, Optional
from datetime import datetime

STORAGE_FILE = 'rawdata/agent_info.json'

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)

def save_agent_info(agent_info: Dict) -> None:
    """Save agent information to JSON file"""
    ensure_data_directory()
    with open(STORAGE_FILE, 'w') as f:
        json.dump(agent_info, f, indent=2)

def load_agent_info() -> Optional[Dict]:
    """Load agent information from JSON file"""
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None



UPDATES_FILE = 'rawdata/updates.json'

def save_update(action_type: str, details: str) -> None:
    """Save a new update to updates.json"""
    ensure_data_directory()

    try:
        with open(UPDATES_FILE, 'r') as f:
            updates = json.load(f)
    except FileNotFoundError:
        updates = []

    new_update = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action_type': action_type,
        'details': details
    }

    # Add new update at the beginning
    updates.insert(0, new_update)

    # Keep only last 50 updates
    updates = updates[:50]

    with open(UPDATES_FILE, 'w') as f:
        json.dump(updates, f, indent=2)

def get_updates() -> list:
    """Load all updates from updates.json"""
    try:
        with open(UPDATES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

