# Basic Gemini Chat

## Overview
This is the simplest possible Holon configuration - a single Gemini agent accessible via a web chat interface.

## Purpose
- **Syntax Exploration**: Demonstrates minimal configuration requirements
- **Testing**: Can be used to validate basic chat functionality
- **Documentation**: Entry-level example for new users

## Configuration Highlights

### Trigger
- **Type**: `websocket` - Real-time bidirectional communication
- **Mode**: `interactive` - Direct chat without predefined workflows
- **CORS**: Allows connections from local dev and production web dashboard

### Resources
- **Single Agent**: Google Gemini 1.5 Pro
- **System Prompt**: Basic helpful assistant persona

### Workflow
- **Type**: `sequential` - Simplest workflow type
- **Single Step**: Direct response to user message

## Usage
When the Holon engine is running with this configuration, users can:
1. Open the web dashboard chat interface
2. Type messages directly
3. Receive responses from Gemini in real-time

## Notes
This configuration is intentionally minimal to demonstrate the core components:
- Every holon.yaml needs: `version`, `project`, `trigger`, `resources`, `workflow`
- The simplest workflow has one agent and one step
- Websocket triggers enable real-time chat interfaces
