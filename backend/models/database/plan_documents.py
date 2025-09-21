"""
Database models for MongoDB document structure
These models handle the database-specific concerns and mapping
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

class PlanDocument:
    """MongoDB document structure for Plan"""
    
    @staticmethod
    def to_document(plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert domain model to MongoDB document"""
        doc = plan_data.copy()
        
        # Remove id field if present - MongoDB will generate _id
        doc.pop('id', None)
        
        # Ensure datetime fields are properly handled
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in doc and isinstance(doc['updated_at'], str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'].replace('Z', '+00:00'))
        
        # Ensure all tasks have proper IDs
        if 'days' in doc:
            for day in doc['days']:
                if 'tasks' in day:
                    for task in day['tasks']:
                        if 'id' not in task or task['id'] is None:
                            task['id'] = str(ObjectId())
                        if 'created_at' in task and isinstance(task['created_at'], str):
                            task['created_at'] = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
        
        return doc
    
    @staticmethod
    def from_document(doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to domain model format"""
        if not doc:
            return {}
        
        result = doc.copy()
        
        # Convert _id to id
        if '_id' in result:
            result['id'] = str(result.pop('_id'))
        elif 'id' not in result or result.get('id') is None:
            result['id'] = str(ObjectId())
        
        # Ensure all nested objects have proper IDs
        if 'days' in result:
            for day in result['days']:
                if 'tasks' in day:
                    for task in day['tasks']:
                        if 'id' not in task or task['id'] is None:
                            task['id'] = str(ObjectId())
                        # Remove problematic fields that might cause Pydantic issues
                        task.pop('external_info', None)
                        
                        # Ensure required fields
                        if 'description' not in task or not task['description']:
                            task['description'] = task.get('title', 'No description')
                        if 'status' not in task:
                            task['status'] = 'pending'
        
        return result

class TaskDocument:
    """MongoDB document structure for Task"""
    
    @staticmethod
    def to_document(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert task domain model to MongoDB document"""
        doc = task_data.copy()
        
        # Ensure task has an ID
        if 'id' not in doc or doc['id'] is None:
            doc['id'] = str(ObjectId())
            
        return doc
    
    @staticmethod
    def from_document(doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to task domain model format"""
        if not doc:
            return {}
            
        result = doc.copy()
        
        # Ensure task has an ID
        if 'id' not in result or result['id'] is None:
            result['id'] = str(ObjectId())
            
        return result