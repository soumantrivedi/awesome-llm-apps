"""
Async Operation Tracker for Agentic PM
Tracks async operations and their status
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class OperationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AsyncOperationTracker:
    """Tracks async operations for the Agentic PM system"""
    
    def __init__(self, storage_file: str = "async_operations.json"):
        self.storage_file = storage_file
        self.operations: Dict[str, Dict] = {}
        self.load()
    
    def load(self):
        """Load operations from storage"""
        try:
            with open(self.storage_file, 'r') as f:
                self.operations = json.load(f)
        except FileNotFoundError:
            self.operations = {}
    
    def save(self):
        """Save operations to storage"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.operations, f, indent=2, default=str)
    
    def create_operation(self, operation_type: str, description: str, 
                        metadata: Optional[Dict] = None) -> str:
        """Create a new async operation"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.operations[operation_id] = {
            "id": operation_id,
            "type": operation_type,
            "description": description,
            "status": OperationStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "result": None,
            "error": None
        }
        
        self.save()
        return operation_id
    
    def update_operation(self, operation_id: str, status: Optional[OperationStatus] = None,
                       result: Optional[Dict] = None, error: Optional[str] = None,
                       metadata: Optional[Dict] = None):
        """Update an operation"""
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        operation = self.operations[operation_id]
        
        if status:
            operation["status"] = status.value
        if result is not None:
            operation["result"] = result
        if error:
            operation["error"] = error
        if metadata:
            operation["metadata"].update(metadata)
        
        operation["updated_at"] = datetime.now().isoformat()
        self.save()
    
    def get_operation(self, operation_id: str) -> Optional[Dict]:
        """Get an operation by ID"""
        return self.operations.get(operation_id)
    
    def get_operations_by_type(self, operation_type: str) -> List[Dict]:
        """Get all operations of a specific type"""
        return [op for op in self.operations.values() if op["type"] == operation_type]
    
    def get_pending_operations(self) -> List[Dict]:
        """Get all pending operations"""
        return [op for op in self.operations.values() 
                if op["status"] == OperationStatus.PENDING.value]
    
    def get_in_progress_operations(self) -> List[Dict]:
        """Get all in-progress operations"""
        return [op for op in self.operations.values() 
                if op["status"] == OperationStatus.IN_PROGRESS.value]
    
    def get_failed_operations(self) -> List[Dict]:
        """Get all failed operations"""
        return [op for op in self.operations.values() 
                if op["status"] == OperationStatus.FAILED.value]
    
    def mark_completed(self, operation_id: str, result: Optional[Dict] = None):
        """Mark an operation as completed"""
        self.update_operation(operation_id, status=OperationStatus.COMPLETED, result=result)
    
    def mark_failed(self, operation_id: str, error: str):
        """Mark an operation as failed"""
        self.update_operation(operation_id, status=OperationStatus.FAILED, error=error)
    
    def mark_in_progress(self, operation_id: str):
        """Mark an operation as in progress"""
        self.update_operation(operation_id, status=OperationStatus.IN_PROGRESS)
    
    def get_summary(self) -> Dict:
        """Get summary of all operations"""
        total = len(self.operations)
        pending = len(self.get_pending_operations())
        in_progress = len(self.get_in_progress_operations())
        completed = len([op for op in self.operations.values() 
                        if op["status"] == OperationStatus.COMPLETED.value])
        failed = len(self.get_failed_operations())
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed
        }

