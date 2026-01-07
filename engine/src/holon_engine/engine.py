"""Workflow execution engine - interprets and executes HolonDSL workflows."""

import re
import httpx
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import yaml

from .models import (
    HolonConfig,
    RunStatus,
    TraceEventStatus,
    WorkflowType,
    Run,
    TraceEvent,
    TraceEventMetrics,
)
from .persistence import PersistenceService


class WorkflowEngine:
    """
    The core execution engine that interprets HolonDSL configurations.
    """

    def __init__(self, persistence: PersistenceService):
        self.store = persistence

    def parse_config(self, config_yaml: str) -> HolonConfig:
        config_dict = yaml.safe_load(config_yaml)
        return HolonConfig(**config_dict)

    def _call_ollama_agent(self, base_url: str, model: str, instruction: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API to get agent response."""
        try:
            # Prepare the request payload
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": instruction})
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            # Make the API call
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract the assistant's response
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"]
                else:
                    return f"[Error: Unexpected Ollama response format: {result}]"
                    
        except httpx.ConnectError:
            return f"[Error: Could not connect to Ollama at {base_url}. Make sure Ollama is running.]"
        except httpx.TimeoutException:
            return "[Error: Ollama request timed out]"
        except Exception as e:
            return f"[Error calling Ollama: {str(e)}]"

    def execute_run(self, run_id: UUID, config_yaml: str) -> None:
        run = self.store.get_run(run_id)
        if not run:
            return

        try:
            config = self.parse_config(config_yaml)

            # Start Run
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            self.store.save_run(run)

            # Init Context
            context = {"trigger": {"input": run.input_context or {}}, "steps": {}}

            # Execute
            if config.workflow.type == WorkflowType.SEQUENTIAL:
                self._execute_sequential(run.id, config, context)
            else:
                raise NotImplementedError(
                    f"Workflow type {config.workflow.type} not yet implemented"
                )

            # Reload run to get latest state (trace events added during execution)
            run = self.store.get_run(run_id)

            # Complete Run
            run.status = RunStatus.COMPLETED
            run.ended_at = datetime.utcnow()
            run.context = context
            self.store.save_run(run)

        except Exception as e:
            # Refresh run in case of partial updates
            run = self.store.get_run(run_id) or run
            run.status = RunStatus.FAILED
            run.ended_at = datetime.utcnow()
            # If context exists, save it for debugging
            if "context" in locals():
                run.context = context

            error_event = TraceEvent(
                step_id="system_error",
                status=TraceEventStatus.FAILED,
                output={"error": str(e)},
                timestamp=datetime.utcnow(),
            )
            run.trace_events.append(error_event)
            self.store.save_run(run)
            # We don't re-raise here because this is the top level background task

    def _execute_sequential(
        self, run_id: UUID, config: HolonConfig, context: Dict[str, Any]
    ) -> None:
        """Execute a sequential workflow."""
        for step in config.workflow.steps:
            start_time = datetime.utcnow()
            run = self.store.get_run(run_id)

            try:
                instruction = self._resolve_template(step.instruction or "", context)

                step_input = {
                    "agent": step.agent,
                    "instruction": instruction,
                    "inputs": step.inputs,
                }

                # Find the agent configuration
                agent = None
                for resource in config.resources:
                    if resource.id == step.agent:
                        agent = resource
                        break
                
                # Execute the agent
                if agent and agent.provider == "ollama":
                    # Call Ollama
                    base_url = getattr(agent, "base_url", "http://localhost:11434")
                    model = agent.model or "llama3"
                    system_prompt = getattr(agent, "system_prompt", None)
                    
                    result = self._call_ollama_agent(base_url, model, instruction, system_prompt)
                    step_output = {
                        "result": result,
                        "instruction": instruction,
                    }
                else:
                    # SIMULATION for other providers
                    step_output = {
                        "result": f"[SIMULATED] Executed step {step.id}",
                        "instruction": instruction,
                    }

                context["steps"][step.id] = step_output

                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)

                trace_event = TraceEvent(
                    step_id=step.id,
                    status=TraceEventStatus.COMPLETED,
                    input=step_input,
                    output=step_output,
                    metrics=TraceEventMetrics(latency_ms=latency_ms, cost_usd=0.0),
                    timestamp=end_time,
                )

                run.trace_events.append(trace_event)
                # Ideally, we also save partial context here
                run.context = context
                self.store.save_run(run)

            except Exception as e:
                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)

                trace_event = TraceEvent(
                    step_id=step.id,
                    status=TraceEventStatus.FAILED,
                    input={"instruction": step.instruction},
                    output={"error": str(e)},
                    metrics=TraceEventMetrics(latency_ms=latency_ms),
                    timestamp=end_time,
                )
                run.trace_events.append(trace_event)
                self.store.save_run(run)
                raise

    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        def replace_var(match):
            var_path = match.group(1)
            parts = var_path.split(".")
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)
            return str(value)

        return re.sub(r"\{([^}]+)\}", replace_var, template)
