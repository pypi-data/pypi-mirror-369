"""
Tool Call Statistics Tracking for C4 Memory Tools
Simple implementation tracking tool usage counts and timestamps
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json

@dataclass
class ToolCallRecord:
    """Single tool call record"""
    tool_name: str
    timestamp: float
    success: bool
    execution_time: Optional[float] = None
    error_message: Optional[str] = None

class ToolCallStats:
    """
    Simple tool call statistics tracker for C4 memory tools.
    Tracks usage counts, timestamps, and basic performance metrics.
    """
    
    def __init__(self):
        """Initialize empty statistics tracking"""
        self.call_counts: Dict[str, int] = {}
        self.call_history: List[ToolCallRecord] = []
        self.success_counts: Dict[str, int] = {}
        self.failure_counts: Dict[str, int] = {}
        self.total_execution_time: Dict[str, float] = {}
        self.start_time = time.time()
        
    def record_call_start(self, tool_name: str) -> float:
        """
        Record the start of a tool call
        
        Args:
            tool_name (str): Name of the tool being called
            
        Returns:
            float: Start timestamp for execution time calculation
        """
        start_time = time.time()
        
        # Initialize counters if first time seeing this tool
        if tool_name not in self.call_counts:
            self.call_counts[tool_name] = 0
            self.success_counts[tool_name] = 0
            self.failure_counts[tool_name] = 0
            self.total_execution_time[tool_name] = 0.0
            
        # Increment call count
        self.call_counts[tool_name] += 1
        
        return start_time
        
    def record_call_end(self, tool_name: str, start_time: float, success: bool = True, error_message: str = None):
        """
        Record the end of a tool call and update statistics
        
        Args:
            tool_name (str): Name of the tool that was called
            start_time (float): Start timestamp from record_call_start
            success (bool): Whether the call was successful
            error_message (str): Error message if call failed
        """
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Update success/failure counts
        if success:
            self.success_counts[tool_name] += 1
        else:
            self.failure_counts[tool_name] += 1
            
        # Update total execution time
        self.total_execution_time[tool_name] += execution_time
        
        # Add to call history
        record = ToolCallRecord(
            tool_name=tool_name,
            timestamp=end_time,
            success=success,
            execution_time=execution_time,
            error_message=error_message
        )
        self.call_history.append(record)
        
    def get_tool_count(self, tool_name: str) -> int:
        """Get total call count for a specific tool"""
        return self.call_counts.get(tool_name, 0)
        
    def get_total_calls(self) -> int:
        """Get total number of tool calls across all tools"""
        return sum(self.call_counts.values())
        
    def get_success_rate(self, tool_name: str) -> float:
        """
        Get success rate for a specific tool
        
        Returns:
            float: Success rate between 0.0 and 1.0, or 0.0 if no calls
        """
        total_calls = self.call_counts.get(tool_name, 0)
        if total_calls == 0:
            return 0.0
        return self.success_counts.get(tool_name, 0) / total_calls
        
    def get_average_execution_time(self, tool_name: str) -> float:
        """
        Get average execution time for a specific tool
        
        Returns:
            float: Average execution time in seconds, or 0.0 if no calls
        """
        total_calls = self.call_counts.get(tool_name, 0)
        if total_calls == 0:
            return 0.0
        return self.total_execution_time.get(tool_name, 0.0) / total_calls
        
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive usage summary
        
        Returns:
            Dict containing overall statistics
        """
        total_calls = self.get_total_calls()
        session_duration = time.time() - self.start_time
        
        tool_summaries = {}
        for tool_name in self.call_counts:
            tool_summaries[tool_name] = {
                "total_calls": self.call_counts[tool_name],
                "successful_calls": self.success_counts[tool_name],
                "failed_calls": self.failure_counts[tool_name],
                "success_rate": self.get_success_rate(tool_name),
                "average_execution_time": self.get_average_execution_time(tool_name),
                "total_execution_time": self.total_execution_time[tool_name]
            }
            
        return {
            "session_start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "session_duration_seconds": session_duration,
            "total_tool_calls": total_calls,
            "unique_tools_used": len(self.call_counts),
            "tool_summaries": tool_summaries,
            "recent_calls": len(self.call_history)
        }
        
    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent tool calls
        
        Args:
            limit (int): Maximum number of recent calls to return
            
        Returns:
            List of recent call records
        """
        recent = self.call_history[-limit:] if len(self.call_history) > limit else self.call_history
        
        return [
            {
                "tool_name": record.tool_name,
                "timestamp": datetime.fromtimestamp(record.timestamp).isoformat(),
                "success": record.success,
                "execution_time": record.execution_time,
                "error_message": record.error_message
            }
            for record in recent
        ]
        
    def export_stats_to_json(self) -> str:
        """
        Export all statistics to JSON format
        
        Returns:
            str: JSON string containing all statistics
        """
        export_data = {
            "summary": self.get_usage_summary(),
            "recent_calls": self.get_recent_calls(50),  # Export last 50 calls
            "export_timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(export_data, indent=2)
        
    def reset_stats(self):
        """Reset all statistics - useful for testing or starting fresh"""
        self.call_counts.clear()
        self.call_history.clear()
        self.success_counts.clear()
        self.failure_counts.clear()
        self.total_execution_time.clear()
        self.start_time = time.time()
        
    def __str__(self) -> str:
        """String representation showing basic stats"""
        total_calls = self.get_total_calls()
        unique_tools = len(self.call_counts)
        
        return f"ToolCallStats(total_calls={total_calls}, unique_tools={unique_tools}, session_duration={time.time() - self.start_time:.1f}s)"