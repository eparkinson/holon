"""
HTTP API server for Holon agents and networks.

This module provides a FastAPI-based server for running agents and networks
as production services with REST endpoints, webhooks, and health checks.
"""

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .models import AgentDefinition, NetworkDefinition
from .network_runtime import NetworkRuntime
from .parser import Parser
from .runtime import Runtime


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message to send to the agent")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for maintaining context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent's response")
    agent_id: str = Field(..., description="ID of the responding agent")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NetworkRequest(BaseModel):
    """Request model for network execution."""
    input: str = Field(..., description="Input to the network")
    execution_id: Optional[str] = Field(
        None, description="Optional execution ID for tracking"
    )


class NetworkResponse(BaseModel):
    """Response model for network execution."""
    output: str = Field(..., description="Network output")
    network_id: str = Field(..., description="ID of the network")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    agent_outputs: Dict[str, str] = Field(..., description="Individual agent outputs")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    agents: List[str] = Field(..., description="List of loaded agent IDs")
    networks: List[str] = Field(..., description="List of loaded network IDs")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HolonServer:
    """Holon API server for agents and networks."""

    def __init__(self, definitions_path: Optional[Path] = None):
        """
        Initialize the Holon server.

        Args:
            definitions_path: Path to directory containing agent/network definitions
        """
        self.app = FastAPI(
            title="Holon Agent Server",
            description="REST API for Holon agents and networks",
            version="0.1.0"
        )
        self.definitions_path = definitions_path or Path.cwd()
        self.agents: Dict[str, AgentDefinition] = {}
        self.networks: Dict[str, NetworkDefinition] = {}
        self.agent_runtimes: Dict[str, Runtime] = {}
        self.network_runtimes: Dict[str, NetworkRuntime] = {}
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

        # Load definitions
        self._load_definitions()

        # Setup routes
        self._setup_routes()

    def _load_definitions(self):
        """Load all agent and network definitions from the definitions path."""
        if not self.definitions_path.exists():
            return

        for md_file in self.definitions_path.rglob("*.md"):
            try:
                definition = Parser.parse_file(md_file)
                
                if isinstance(definition, NetworkDefinition):
                    self.networks[definition.config.id] = definition
                    # Initialize network runtime with base path
                    self.network_runtimes[definition.config.id] = NetworkRuntime(
                        definition, base_path=md_file.parent
                    )
                else:
                    self.agents[definition.config.id] = definition
                    self.agent_runtimes[definition.config.id] = Runtime(definition)
            except Exception as e:
                print(f"Warning: Failed to load {md_file}: {e}")

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                agents=list(self.agents.keys()),
                networks=list(self.networks.keys())
            )

        @self.app.get("/agents")
        async def list_agents():
            """List all available agents."""
            return {
                "agents": [
                    {
                        "id": agent_id,
                        "model": agent.config.model,
                        "tools": agent.config.tools or []
                    }
                    for agent_id, agent in self.agents.items()
                ]
            }

        @self.app.get("/networks")
        async def list_networks():
            """List all available networks."""
            return {
                "networks": [
                    {
                        "id": network_id,
                        "execution_mode": network.config.execution_mode.value,
                        "agents": network.config.agents
                    }
                    for network_id, network in self.networks.items()
                ]
            }

        @self.app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
        async def chat_with_agent(agent_id: str, request: ChatRequest):
            """
            Send a message to an agent.
            
            Args:
                agent_id: ID of the agent to chat with
                request: Chat request with message
                
            Returns:
                Agent's response
            """
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

            runtime = self.agent_runtimes[agent_id]
            
            # Get or create conversation
            conv_id = request.conversation_id or f"{agent_id}_{datetime.now(timezone.utc).isoformat()}"
            
            if conv_id not in self.conversations:
                self.conversations[conv_id] = [
                    {"role": "system", "content": runtime.agent.prompt}
                ]
            
            # Add user message
            self.conversations[conv_id].append({"role": "user", "content": request.message})
            
            # Update runtime conversation history
            runtime.conversation_history = self.conversations[conv_id].copy()
            
            # Get response
            try:
                response_text = runtime._get_llm_response()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error getting response from agent: {str(e)}"
                )
            
            # Add assistant response to conversation
            self.conversations[conv_id].append({"role": "assistant", "content": response_text})
            
            return ChatResponse(
                response=response_text,
                agent_id=agent_id,
                conversation_id=conv_id
            )

        @self.app.post("/networks/{network_id}/execute", response_model=NetworkResponse)
        async def execute_network(network_id: str, request: NetworkRequest):
            """
            Execute a network with the given input.
            
            Args:
                network_id: ID of the network to execute
                request: Network execution request
                
            Returns:
                Network execution results
            """
            if network_id not in self.networks:
                raise HTTPException(status_code=404, detail=f"Network '{network_id}' not found")

            network_runtime = self.network_runtimes[network_id]
            
            # Execute the network
            try:
                result = network_runtime.execute(request.input)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing network: {str(e)}"
                )
            
            exec_id = request.execution_id or f"{network_id}_{datetime.now(timezone.utc).isoformat()}"
            
            return NetworkResponse(
                output=result["final_output"],
                network_id=network_id,
                execution_id=exec_id,
                agent_outputs=result["outputs"]
            )

        @self.app.post("/webhook/{agent_id}")
        async def webhook_trigger(agent_id: str, request: Request, background_tasks: BackgroundTasks):
            """
            Webhook endpoint for triggering agent execution.
            
            Args:
                agent_id: ID of the agent to trigger
                request: Incoming webhook request
                
            Returns:
                Acknowledgment response
            """
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

            # Get webhook payload
            try:
                payload = await request.json()
            except Exception:
                payload = {"message": "Webhook triggered"}
            
            # Process in background - wrap sync LLM call in async
            async def process_webhook():
                runtime = self.agent_runtimes[agent_id]
                message = payload.get("message", "Webhook triggered")
                
                # Create new conversation for webhook
                runtime.conversation_history = [
                    {"role": "system", "content": runtime.agent.prompt},
                    {"role": "user", "content": message}
                ]
                
                try:
                    # Run the synchronous LLM call in a thread pool to avoid blocking
                    response = await asyncio.to_thread(runtime._get_llm_response)
                    # Here you could store the response, send it somewhere, etc.
                    print(f"Webhook response from {agent_id}: {response}")
                except Exception as e:
                    print(f"Error processing webhook for {agent_id}: {e}")
            
            background_tasks.add_task(process_webhook)
            
            return JSONResponse(
                status_code=202,
                content={
                    "status": "accepted",
                    "agent_id": agent_id,
                    "message": "Webhook processing started"
                }
            )

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


def create_server(definitions_path: Optional[str] = None) -> HolonServer:
    """
    Create a Holon server instance.
    
    Args:
        definitions_path: Path to directory containing agent/network definitions
        
    Returns:
        HolonServer instance
    """
    path = Path(definitions_path) if definitions_path else None
    return HolonServer(definitions_path=path)
