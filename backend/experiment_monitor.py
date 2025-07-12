#!/usr/bin/env python3
"""
Real-time Experiment Monitor Dashboard
Provides live monitoring of experiment progress, participant status, and system health
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentMonitor:
    """Real-time experiment monitoring and dashboard"""

    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.progress_file = self.data_path / "experiment_progress.json"
        self.recovery_file = self.data_path / "experiment_recovery.json"
        self.log_file = self.data_path / "experiment_runner.log"
        self.last_check = datetime.now()
        self.monitoring_active = True

    def get_experiment_progress(self) -> Dict[str, Any]:
        """Get current experiment progress"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)

                # Calculate additional metrics
                total_participants = progress.get("total_participants", 0)
                completed = progress.get("completed_participants", 0)
                failed = progress.get("failed_participants", 0)

                if total_participants > 0:
                    completion_rate = (completed / total_participants) * 100
                    success_rate = (completed / (completed + failed)) * 100 if (completed + failed) > 0 else 0
                else:
                    completion_rate = 0
                    success_rate = 0

                return {
                    "status": "running" if self.monitoring_active else "stopped",
                    "total_participants": total_participants,
                    "completed_participants": completed,
                    "failed_participants": failed,
                    "completion_rate": f"{completion_rate:.1f}%",
                    "success_rate": f"{success_rate:.1f}%",
                    "current_participant": progress.get("current_participant", "None"),
                    "start_time": progress.get("start_time"),
                    "last_save_time": progress.get("last_save_time"),
                    "errors": progress.get("errors", []),
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error reading progress: {e}")
            return {"status": "error", "error": str(e)}

        return {"status": "no_progress_file"}

    def get_system_health(self) -> Dict[str, Any]:
        """Check system health (backend, frontend, API)"""
        health_status = {
            "backend": {"status": "unknown", "response_time": 0},
            "frontend": {"status": "unknown", "response_time": 0},
            "api_keys": {"status": "unknown"},
            "last_check": datetime.now().isoformat()
        }

        # Check backend
        try:
            start_time = time.time()
            response = httpx.get("http://localhost:8000/health", timeout=5)
            response_time = (time.time() - start_time) * 1000

            health_status["backend"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": f"{response_time:.1f}ms",
                "status_code": response.status_code
            }
        except Exception as e:
            health_status["backend"] = {
                "status": "error",
                "error": str(e),
                "response_time": "N/A"
            }

        # Check frontend
        try:
            start_time = time.time()
            response = httpx.get("http://localhost:3000", timeout=5)
            response_time = (time.time() - start_time) * 1000

            health_status["frontend"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": f"{response_time:.1f}ms",
                "status_code": response.status_code
            }
        except Exception as e:
            health_status["frontend"] = {
                "status": "error",
                "error": str(e),
                "response_time": "N/A"
            }

        # Check API keys
        api_keys = {
            "GAMINI_API_KEY": bool(os.getenv("GAMINI_API_KEY")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
        }

        health_status["api_keys"] = {
            "status": "configured" if any(api_keys.values()) else "missing",
            "details": api_keys
        }

        return health_status

    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Get recent log entries"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
        return []

    def get_experiment_files(self) -> Dict[str, Any]:
        """Get list of experiment data files"""
        try:
            files = {}
            for file_path in self.data_path.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files[file_path.name] = {
                        "size": f"{stat.st_size / 1024:.1f} KB",
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "progress" if "progress" in file_path.name else
                               "recovery" if "recovery" in file_path.name else
                               "results" if "results" in file_path.name else
                               "logs" if "log" in file_path.name else "other"
                    }
            return files
        except Exception as e:
            logger.error(f"Error reading files: {e}")
            return {}

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "experiment_progress": self.get_experiment_progress(),
            "system_health": self.get_system_health(),
            "recent_logs": self.get_recent_logs(),
            "experiment_files": self.get_experiment_files(),
            "dashboard_updated": datetime.now().isoformat()
        }

    def print_dashboard(self):
        """Print a formatted dashboard to console"""
        data = self.get_dashboard_data()

        print("\n" + "="*80)
        print("🔬 AI-POWERED FOOD RECOMMENDER EXPERIMENT MONITOR")
        print("="*80)

        # Experiment Progress
        progress = data["experiment_progress"]
        print(f"\n📊 EXPERIMENT PROGRESS:")
        print(f"   Status: {progress.get('status', 'Unknown')}")
        print(f"   Completion: {progress.get('completion_rate', '0%')} ({progress.get('completed_participants', 0)}/{progress.get('total_participants', 0)})")
        print(f"   Success Rate: {progress.get('success_rate', '0%')}")
        print(f"   Failed: {progress.get('failed_participants', 0)}")
        print(f"   Current Participant: {progress.get('current_participant', 'None')}")

        # System Health
        health = data["system_health"]
        print(f"\n🏥 SYSTEM HEALTH:")
        print(f"   Backend: {health['backend']['status']} ({health['backend']['response_time']})")
        print(f"   Frontend: {health['frontend']['status']} ({health['frontend']['response_time']})")
        print(f"   API Keys: {health['api_keys']['status']}")

        # Recent Activity
        logs = data["recent_logs"]
        if logs:
            print(f"\n📝 RECENT ACTIVITY (last {len(logs)} entries):")
            for log in logs[-5:]:  # Show last 5 logs
                print(f"   {log.strip()}")

        # Files
        files = data["experiment_files"]
        if files:
            print(f"\n📁 EXPERIMENT FILES:")
            for filename, file_info in files.items():
                print(f"   {filename}: {file_info['size']} ({file_info['type']})")

        print(f"\n⏰ Last Updated: {data['dashboard_updated']}")
        print("="*80)

async def monitor_experiment(interval: int = 30):
    """Continuously monitor experiment progress"""
    monitor = ExperimentMonitor()

    print("🔍 Starting experiment monitoring...")
    print("Press Ctrl+C to stop monitoring")

    try:
        while True:
            monitor.print_dashboard()
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

def get_single_report():
    """Get a single dashboard report"""
    monitor = ExperimentMonitor()
    monitor.print_dashboard()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Continuous monitoring
        asyncio.run(monitor_experiment())
    else:
        # Single report
        get_single_report()