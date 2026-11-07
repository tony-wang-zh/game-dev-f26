# Implementation Agent Instructions & Project Boundaries

## 1. Role & Objectives
You are the primary implementation agent for this project. 
Your responsibility is to write modular, well-tested Python code adhering strictly to our game design specification.

## 2. Directory & Scope Permissions
- **Allowed Modifications:** You may only update files under `midterms/tony-wang-zh`
- **Restricted Files:** Do NOT modify `AGENT-TEAM.md`,  `EVALUATION.md`. These files are human-authored.
- Also do not modify `coursework_instructions.md` and `my_instructions.md`. these provide overall project guidelines
- **Dependency Boundary:** Keep all configuration files and dependencies scoped strictly inside `midterms/tony-wang-zh` .


## 4. API & Vertex AI Integration Guidelines
When writing code that connects to Google Cloud Vertex AI:
- Use the official `google-genai` Python library.
- Instantiate clients using:
  ```python
  from google import genai
  client = genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location="us-central1")

## implementation details 
- see EXECUTION_PLAN for plan and human-added instructions regarding execution
