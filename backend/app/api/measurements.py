from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import csv
import os
import random
from logging_config import logger

router = APIRouter(prefix="/api/measurements", tags=["measurements"])

# Pydantic Models for Measurements

class NASATLXRequest(BaseModel):
    """NASA Task Load Index measurement request"""
    mental_demand: int = Field(ge=0, le=100, description="Mental workload required")
    physical_demand: int = Field(ge=0, le=100, description="Physical activity required")
    temporal_demand: int = Field(ge=0, le=100, description="Time pressure felt")
    performance: int = Field(ge=0, le=100, description="How successful you think you were")
    effort: int = Field(ge=0, le=100, description="How hard you had to work")
    frustration: int = Field(ge=0, le=100, description="How insecure, discouraged, irritated, stressed you felt")
    session_id: str = Field(description="Unique session identifier")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class SUSRequest(BaseModel):
    """System Usability Scale measurement request"""
    q1_use_frequently: int = Field(ge=1, le=5, description="I think that I would like to use this system frequently")
    q2_unnecessarily_complex: int = Field(ge=1, le=5, description="I found the system unnecessarily complex")
    q3_easy_to_use: int = Field(ge=1, le=5, description="I thought the system was easy to use")
    q4_need_support: int = Field(ge=1, le=5, description="I think that I would need the support of a technical person")
    q5_well_integrated: int = Field(ge=1, le=5, description="I found the various functions in this system were well integrated")
    q6_too_much_inconsistency: int = Field(ge=1, le=5, description="I thought there was too much inconsistency in this system")
    q7_learn_quickly: int = Field(ge=1, le=5, description="I would imagine that most people would learn to use this system very quickly")
    q8_very_cumbersome: int = Field(ge=1, le=5, description="I found the system very cumbersome to use")
    q9_very_confident: int = Field(ge=1, le=5, description="I felt very confident using the system")
    q10_learn_lot_before: int = Field(ge=1, le=5, description="I needed to learn a lot of things before I could get going with this system")
    session_id: str = Field(description="Unique session identifier")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class TaskCompletionRequest(BaseModel):
    """Task completion measurement request"""
    session_id: str = Field(description="Unique session identifier")
    task_start_time: datetime = Field(description="When the task started")
    task_end_time: datetime = Field(description="When the task completed")
    task_type: str = Field(description="Type of task (e.g., 'order_food', 'browse_menu')")
    success: bool = Field(description="Whether the task was completed successfully")
    steps_completed: int = Field(ge=0, description="Number of steps completed")
    total_steps: int = Field(ge=1, description="Total number of steps in the task")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class ErrorTrackingRequest(BaseModel):
    """Error tracking measurement request"""
    session_id: str = Field(description="Unique session identifier")
    error_type: str = Field(description="Type of error (e.g., 'selection_error', 'navigation_error')")
    error_description: str = Field(description="Description of the error")
    timestamp: datetime = Field(description="When the error occurred")
    context: Dict[str, Any] = Field(default={}, description="Additional context about the error")
    recovered: bool = Field(default=False, description="Whether user recovered from the error")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class SatisfactionRequest(BaseModel):
    """Decision satisfaction measurement request"""
    session_id: str = Field(description="Unique session identifier")
    overall_satisfaction: int = Field(ge=1, le=7, description="Overall satisfaction with the experience")
    ease_of_use: int = Field(ge=1, le=7, description="How easy was it to use the system")
    recommendation_quality: int = Field(ge=1, le=7, description="Quality of recommendations received")
    perceived_personalization: int = Field(ge=1, le=7, description="How personalized the experience felt")
    decision_confidence: int = Field(ge=1, le=7, description="Confidence in your final decision")
    enjoyment: int = Field(ge=1, le=7, description="How enjoyable was the experience")
    return_intention: int = Field(ge=1, le=7, description="Likelihood of using the system again")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class DecisionChangeRequest(BaseModel):
    """Decision change tracking request"""
    session_id: str = Field(description="Unique session identifier")
    change_type: str = Field(description="Type of change (e.g., 'protein_change', 'sauce_change')")
    original_choice: str = Field(description="Original choice")
    new_choice: str = Field(description="New choice")
    timestamp: datetime = Field(description="When the change occurred")
    reason: Optional[str] = Field(default="", description="Reason for the change if provided")
    condition: Optional[str] = Field(default="standard", description="Experimental condition")

