"""Workflow execution engine - interprets and executes HolonDSL workflows."""

import re
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import yaml

from .models import HolonConfig, RunStatus, TraceEventStatus, WorkflowType
from .database import Run, TraceEvent


class WorkflowEngine:
    """
    The core execution engine that interprets HolonDSL configurations.
    
    For the MVP/prototype, this is a simple sequential executor that:
    1. Parses the workflow
    2. Executes steps in order
    3. Maintains a context/blackboard for data passing
    4. Logs trace events
    """
    
    def __init__(self, db_session):
        """Initialize the workflow engine with a database session."""
        self.db_session = db_session
        
    def parse_config(self, config_yaml: str) -> HolonConfig:
        """Parse and validate a holon.yaml configuration."""
        config_dict = yaml.safe_load(config_yaml)
        return HolonConfig(**config_dict)
    
    def execute_run(self, run: Run, config_yaml: str) -> None:
        """
        Execute a workflow run.
        
        This is a simplified prototype implementation that:
        - Parses the configuration
        - Sets up the execution context
        - Executes steps (currently just logs them as we don't have real agents yet)
        - Updates run status
        
        Args:
            run: The Run database object to execute
            config_yaml: The YAML configuration to execute
        """
        # Initialize context early so it's always available
        context = {}
        
        try:
            # Parse the configuration
            config = self.parse_config(config_yaml)
            
            # Update run status to RUNNING
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            self.db_session.commit()
            
            # Initialize execution context (the "blackboard")
            context = {
                "trigger": {
                    "input": run.input_context or {}
                },
                "steps": {}
            }
            
            # Execute the workflow
            if config.workflow.type == WorkflowType.SEQUENTIAL:
                self._execute_sequential(run, config, context)
            else:
                # For now, only sequential is implemented
                raise NotImplementedError(f"Workflow type {config.workflow.type} not yet implemented")
            
            # Update run status to COMPLETED
            run.status = RunStatus.COMPLETED
            run.ended_at = datetime.utcnow()
            run.context = context
            self.db_session.commit()
            
        except Exception as e:
            # Update run status to FAILED
            run.status = RunStatus.FAILED
            run.ended_at = datetime.utcnow()
            run.context = context if context else {"error": str(e)}
            self.db_session.commit()
            raise
    
    def _execute_sequential(self, run: Run, config: HolonConfig, context: Dict[str, Any]) -> None:
        """Execute a sequential workflow."""
        for step in config.workflow.steps:
            start_time = datetime.utcnow()
            
            try:
                # Resolve instruction template with context variables
                instruction = self._resolve_template(step.instruction or "", context)
                
                # For the prototype, we'll simulate execution
                # In a real implementation, this would call the actual agent
                step_input = {
                    "agent": step.agent,
                    "instruction": instruction,
                    "inputs": step.inputs
                }
                
                # Simulate a successful execution
                # In reality, this would call the agent provider's API
                step_output = {
                    "result": f"[SIMULATED] Executed step {step.id}",
                    "instruction": instruction
                }
                
                # Store step result in context
                context["steps"][step.id] = step_output
                
                # Log trace event
                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                trace_event = TraceEvent(
                    run_id=run.id,
                    step_id=step.id,
                    status=TraceEventStatus.COMPLETED.value,
                    input=step_input,
                    output=step_output,
                    metrics={"latency_ms": latency_ms, "cost_usd": 0.0},
                    timestamp=end_time
                )
                self.db_session.add(trace_event)
                self.db_session.commit()
                
            except Exception as e:
                # Log failed trace event
                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                trace_event = TraceEvent(
                    run_id=run.id,
                    step_id=step.id,
                    status=TraceEventStatus.FAILED.value,
                    input={"error": str(e)},
                    output=None,
                    metrics={"latency_ms": latency_ms},
                    timestamp=end_time
                )
                self.db_session.add(trace_event)
                self.db_session.commit()
                raise
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Resolve template variables like ${trigger.input} with actual values.
        
        This is a simple implementation that handles basic dot notation.
        A production version would be more robust.
        """
        def replace_var(match):
            var_path = match.group(1)
            parts = var_path.split(".")
            
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Return original if not found
            
            return str(value)
        
        # Replace ${variable.path} patterns
        return re.sub(r'\$\{([^}]+)\}', replace_var, template)
