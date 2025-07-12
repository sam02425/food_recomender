#!/usr/bin/env python3
"""
Cleanup script to remove face recognition and dish name endpoints
from the backend for the improved experiment
"""

import os
import re
from pathlib import Path

def remove_face_recognition_endpoints():
    """Remove face recognition endpoints from backend files"""

    # Files to clean
    files_to_clean = [
        "backend/main.py",
        "simple_server.py"
    ]

    for file_path in files_to_clean:
        if not os.path.exists(file_path):
            continue

        print(f"Cleaning {file_path}...")

        with open(file_path, 'r') as f:
            content = f.read()

        # Remove face recognition endpoints
        patterns_to_remove = [
            r'@app\.post\("/api/face-recognition"\).*?def face_recognition.*?except Exception as e:.*?return.*?}\n',
            r'@app\.post\("/api/track-mood"\).*?def track_real_time_mood.*?except Exception as e:.*?return.*?}\n',
            r'@app\.post\("/api/analyze-recommendation-reaction"\).*?def analyze_recommendation_reaction.*?except Exception as e:.*?return.*?}\n',
            r'@app\.post\("/api/end-mood-session"\).*?def end_mood_tracking_session.*?except Exception as e:.*?return.*?}\n',
            r'@app\.get\("/api/mood-statistics"\).*?def get_mood_statistics.*?except Exception as e:.*?return.*?}\n',
            r'@app\.post\("/api/store-customer-face"\).*?def store_customer_face.*?except Exception as e:.*?return.*?}\n',
        ]

        for pattern in patterns_to_remove:
            content = re.sub(pattern, '# Face recognition endpoint removed\n', content, flags=re.DOTALL)

        # Remove dish name endpoints
        dish_patterns = [
            r'@app\.post\("/api/dish-name"\).*?def get_dish_name.*?except Exception as e:.*?return.*?}\n',
        ]

        for pattern in dish_patterns:
            content = re.sub(pattern, '# Dish name endpoint removed\n', content, flags=re.DOTALL)

        # Remove related imports and models
        content = re.sub(r'class FaceRecognitionRequest.*?}\n', '# FaceRecognitionRequest model removed\n', content, flags=re.DOTALL)
        content = re.sub(r'class StoreCustomerFaceRequest.*?}\n', '# StoreCustomerFaceRequest model removed\n', content, flags=re.DOTALL)

        # Remove ML-related imports
        content = re.sub(r'import cv2.*?\n', '# ML imports removed\n', content)
        content = re.sub(r'from fer import FER.*?\n', '# FER import removed\n', content)
        content = re.sub(r'import base64.*?\n', '# base64 import removed\n', content)
        content = re.sub(r'from PIL import Image.*?\n', '# PIL import removed\n', content)

        # Write cleaned content
        with open(file_path, 'w') as f:
            f.write(content)

        print(f"✅ Cleaned {file_path}")

def update_experiment_data_model():
    """Update ExperimentData model to remove face-related fields"""

    files_to_update = [
        "backend/main.py",
        "simple_server.py"
    ]

    for file_path in files_to_update:
        if not os.path.exists(file_path):
            continue

        print(f"Updating ExperimentData model in {file_path}...")

        with open(file_path, 'r') as f:
            content = f.read()

        # Update ExperimentData model
        old_model = r'class ExperimentData\(BaseModel\):.*?final_dish_name: Optional\[str\] = None'
        new_model = '''class ExperimentData(BaseModel):
    experiment_id: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    # Face recognition and dish name fields removed for experiment
    selected_base: Optional[str] = None
    selected_protein: Optional[str] = None
    selected_veggies: Optional[List[str]] = None
    selected_sauce: Optional[str] = None
    final_order_details: dict'''

        content = re.sub(old_model, new_model, content, flags=re.DOTALL)

        with open(file_path, 'w') as f:
            f.write(content)

        print(f"✅ Updated ExperimentData model in {file_path}")

def main():
    """Main cleanup function"""
    print("🧹 Starting backend cleanup...")

    # Remove face recognition and dish name endpoints
    remove_face_recognition_endpoints()

    # Update experiment data model
    update_experiment_data_model()

    print("✅ Backend cleanup completed!")
    print("\n📝 Summary of changes:")
    print("   - Removed face recognition endpoints")
    print("   - Removed dish name generation endpoints")
    print("   - Removed mood tracking endpoints")
    print("   - Removed ML-related imports")
    print("   - Updated ExperimentData model")
    print("\n🚀 Backend is now ready for the improved experiment!")

if __name__ == "__main__":
    main()