class MeasurementResponse(BaseModel):
    """Standard response for measurement submissions"""
    success: bool
    message: str
    session_id: str
    timestamp: datetime
    measurement_id: Optional[str] = None

class SessionSummaryResponse(BaseModel):
    """Summary of all measurements for a session"""
    session_id: str
    condition: str
    nasa_tlx: Optional[Dict[str, Any]] = None
    sus_score: Optional[float] = None
    task_completion: Optional[Dict[str, Any]] = None
    error_count: int = 0
    decision_changes: int = 0
    satisfaction: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Data storage functions
def ensure_data_directory():
    """Ensure the measurements data directory exists"""
    os.makedirs("data/measurements", exist_ok=True)

def save_measurement_to_csv(measurement_type: str, data: Dict[str, Any]):
    """Save measurement data to CSV file"""
    ensure_data_directory()
    filepath = f"data/measurements/{measurement_type}.csv"

    file_exists = os.path.exists(filepath)

    with open(filepath, 'a', newline='') as csvfile:
        if data:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

# NASA-TLX Endpoints
@router.post("/nasa-tlx", response_model=MeasurementResponse)
async def submit_nasa_tlx(request: NASATLXRequest):
    """Submit NASA Task Load Index measurements"""
    try:
        # Calculate overall workload score (average of all dimensions)
        overall_workload = (
            request.mental_demand + request.physical_demand + request.temporal_demand +
            request.performance + request.effort + request.frustration
        ) / 6

        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "mental_demand": request.mental_demand,
            "physical_demand": request.physical_demand,
            "temporal_demand": request.temporal_demand,
            "performance": request.performance,
            "effort": request.effort,
            "frustration": request.frustration,
            "overall_workload": round(overall_workload, 2),
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("nasa_tlx", measurement_data)

        logger.info(f"NASA-TLX measurement recorded for session {request.session_id}")

        return MeasurementResponse(
            success=True,
            message="NASA-TLX measurement recorded successfully",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"nasa_tlx_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording NASA-TLX measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.post("/sus", response_model=MeasurementResponse)
async def submit_sus(request: SUSRequest):
    """Submit System Usability Scale measurements"""
    try:
        # Calculate SUS score according to standard formula
        odd_items = [request.q1_use_frequently, request.q3_easy_to_use, request.q5_well_integrated,
                    request.q7_learn_quickly, request.q9_very_confident]
        even_items = [request.q2_unnecessarily_complex, request.q4_need_support, request.q6_too_much_inconsistency,
                     request.q8_very_cumbersome, request.q10_learn_lot_before]

        sus_score = (sum(score - 1 for score in odd_items) + sum(5 - score for score in even_items)) * 2.5

        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "q1_use_frequently": request.q1_use_frequently,
            "q2_unnecessarily_complex": request.q2_unnecessarily_complex,
            "q3_easy_to_use": request.q3_easy_to_use,
            "q4_need_support": request.q4_need_support,
            "q5_well_integrated": request.q5_well_integrated,
            "q6_too_much_inconsistency": request.q6_too_much_inconsistency,
            "q7_learn_quickly": request.q7_learn_quickly,
            "q8_very_cumbersome": request.q8_very_cumbersome,
            "q9_very_confident": request.q9_very_confident,
            "q10_learn_lot_before": request.q10_learn_lot_before,
            "sus_score": round(sus_score, 2),
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("sus", measurement_data)

        logger.info(f"SUS measurement recorded for session {request.session_id}, score: {sus_score}")

        return MeasurementResponse(
            success=True,
            message=f"SUS measurement recorded successfully (Score: {sus_score:.1f})",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"sus_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording SUS measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.post("/task-completion", response_model=MeasurementResponse)
async def submit_task_completion(request: TaskCompletionRequest):
    """Submit task completion measurements"""
    try:
        completion_time = (request.task_end_time - request.task_start_time).total_seconds()
        completion_rate = request.steps_completed / request.total_steps

        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "task_type": request.task_type,
            "task_start_time": request.task_start_time.isoformat(),
            "task_end_time": request.task_end_time.isoformat(),
            "completion_time_seconds": completion_time,
            "completion_time_minutes": round(completion_time / 60, 2),
            "success": request.success,
            "steps_completed": request.steps_completed,
            "total_steps": request.total_steps,
            "completion_rate": round(completion_rate, 3),
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("task_completion", measurement_data)

        logger.info(f"Task completion measurement recorded for session {request.session_id}")

        return MeasurementResponse(
            success=True,
            message="Task completion measurement recorded successfully",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"task_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording task completion measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.post("/error-tracking", response_model=MeasurementResponse)
async def submit_error_tracking(request: ErrorTrackingRequest):
    """Submit error tracking measurements"""
    try:
        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "error_type": request.error_type,
            "error_description": request.error_description,
            "error_timestamp": request.timestamp.isoformat(),
            "context": json.dumps(request.context),
            "recovered": request.recovered,
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("error_tracking", measurement_data)

        logger.info(f"Error tracking measurement recorded for session {request.session_id}")

        return MeasurementResponse(
            success=True,
            message="Error tracking measurement recorded successfully",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"error_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording error tracking measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.post("/satisfaction", response_model=MeasurementResponse)
async def submit_satisfaction(request: SatisfactionRequest):
    """Submit satisfaction measurements"""
    try:
        # Calculate average satisfaction score
        avg_satisfaction = (
            request.overall_satisfaction + request.ease_of_use + request.recommendation_quality +
            request.perceived_personalization + request.decision_confidence +
            request.enjoyment + request.return_intention
        ) / 7

        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "overall_satisfaction": request.overall_satisfaction,
            "ease_of_use": request.ease_of_use,
            "recommendation_quality": request.recommendation_quality,
            "perceived_personalization": request.perceived_personalization,
            "decision_confidence": request.decision_confidence,
            "enjoyment": request.enjoyment,
            "return_intention": request.return_intention,
            "average_satisfaction": round(avg_satisfaction, 2),
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("satisfaction", measurement_data)

        logger.info(f"Satisfaction measurement recorded for session {request.session_id}")

        return MeasurementResponse(
            success=True,
            message="Satisfaction measurement recorded successfully",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"satisfaction_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording satisfaction measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.post("/decision-change", response_model=MeasurementResponse)
async def submit_decision_change(request: DecisionChangeRequest):
    """Submit decision change tracking"""
    try:
        measurement_data = {
            "session_id": request.session_id,
            "condition": request.condition,
            "change_type": request.change_type,
            "original_choice": request.original_choice,
            "new_choice": request.new_choice,
            "change_timestamp": request.timestamp.isoformat(),
            "reason": request.reason,
            "timestamp": datetime.now().isoformat()
        }

        save_measurement_to_csv("decision_changes", measurement_data)

        logger.info(f"Decision change measurement recorded for session {request.session_id}")

        return MeasurementResponse(
            success=True,
            message="Decision change measurement recorded successfully",
            session_id=request.session_id,
            timestamp=datetime.now(),
            measurement_id=f"change_{request.session_id}_{int(datetime.now().timestamp())}"
        )

    except Exception as e:
        logger.error(f"Error recording decision change measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording measurement: {str(e)}")

@router.get("/session-summary/{session_id}", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    """Get summary of all measurements for a session"""
    try:
        ensure_data_directory()

        summary = SessionSummaryResponse(
            session_id=session_id,
            condition="standard",
            timestamp=datetime.now()
        )

        # Load NASA-TLX data
        nasa_tlx_file = "/app/data/measurements/nasa_tlx.csv"
        if os.path.exists(nasa_tlx_file):
            with open(nasa_tlx_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['session_id'] == session_id:
                        summary.nasa_tlx = {
                            "mental_demand": float(row['mental_demand']),
                            "physical_demand": float(row['physical_demand']),
                            "temporal_demand": float(row['temporal_demand']),
                            "performance": float(row['performance']),
                            "effort": float(row['effort']),
                            "frustration": float(row['frustration']),
                            "overall_workload": float(row['overall_workload'])
                        }
                        summary.condition = row.get('condition', 'standard')
                        break

        # Load SUS data
        sus_file = "/app/data/measurements/sus.csv"
        if os.path.exists(sus_file):
            with open(sus_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['session_id'] == session_id:
                        summary.sus_score = float(row['sus_score'])
                        break

        # Load task completion data
        task_file = "/app/data/measurements/task_completion.csv"
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['session_id'] == session_id:
                        summary.task_completion = {
                            "task_type": row['task_type'],
                            "completion_time_minutes": float(row['completion_time_minutes']),
                            "success": row['success'].lower() == 'true',
                            "completion_rate": float(row['completion_rate'])
                        }
                        break

        # Count errors
        error_file = "/app/data/measurements/error_tracking.csv"
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                reader = csv.DictReader(f)
                summary.error_count = sum(1 for row in reader if row['session_id'] == session_id)

        # Count decision changes
        changes_file = "/app/data/measurements/decision_changes.csv"
        if os.path.exists(changes_file):
            with open(changes_file, 'r') as f:
                reader = csv.DictReader(f)
                summary.decision_changes = sum(1 for row in reader if row['session_id'] == session_id)

        # Load satisfaction data
        satisfaction_file = "/app/data/measurements/satisfaction.csv"
        if os.path.exists(satisfaction_file):
            with open(satisfaction_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['session_id'] == session_id:
                        summary.satisfaction = {
                            "overall_satisfaction": float(row['overall_satisfaction']),
                            "ease_of_use": float(row['ease_of_use']),
                            "recommendation_quality": float(row['recommendation_quality']),
                            "perceived_personalization": float(row['perceived_personalization']),
                            "decision_confidence": float(row['decision_confidence']),
                            "enjoyment": float(row['enjoyment']),
                            "return_intention": float(row['return_intention']),
                            "average_satisfaction": float(row['average_satisfaction'])
                        }
                        break

        return summary

    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session summary: {str(e)}")

@router.get("/analytics/summary")
async def get_measurement_analytics():
    """Get analytics summary of all measurements"""
    try:
        ensure_data_directory()

        analytics = {
            "total_sessions": 0,
            "conditions": {},
            "nasa_tlx_averages": {},
            "sus_average": 0,
            "task_completion_stats": {},
            "error_stats": {},
            "satisfaction_averages": {},
            "timestamp": datetime.now().isoformat()
        }

        # Analyze NASA-TLX data
        nasa_tlx_file = "/app/data/measurements/nasa_tlx.csv"
        if os.path.exists(nasa_tlx_file):
            nasa_data = []
            conditions = set()
            with open(nasa_tlx_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nasa_data.append(row)
                    conditions.add(row.get('condition', 'standard'))

            analytics["total_sessions"] = len(nasa_data)
            analytics["conditions"] = {cond: sum(1 for row in nasa_data if row.get('condition') == cond) for cond in conditions}

            if nasa_data:
                analytics["nasa_tlx_averages"] = {
                    "mental_demand": sum(float(row['mental_demand']) for row in nasa_data) / len(nasa_data),
                    "physical_demand": sum(float(row['physical_demand']) for row in nasa_data) / len(nasa_data),
                    "temporal_demand": sum(float(row['temporal_demand']) for row in nasa_data) / len(nasa_data),
                    "performance": sum(float(row['performance']) for row in nasa_data) / len(nasa_data),
                    "effort": sum(float(row['effort']) for row in nasa_data) / len(nasa_data),
                    "frustration": sum(float(row['frustration']) for row in nasa_data) / len(nasa_data),
                    "overall_workload": sum(float(row['overall_workload']) for row in nasa_data) / len(nasa_data)
                }

        # Analyze SUS data
        sus_file = "/app/data/measurements/sus.csv"
        if os.path.exists(sus_file):
            with open(sus_file, 'r') as f:
                reader = csv.DictReader(f)
                sus_scores = [float(row['sus_score']) for row in reader]
                if sus_scores:
                    analytics["sus_average"] = sum(sus_scores) / len(sus_scores)

        # Analyze task completion data
        task_file = "/app/data/measurements/task_completion.csv"
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                reader = csv.DictReader(f)
                task_data = list(reader)
                if task_data:
                    success_rate = sum(1 for row in task_data if row['success'].lower() == 'true') / len(task_data)
                    avg_completion_time = sum(float(row['completion_time_minutes']) for row in task_data) / len(task_data)
                    analytics["task_completion_stats"] = {
                        "success_rate": success_rate,
                        "average_completion_time_minutes": avg_completion_time,
                        "total_tasks": len(task_data)
                    }

        # Analyze error data
        error_file = "/app/data/measurements/error_tracking.csv"
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                reader = csv.DictReader(f)
                error_data = list(reader)
                if error_data:
                    error_types = {}
                    recovery_rate = sum(1 for row in error_data if row['recovered'].lower() == 'true') / len(error_data)
                    for row in error_data:
                        error_type = row['error_type']
                        error_types[error_type] = error_types.get(error_type, 0) + 1

                    analytics["error_stats"] = {
                        "total_errors": len(error_data),
                        "recovery_rate": recovery_rate,
                        "error_types": error_types
                    }

        # Analyze satisfaction data
        satisfaction_file = "/app/data/measurements/satisfaction.csv"
        if os.path.exists(satisfaction_file):
            with open(satisfaction_file, 'r') as f:
                reader = csv.DictReader(f)
                satisfaction_data = list(reader)
                if satisfaction_data:
                    analytics["satisfaction_averages"] = {
                        "overall_satisfaction": sum(float(row['overall_satisfaction']) for row in satisfaction_data) / len(satisfaction_data),
                        "ease_of_use": sum(float(row['ease_of_use']) for row in satisfaction_data) / len(satisfaction_data),
                        "recommendation_quality": sum(float(row['recommendation_quality']) for row in satisfaction_data) / len(satisfaction_data),
                        "perceived_personalization": sum(float(row['perceived_personalization']) for row in satisfaction_data) / len(satisfaction_data),
                        "decision_confidence": sum(float(row['decision_confidence']) for row in satisfaction_data) / len(satisfaction_data),
                        "enjoyment": sum(float(row['enjoyment']) for row in satisfaction_data) / len(satisfaction_data),
                        "return_intention": sum(float(row['return_intention']) for row in satisfaction_data) / len(satisfaction_data),
                        "average_satisfaction": sum(float(row['average_satisfaction']) for row in satisfaction_data) / len(satisfaction_data)
                    }

        return analytics

    except Exception as e:
        logger.error(f"Error getting measurement analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session_data(session_id: str):
    """Delete all measurement data for a specific session"""
    try:
        ensure_data_directory()
        deleted_count = 0

        measurement_files = [
            "nasa_tlx.csv", "sus.csv", "task_completion.csv",
            "error_tracking.csv", "satisfaction.csv", "decision_changes.csv"
        ]

        for filename in measurement_files:
            filepath = f"/app/data/measurements/{filename}"
            if os.path.exists(filepath):
                # Read all data
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = [row for row in reader if row['session_id'] != session_id]

                # Write back without the session data
                if rows:
                    with open(filepath, 'w', newline='') as f:
                        if rows:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
                            deleted_count += 1

        logger.info(f"Deleted measurement data for session {session_id}")

        return {
            "success": True,
            "message": f"Deleted measurement data for session {session_id}",
            "files_processed": deleted_count
        }

    except Exception as e:
        logger.error(f"Error deleting session data: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session data: {str(e)}")

@router.get("/health")
async def measurement_health_check():
    """Health check for measurement system"""
    try:
        ensure_data_directory()

        measurement_files = [
            "nasa_tlx.csv", "sus.csv", "task_completion.csv",
            "error_tracking.csv", "satisfaction.csv", "decision_changes.csv"
        ]

        file_status = {}
        for filename in measurement_files:
            filepath = f"/app/data/measurements/{filename}"
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    row_count = sum(1 for row in reader)
                file_status[filename] = {"exists": True, "rows": row_count}
            else:
                file_status[filename] = {"exists": False, "rows": 0}

        return {
            "status": "healthy",
            "measurement_system": "operational",
            "data_directory": "/app/data/measurements",
            "files": file_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in measurement health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }