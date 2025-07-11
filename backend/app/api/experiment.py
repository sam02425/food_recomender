from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, EmailStr
from backend.app.db import SessionLocal
from backend.app.models.user import User
from backend.app.models.participant import Participant
from backend.utils.experiment_logger import ExperimentLogger
from backend.app.api.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import Depends
import csv
import os
from datetime import datetime
from statistics import mean, median
from collections import Counter, defaultdict
import pandas as pd
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/experiment", tags=["experiment"])

# Update ParticipantData to include experiment_number
class ParticipantData(BaseModel):
    name: str
    email: EmailStr
    responses: dict
    experiment_number: int = 1

CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/participants.csv')

@router.post("/submit")
async def submit_participant_data(data: ParticipantData, request: Request):
    db = SessionLocal()
    try:
        participant = Participant(name=data.name, email=data.email, responses=data.responses)
        participant.experiment_number = data.experiment_number
        db.add(participant)
        db.commit()
        db.refresh(participant)
    finally:
        db.close()
    # Save to CSV (add experiment_number)
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, mode='a', newline='') as csvfile:
        fieldnames = ['name', 'email', 'responses', 'experiment_number', 'submitted_at', 'ip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'name': data.name,
            'email': data.email,
            'responses': str(data.responses),
            'experiment_number': data.experiment_number,
            'submitted_at': datetime.now().isoformat(),
            'ip': request.client.host
        })
    return {"success": True, "message": "Thank you for participating!"}

# Promote user to admin (admin only)
@router.post("/promote-user")
async def promote_user_to_admin(username: str, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.commit()
    return {"success": True, "message": f"User {username} promoted to admin."}

# Set up a new experiment (admin only)
@router.post("/setup-experiment")
async def setup_experiment(experiment_number: int, description: str, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    # Log experiment setup
    logger = ExperimentLogger(CSV_PATH.replace('participants.csv', f'experiment_{experiment_number}_log.csv'))
    logger.log('setup', {'experiment_number': experiment_number, 'description': description})
    return {"success": True, "message": f"Experiment {experiment_number} set up."}

# Get analytics for a specific experiment (admin only)
@router.get("/analytics/{experiment_number}")
async def get_experiment_analytics(experiment_number: int, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    participants = db.query(Participant).filter_by(experiment_number=experiment_number).all()
    total = len(participants)
    emails = set(p.email for p in participants)
    responses = [p.responses for p in participants]
    # Time-based stats
    times = [getattr(p, 'submitted_at', None) for p in participants if getattr(p, 'submitted_at', None)]
    if times:
        times_sorted = sorted(times)
        time_stats = {
            "earliest": str(times_sorted[0]),
            "latest": str(times_sorted[-1]),
            "average": str(times_sorted[len(times_sorted)//2]),
            "count": len(times_sorted)
        }
    else:
        time_stats = {}
    # Response breakdowns
    response_breakdown = defaultdict(Counter)
    for resp in responses:
        if isinstance(resp, dict):
            for k, v in resp.items():
                response_breakdown[k][str(v)] += 1
    analytics = {
        "experiment_number": experiment_number,
        "total_participants": total,
        "unique_emails": len(emails),
        "responses_sample": responses[:5],
        "time_stats": time_stats,
        "response_breakdown": {k: dict(v) for k, v in response_breakdown.items()}
    }
    return {"success": True, "analytics": analytics}

# Export full CSV for a given experiment
@router.get("/export-csv/{experiment_number}")
async def export_experiment_csv(experiment_number: int, current_user: User = Depends(get_current_user)):
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    # Find the CSV file
    csv_path = CSV_PATH
    # Use pandas if available for filtering
    try:
        df = pd.read_csv(csv_path)
        df = df[df['experiment_number'] == experiment_number]
        stream = df.to_csv(index=False)
        return StreamingResponse(iter([stream]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_number}_participants.csv"})
    except Exception:
        # Fallback: manual filter
        import io
        output = io.StringIO()
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader if str(row.get('experiment_number')) == str(experiment_number)]
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_number}_participants.csv"})