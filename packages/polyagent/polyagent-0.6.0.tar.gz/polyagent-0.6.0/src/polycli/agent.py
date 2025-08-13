#!/usr/bin/env python3
"""
A reusable Python module for a stateful AI agent that interacts with the Claude CLI
or other LLMs via configurable endpoints.

This version includes:
- Model configuration via models.json file
- Fake user messages that append to existing ones
- Routing to different models via unified API
- System prompt support (default and per-run)
- Auto-skip permissions for Claude Code
- Ephemeral messages for LLM runs (not added to messages)
"""

import json
import subprocess
import os
import sys
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Type, Callable
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from .utils.serializers import default_json_serializer, json_list_serializer
from .utils.llm_client import get_llm_client
import copy
from .messages import add_user_message_opensouce, add_user_message_claude, extract_message_content

# Load environment variables from .env file
load_dotenv()

from abc import ABC, abstractmethod
from .adapters import RunResult

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    def run(self, prompt: str, **kwargs) -> RunResult:
        """Execute a prompt and return the result."""
        pass
    
    def save_state(self, file_path: str):
        """Saves the conversation history to a file."""
        raise NotImplementedError("This agent does not support saving state.")

    def load_state(self, file_path: str):
        """Loads the conversation history from a file."""
        raise NotImplementedError("This agent does not support loading state.")

    def get_id(self) -> str:
        return self.id if hasattr(self, "id") else "unnamed"
    
    @abstractmethod
    def add_user_message(self, user_text: str, position: str = "end"):
        pass

    def compact_messages(self, model: str = "glm-4.5"):
        """
        Compacts the conversation history by summarizing the first half of messages using a duplicate agent.
        
        Replaces the first half of self.messages with a single compacted summary message,
        reducing the total message count and checkpoint file size.
        
        Args:
            model: Model to use for generating the summary.
        """
        if len(self.messages) < 4:
            if self.debug:
                print(f"[DEBUG] compact_messages: Too few messages ({len(self.messages)}) to compact")
            return
        
        # Calculate split point (first half)
        split_point = len(self.messages) // 2
        first_half = self.messages[:split_point]
        second_half = self.messages[split_point:]
        
        if self.debug:
            print(f"[DEBUG] compact_messages: Compacting {len(first_half)} messages, keeping {len(second_half)}")
        
        # Create a temporary agent of the same type with only the first half of messages
        temp_agent = self.__class__(debug=self.debug)
        if hasattr(self, 'cwd'):
            temp_agent.cwd = self.cwd
        if hasattr(self, 'system_prompt'):
            temp_agent.system_prompt = self.system_prompt
        temp_agent.messages = copy.deepcopy(first_half)
        
        # DEBUG: Print exactly what we're sending for summary
        print(f"\n[COMPACT_DEBUG] === COMPACTION STARTING ===")
        print(f"[COMPACT_DEBUG] Total messages: {len(self.messages)}")
        print(f"[COMPACT_DEBUG] Split point: {split_point}")
        print(f"[COMPACT_DEBUG] First half size: {len(first_half)} messages")
        print(f"[COMPACT_DEBUG] Second half size: {len(second_half)} messages")
        print(f"[COMPACT_DEBUG] Temp agent message count: {len(temp_agent.messages)}")
        print(f"[COMPACT_DEBUG] First message in temp_agent: {str(temp_agent.messages[0])[:100] if temp_agent.messages else 'NONE'}...")
        print(f"[COMPACT_DEBUG] Last message in temp_agent: {str(temp_agent.messages[-1])[:100] if temp_agent.messages else 'NONE'}...")
        print(f"[COMPACT_DEBUG] First message in second_half: {str(second_half[0])[:100] if second_half else 'NONE'}...")
        print(f"[COMPACT_DEBUG] Model being used: {model}")
        
        # Generate summary using the temp agent (ephemeral so it doesn't affect its messages)
        summary_prompt = """Please provide a comprehensive summary of this entire conversation history. Include:
1. All key tasks, problems, and solutions discussed
2. Important technical details, code snippets, and decisions made
3. Current context and state of the conversation
4. Any patterns, iterations, or recurring themes
5. Specific data, configurations, or requirements mentioned

Be thorough but well-organized. The summary should preserve all critical information that might be referenced later."""
        
        if self.debug:
            print(f"[DEBUG] compact_messages: Running summary generation on temp agent")
        
        # Try to generate summary with retries
        max_retries = 5
        retry_count = 0
        summary_text = None
        
        while retry_count < max_retries and not summary_text:
            if retry_count > 0:
                print(f"[COMPACT_DEBUG] Retry {retry_count}/{max_retries} for summary generation...")
            else:
                print(f"[COMPACT_DEBUG] Sending summary request to model...")
            
            result = temp_agent.run(summary_prompt, model=model, ephemeral=True)
            
            # Extract summary text from result
            if hasattr(result, 'content') and result.content:
                # Check if it's an error message (happens when Instructor fails)
                if result.content.startswith("Error calling"):
                    if self.debug:
                        print(f"[DEBUG] compact_messages: Summary generation failed: {result.content[:100]}")
                    summary_text = None
                else:
                    summary_text = result.content
            elif hasattr(result, 'data') and isinstance(result.data, dict):
                # Handle both ClaudeAgent and OpenSourceAgent result formats
                if 'result' in result.data:
                    summary_text = result.data['result']
                else:
                    summary_text = str(result.data)
            
            # Check if we got valid summary
            if summary_text and summary_text.strip() and len(summary_text) > 50:
                print(f"[COMPACT_DEBUG] Summary generation completed successfully")
                break
            else:
                retry_count += 1
                summary_text = None
                if retry_count < max_retries:
                    import time
                    time.sleep(1)  # Brief pause before retry
        
        # DEBUG: Print the full summary for inspection
        if summary_text:
            print(f"[COMPACT_DEBUG] Summary generated, length: {len(summary_text)} chars")
            print(f"[COMPACT_DEBUG] FULL SUMMARY CONTENT:")
            print("[COMPACT_DEBUG] " + "=" * 60)
            for line in summary_text.split('\n'):
                print(f"[COMPACT_DEBUG] {line}")
            print("[COMPACT_DEBUG] " + "=" * 60)
        
        # Fallback if summarization fails or is empty after retries
        if not summary_text or summary_text.strip() == "":
            if self.debug:
                print(f"[DEBUG] compact_messages: All retries failed, using fallback")
            print(f"[COMPACT_DEBUG] WARNING: Summary generation failed after {max_retries} attempts")
            summary_text = f"[Compacted {len(first_half)} messages from conversation history]"
        
        # Replace messages: keep only second half
        self.messages = second_half
        
        # Prepend the summary as a user message at the start
        summary_message = f"[CONVERSATION SUMMARY]\n{summary_text}"
        
        # Use add_user_message if available (both agents should have it now)
        if hasattr(self, 'add_user_message'):
            self.add_user_message(summary_message, position="start")
        else:
            # Fallback for any agent that doesn't have add_user_message
            new_msg = {"role": "user", "content": summary_message}
            self.messages.insert(0, new_msg)
        
        if self.debug:
            original_count = len(first_half) + len(second_half)
            print(f"[DEBUG] compact_messages: Reduced from {original_count} to {len(self.messages)} messages")

class OpenSourceAgent(BaseAgent):
    def __init__(self, debug=False, system_prompt=None, cwd=None, id=None) -> None:
        self.cwd = cwd
        self.messages = []
        self.system_prompt = system_prompt
        self.debug = debug
        self.id = id
        # We separate system prompt and normal message, so the following is commented out
        # if system_prompt:
        #     self.messages.append({"role": "system", "content": system_prompt})
    
    def save_state(self, file_path: str):
        """Save conversation history to a JSON file in Qwen format"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to Qwen format before saving
        qwen_messages = self._convert_to_qwen_format(self.messages)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(qwen_messages, f, ensure_ascii=False, indent=2)
        
        if self.debug:
            print(f"[DEBUG] Saved {len(qwen_messages)} messages to {path}")
    
    def load_state(self, file_path: str):
        """Load conversation history from a JSON file"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                # Load directly - format will be converted on-demand when needed
                self.messages = json.load(f)
            
            if self.debug:
                print(f"[DEBUG] Loaded {len(self.messages)} messages from {path}")

    def add_user_message(self, user_text: str, position: str = "end"):
        """
        Adds a user message at specified position, merging with adjacent user messages if needed.
        
        Args:
            user_text: The text content to add
            position: "start" or "end" (default: "end")
        """
        add_user_message_opensouce(self.messages, user_text, position, self.debug)
    
    def _convert_to_qwen_format(self, messages):
        """Convert messages to Qwen format (role/parts structure)"""
        qwen_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                # Check if already in Qwen format
                if "parts" in msg:
                    qwen_messages.append(msg)
                else:
                    # Convert from simple format to Qwen format
                    role = msg.get("role", "user")
                    # Map assistant to model for Qwen
                    if role == "assistant":
                        role = "model"
                    content = msg.get("content", "")
                    qwen_messages.append({
                        "role": role,
                        "parts": [{"text": content}]
                    })
        return qwen_messages
    
    def _run_with_qwen(self, prompt: str, model: str, system_prompt: Optional[str] = None, ephemeral: bool = False):
        """Run using Qwen Code CLI"""
        import tempfile
        import hashlib
        
        # Get model config
        from .utils.model_config import get_model_config
        model_cfg = get_model_config().get_model(model)
        if not model_cfg:
            return RunResult({"status": "error", "message": f"Model '{model}' not found in configuration"})
        
        # Find qwen command
        qwen_cmd = shutil.which('qwen')
        if not qwen_cmd:
            return RunResult({"status": "error", "message": "Qwen command not found. Please ensure it's in your PATH."})
        
        # Get project root (current working directory)
        project_root = os.path.abspath(self.cwd if self.cwd else os.getcwd())
        
        # Calculate SHA256 hash of project root (same as Qwen does)
        project_hash = hashlib.sha256(project_root.encode()).hexdigest()
        
        # Create checkpoint file if we have history
        checkpoint_file = None
        effective_system_prompt = system_prompt or self.system_prompt
        
        # Prepare messages with system prompt injection
        messages_to_save = copy.deepcopy(self.messages) if self.messages else []
        
        # If we have a system prompt, inject it at the beginning
        system_prompt_injected = False
        if effective_system_prompt:
            # Create the system prompt exchange
            system_user_msg = {"role": "user", "parts": [{"text": f"[System]: {effective_system_prompt}"}]}
            system_model_msg = {"role": "model", "parts": [{"text": "I understand and will follow these instructions."}]}
            
            # Check if we need to update or inject
            if len(messages_to_save) >= 2:
                # Check if first two messages are our system prompt
                first_msg = messages_to_save[0]
                if (first_msg.get('role') == 'user' and 
                    first_msg.get('parts') and 
                    '[System]:' in str(first_msg.get('parts', [{}])[0].get('text', ''))):
                    # Replace existing system prompt
                    messages_to_save[0] = system_user_msg
                    messages_to_save[1] = system_model_msg
                else:
                    # Insert new system prompt at beginning
                    messages_to_save = [system_user_msg, system_model_msg] + messages_to_save
            else:
                # Insert new system prompt at beginning
                messages_to_save = [system_user_msg, system_model_msg] + messages_to_save
            system_prompt_injected = True
        
        # Convert and save if we have messages
        if messages_to_save:
            # Convert to Qwen format
            qwen_messages = self._convert_to_qwen_format(messages_to_save)
            
            # Save to temporary checkpoint file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(qwen_messages, f, ensure_ascii=False)
                checkpoint_file = f.name
        
        # Generate unique tag to avoid conflicts
        save_tag = f"polycli-{uuid.uuid4().hex[:8]}"
        
        try:
            # Build command with all CLI arguments
            cmd = [
                qwen_cmd,
                '--prompt', prompt,
                '--save', save_tag,
                '--yolo',
                '--openai-api-key', model_cfg['api_key'],
                '--openai-base-url', model_cfg['endpoint'],
                '--model', model_cfg['model']
            ]
            
            # Add resume if we have history
            if checkpoint_file:
                cmd.extend(['--resume', checkpoint_file])
            
            # Handle system prompt - removed since we'll handle it via history injection
            
            # Debug: print command
            if self.debug:
                print(f"[DEBUG] Running command: {' '.join(cmd)}")
            
            # Set environment variables as well (qwen seems to prioritize env vars)
            env = os.environ.copy()
            env['OPENAI_MODEL'] = model_cfg['model']
            env['OPENAI_API_KEY'] = model_cfg['api_key']
            env['OPENAI_BASE_URL'] = model_cfg['endpoint']
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                env=env,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # Check for silent failure (empty stdout indicates checkpoint size issue)
                if not result.stdout or not result.stdout.strip():
                    if self.debug:
                        print(f"[DEBUG] Detected qwen-code silent failure (empty stdout)")
                        checkpoint_size = len(json.dumps(messages_to_save, ensure_ascii=False)) if messages_to_save else 0
                        print(f"[DEBUG] Checkpoint size was: ~{checkpoint_size} bytes")
                    
                    # Attempt auto-recovery via compaction if we have enough messages
                    if len(self.messages) >= 4:
                        if self.debug:
                            print(f"[DEBUG] Attempting auto-recovery via message compaction")
                        
                        # Create a backup of messages before attempting recovery
                        original_messages = copy.deepcopy(self.messages)
                        
                        try:
                            # Compact messages to reduce checkpoint size
                            self.compact_messages()
                            
                            if self.debug:
                                print(f"[DEBUG] Messages compacted from {len(original_messages)} to {len(self.messages)}")
                                new_size = len(json.dumps(self._convert_to_qwen_format(self.messages), ensure_ascii=False))
                                print(f"[DEBUG] New checkpoint size estimate: ~{new_size} bytes")
                                print(f"[DEBUG] Retrying qwen-code with compacted history")
                            
                            # Retry the qwen-code call with compacted history
                            return self._run_with_qwen(prompt, model, system_prompt, ephemeral)
                            
                        except Exception as e:
                            if self.debug:
                                print(f"[DEBUG] Auto-recovery failed: {e}")
                            # Restore original messages on failure
                            self.messages = original_messages
                            return RunResult({
                                "status": "error",
                                "message": f"Qwen-code silent failure detected and auto-recovery failed: {e}"
                            })
                    else:
                        return RunResult({
                            "status": "error",
                            "message": "Qwen-code silent failure detected but too few messages to compact"
                        })
                
                # Load the saved checkpoint from Qwen's location
                qwen_dir = Path.home() / ".qwen" / "tmp" / project_hash
                saved_checkpoint = qwen_dir / f"checkpoint-{save_tag}.json"
                
                if saved_checkpoint.exists():
                    # Load the conversation
                    with open(saved_checkpoint, 'r', encoding='utf-8') as f:
                        new_messages = json.load(f)
                    
                    # Clean up the saved checkpoint
                    saved_checkpoint.unlink()
                    
                    # Only update messages if not ephemeral
                    if not ephemeral:
                        # If we injected a system prompt earlier, remove it from the saved messages
                        # to avoid polluting the conversation history
                        if system_prompt_injected and len(new_messages) >= 2:
                            first_msg = new_messages[0]
                            if (first_msg.get('role') == 'user' and 
                                first_msg.get('parts') and 
                                '[System]:' in str(first_msg.get('parts', [{}])[0].get('text', ''))):
                                # Remove the injected system prompt messages
                                new_messages = new_messages[2:]
                        self.messages = new_messages
                    
                    # Extract last model response using utility
                    last_response = ""
                    for msg in reversed(new_messages):
                        if msg.get("role") == "model":
                            last_response = extract_message_content(msg)
                            if last_response:
                                break
                    
                    if self.debug:
                        print(f"[DEBUG] Loaded conversation from {saved_checkpoint}")
                        if ephemeral:
                            print(f"[DEBUG] Ephemeral mode: conversation not saved to messages")
                        else:
                            print(f"[DEBUG] Total messages: {len(self.messages)}")
                    
                    return RunResult({
                        "status": "success",
                        "message": {"role": "assistant", "content": last_response},
                        "type": "assistant"
                    })
                else:
                    return RunResult({
                        "status": "error",
                        "message": f"Checkpoint file not found at {saved_checkpoint}"
                    })
            else:
                return RunResult({
                    "status": "error",
                    "message": f"Qwen command failed: {result.stderr}"
                })
                
        finally:
            # Clean up temporary checkpoint file
            if checkpoint_file and os.path.exists(checkpoint_file):
                os.unlink(checkpoint_file)
    
    def _run_no_tools(self, prompt: str, model: str, system_prompt: Optional[str] = None, 
                      schema_cls: Optional[Type[BaseModel]] = None, 
                      memory_serializer: Optional[Callable[[BaseModel], str]] = None,
                      ephemeral: bool = False):
        """Run using direct LLM API without tools (similar to Claude Code with non-Claude models)"""
        # Get LLM client
        try:
            llm_client, actual_model_name = get_llm_client(model)
        except Exception as e:
            return RunResult({"status": "error", "message": str(e)})
        
        if self.debug:
            print(f"[DEBUG] Running no-tools mode with model: {model}")
        
        # Prepare messages for the LLM
        messages = []
        
        # Use provided system prompt, fall back to default
        effective_system_prompt = system_prompt or self.system_prompt
        if effective_system_prompt:
            messages.append({"role": "system", "content": effective_system_prompt})
        
        # Convert existing messages to standard format and add to messages
        for msg in self.messages:
            # Extract content using utility
            content = extract_message_content(msg)
            if content:
                role = msg.get("role", "user")
                if role == "model":
                    role = "assistant"
                messages.append({"role": role, "content": content})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        try:
            if schema_cls:
                # Structured response
                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Serialize for messages
                serializer = memory_serializer or default_json_serializer
                response_text = serializer(result)
                
                # Update messages only if not ephemeral
                if not ephemeral:
                    self.messages.append({"role": "user", "content": prompt})
                    self.messages.append({"role": "assistant", "content": f"[Structured response ({schema_cls.__name__})]\n{response_text}"})
                
                if self.debug:
                    if ephemeral:
                        print(f"[DEBUG] No-tools mode completed with structured output (ephemeral)")
                    else:
                        print(f"[DEBUG] No-tools mode completed with structured output. Total messages: {len(self.messages)}")
                
                return RunResult({
                    "status": "success",
                    "result": result.model_dump(),
                    "type": "structured",
                    "schema": schema_cls.__name__
                })
            else:
                # Plain text response - bypass Instructor for better compatibility
                # Use raw API directly instead of Instructor wrapper
                result = llm_client.client.chat.completions.create(
                    model=actual_model_name,
                    messages=messages
                )
                
                # Extract response content from raw API response
                if result and result.choices and result.choices[0].message:
                    response_content = result.choices[0].message.content
                else:
                    response_content = ""
                
                # Update messages only if not ephemeral
                if not ephemeral:
                    self.messages.append({"role": "user", "content": prompt})
                    self.messages.append({"role": "assistant", "content": response_content})
                
                if self.debug:
                    if ephemeral:
                        print(f"[DEBUG] No-tools mode completed (ephemeral)")
                    else:
                        print(f"[DEBUG] No-tools mode completed. Total messages: {len(self.messages)}")
                
                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": response_content},
                    "type": "assistant"
                })
            
        except Exception as e:
            error_msg = f"Error calling {model}: {str(e)}"
            if self.debug:
                print(f"[DEBUG] {error_msg}")
            return RunResult({"status": "error", "message": error_msg})
    
    def run(self, prompt: str, model="glm-4.5", system_prompt=None, cli="qwen-code", 
            schema_cls: Optional[Type[BaseModel]] = None, 
            memory_serializer: Optional[Callable[[BaseModel], str]] = None,
            ephemeral: bool = False):
        if cli == "mini-swe":
            # Import mini-swe dependencies only when needed
            from minisweagent.agents.default import DefaultAgent
            from minisweagent.environments.local import LocalEnvironment
            from .utils.llm_client import CustomMiniSweModel
            
            temp_agent = DefaultAgent(
                CustomMiniSweModel(model_name=model),
                LocalEnvironment(cwd=self.cwd if self.cwd else ""),
            )
            
            # Set step limit to prevent infinite loops
            temp_agent.config.step_limit = 10
            
            if system_prompt:
                temp_agent.config.system_template = system_prompt
            else:
                # Use a better default system template for mini-swe
                temp_agent.config.system_template = """You are a helpful AI assistant that can execute shell commands.

When you need to run a command, provide EXACTLY ONE action in triple backticks like this:
```bash
echo "Hello World"
```

After running the command, you will see the output. To complete a task, make sure the FIRST LINE of your command output is 'MINI_SWE_AGENT_FINAL_OUTPUT'."""        

            if self.messages:
                # Convert messages to mini-swe format
                converted_messages = []
                for msg in self.messages:
                    # Extract content using utility
                    content = extract_message_content(msg)
                    if content:
                        role = msg.get("role", "user")
                        if role == "model":
                            role = "assistant"
                        converted_messages.append({"role": role, "content": content})
                
                input_text = json_list_serializer(converted_messages) + "\nuser (current task): " + prompt
            else:
                input_text = prompt
            status, message = temp_agent.run(input_text)

            # Store in simple format for mini-swe only if not ephemeral
            if not ephemeral:
                self.messages = self.messages + [{"role": "user", "content": prompt}] + copy.deepcopy(temp_agent.messages[2:])
            
            if self.debug and ephemeral:
                print(f"[DEBUG] Ephemeral mode: response not added to messages")

            return RunResult({"status": status, "message": {"role": "assistant", "content": message}, "type": "assistant"})
        elif cli == "qwen-code":
            return self._run_with_qwen(prompt, model, system_prompt, ephemeral)
        elif cli == "no-tools":
            return self._run_no_tools(prompt, model, system_prompt, schema_cls, memory_serializer, ephemeral)
        else:
            return RunResult({"status": "error", "message": f"CLI '{cli}' not supported."})

class ClaudeAgent(BaseAgent):
    """
    Manages a conversation with the Claude CLI or other LLMs, handling state and session resumption.

    The agent's state is stored entirely in the `self.messages` list. When continuing
    a conversation with existing history, the agent creates a new session file with
    the conversation history and uses the --resume flag to replay it.
    """

    def __init__(self, debug=False, system_prompt=None, cwd=None, id=None):
        """Initializes a new Agent.

        Args:
            debug (bool): If True, prints detailed diagnostic information.
            system_prompt (str): Default system prompt to use for all runs unless overridden.
            id (str): Optional unique identifier for the agent.
            cwd (str|Path): Working directory for Claude Code execution. If None, uses current directory.
        """
        self.messages = []
        self.debug = debug
        self.default_system_prompt = system_prompt
        self.cwd = str(Path(cwd)) if cwd else None
        self.id = id
        self._claude_cmd = self._find_claude_command()
        self._claude_projects_dir = Path.home() / ".claude" / "projects"
        
        # Model configuration will be loaded on demand from models.json

    def _find_claude_command(self):
        claude_cmd = shutil.which('claude')
        if not claude_cmd:
            raise FileNotFoundError("Claude command not found. Please ensure it's in your PATH.")
        return claude_cmd

    def _encode_path(self, path_str: str) -> str:
        """Replicates Claude's path encoding for session files."""
        if sys.platform == "win32" and ":" in path_str:
            drive, rest = path_str.split(":", 1)
            rest = rest.lstrip(os.path.sep)
            path_str = f"{drive}--{rest}"
        return path_str.replace(os.path.sep, '-')

    def load_state(self, file_path):
        """Loads conversation history from a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to load from.
        """
        self.messages = []
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.messages.append(json.loads(line))

    def save_state(self, file_path):
        """Saves conversation history to a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to save to.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for msg in self.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        if self.debug:
            print(f"[DEBUG] Persisted {len(self.messages)} messages to {path}")

    def add_user_message(self, user_text: str, position: str = "end"):
        """
        Adds a user message at specified position, merging with adjacent user messages if needed.
        
        Args:
            user_text: The text content to add
            position: "start" or "end" (default: "end")
        """
        add_user_message_claude(self.messages, user_text, self.cwd, position, self.debug)
        
    def _extract_conversation_history(self) -> List[Dict[str, str]]:
        """Extract meaningful text content from the conversation history for LLM consumption."""
        conversation = []
        
        for entry in self.messages:
            # Get role from the message
            message = entry.get('message', {})
            role = message.get('role')
            
            # Skip if no role
            if not role:
                continue
            
            # Extract content using our utility (including tool use for Claude history)
            content = extract_message_content(entry, include_tool_use=True)
            
            # If we have any content, add to conversation
            if content:
                conversation.append({
                    'role': role,
                    'content': content
                })
        
        return conversation

    def _run_with_llm(self, prompt: str, model: str, system_prompt: Optional[str] = None, ephemeral: bool = False, schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None):
        """Run the prompt using an external LLM.
        
        Args:
            prompt: The prompt to send
            model: Model name to use
            system_prompt: Optional system prompt for this run
            ephemeral: If True, the prompt and response won't be added to messages
        """
        # Get client for this model
        try:
            llm_client, actual_model_name = get_llm_client(model)
        except Exception as e:
            return RunResult({"error": str(e)})
        
        if self.debug:
            print(f"[DEBUG] Running with LLM model: {model} (ephemeral: {ephemeral})")
        
        # Extract current conversation history
        history = self._extract_conversation_history()
        
        # Prepare messages for the LLM
        messages = []
        
        # Use provided system prompt, fall back to default, or use a basic one
        effective_system_prompt = system_prompt or self.default_system_prompt or \
            "You are a helpful AI assistant. The following is a conversation history. Please provide a helpful response to the latest query."
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": effective_system_prompt
        })
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add the current prompt as a user message (in messages list, not persisted)
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Define response model
        class LLMResponse(BaseModel):
            response: str = Field(description="The AI assistant's response")
        
        try:
            if schema_cls:
                # Structured response path
                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Only add to messages if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Serialize for messages
                    serializer = memory_serializer or default_json_serializer
                    mem_text = serializer(result)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Structured response ({schema_cls.__name__})]\n{mem_text}"
                    self.add_user_message(response_text)
                
                # Return structured response
                return RunResult({
                    "result": result.model_dump(),
                    "session_id": self.messages[-1].get('sessionId') if self.messages else None,
                    "model": model,
                    "ephemeral": ephemeral
                })
            else:
                # Plain text response - bypass Instructor for better compatibility
                # Use raw API directly instead of Instructor wrapper
                result = llm_client.client.chat.completions.create(
                    model=actual_model_name,
                    messages=messages
                )
                
                # Extract response content from raw API response
                response_content = ""
                if result and result.choices and result.choices[0].message:
                    response_content = result.choices[0].message.content or ""
                
                # Only add to messages if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Following is {model}'s response]\n{response_content}"
                    self.add_user_message(response_text)
                
                # Return standardized format
                return RunResult({
                    "result": response_content,
                    "session_id": self.messages[-1].get('sessionId') if self.messages else None,
                    "model": model,
                    "ephemeral": ephemeral
                })
            
        except Exception as e:
            error_msg = f"Error calling {model}: {str(e)}"
            if self.debug:
                print(f"[DEBUG] {error_msg}")
            return RunResult({"error": error_msg})

    def _run_with_claude(self, prompt: str, system_prompt: Optional[str] = None):
        """Run the prompt using Claude Code (original implementation)."""
        if self.debug: print("\n--- AGENT RUN (Claude) ---")

        current_dir = self.cwd if self.cwd else os.getcwd()
        cwd_encoded = self._encode_path(current_dir)
        session_dir = self._claude_projects_dir / cwd_encoded
        use_shell = sys.platform == 'win32'
        
        session_file_we_made = None
        session_file_claude_made = None

        try:
            # Determine the resume ID from messages. No messages means no resume ID.
            resume_id = self.messages[-1].get('sessionId') if self.messages else None

            # Build base command with required flags
            base_cmd = [self._claude_cmd, prompt, '-p', '--output-format', 'json', '--dangerously-skip-permissions']
            
            # Add system prompt if provided (use run-specific or fall back to default)
            effective_system_prompt = system_prompt or self.default_system_prompt
            if effective_system_prompt:
                base_cmd.extend(['--system-prompt', effective_system_prompt])

            if not resume_id:
                # --- Path 1: NEW CONVERSATION ---
                if self.debug: print("[DEBUG] STRATEGY: New conversation. Letting Claude handle state.")
                cmd = base_cmd
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")
            else:
                # --- Path 2: RESUME CONVERSATION ---
                if self.debug: print(f"[DEBUG] STRATEGY: Resuming with Session ID: {resume_id}")
                
                session_file_we_made = session_dir / f"{resume_id}.jsonl"
                session_dir.mkdir(parents=True, exist_ok=True)
                with open(session_file_we_made, 'w', encoding='utf-8') as f:
                    for msg in self.messages:
                        f.write(json.dumps(msg) + '\n')
                if self.debug: print(f"[DEBUG] Wrote {len(self.messages)} messages to temp file: {session_file_we_made}")

                cmd = base_cmd + ['--resume', resume_id]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")

            # --- Process Result (Same for both paths) ---
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                # Use the new session ID from the response to load the updated history
                new_session_id = response_data.get('session_id')
                if new_session_id:
                    session_file_claude_made = session_dir / f"{new_session_id}.jsonl"
                    if self.debug: print(f"[DEBUG] Command successful. Loading updated history from NEW session file: {session_file_claude_made}")
                    
                    # Load a new messages state from the file Claude just created
                    new_messages = []
                    if session_file_claude_made.exists():
                        with open(session_file_claude_made, 'r', encoding='utf-8') as f:
                             for line in f:
                                if line.strip(): new_messages.append(json.loads(line))
                    self.messages = new_messages
                
                # Standardize response format to match OpenRouter format
                return RunResult({
                    "result": response_data.get('result'),
                    "session_id": response_data.get('session_id'),
                    "model": "claude-code",
                    "ephemeral": False,
                    # Keep original Claude metadata for advanced users
                    "_claude_metadata": response_data
                })
            else:
                error_details = f"Exit Code: {result.returncode}\n--- STDERR ---\n{result.stderr or 'No stderr.'}\n--- STDOUT ---\n{result.stdout or 'No stdout.'}\n"
                return RunResult({"error": error_details})

        finally:
            # Clean up both temporary session files
            if session_file_we_made and session_file_we_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up temp file we made: {session_file_we_made}")
                session_file_we_made.unlink()
            if session_file_claude_made and session_file_claude_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up file Claude made: {session_file_claude_made}")
                session_file_claude_made.unlink()

    def run(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None, 
            ephemeral: bool = False, messages_cutoff: Optional[int] = None, 
            schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None, cli="claude-code"):
        """
        Runs a prompt, automatically handling session state, and returns the result.
        
        Args:
            prompt: The prompt to run
            model: Optional model name. If not provided, uses Claude Code.
                   If provided, uses the specified model from models.json configuration.
            system_prompt: Optional system prompt for this specific run.
                          If not provided, uses the default system prompt from __init__.
            ephemeral: If True and using a non-Claude model, the interaction won't be saved to messages.
                      This parameter is ignored for Claude Code calls.
            messages_cutoff: Maximum number of items to keep in messages. When exceeded, oldest items 
                          are removed. Default is 50. Set to None to disable cutoff.
        
        Returns:
            Dictionary with the response result
        """
        # Run the prompt with the appropriate method
        if model:
            # later we will change it to check for cli rather than model, after we implemented the functionality of using different models for claude code
            result = self._run_with_llm(prompt, model, system_prompt, ephemeral, schema_cls, memory_serializer)
        else:
            if ephemeral and self.debug:
                print("[DEBUG] Warning: ephemeral parameter ignored for Claude Code calls")
            if schema_cls and self.debug:
                print("[DEBUG] Warning: schema_cls parameter ignored for Claude Code calls")
            result = self._run_with_claude(prompt, system_prompt)
        
        # Apply messages cutoff if enabled
        if messages_cutoff is not None and len(self.messages) > messages_cutoff:
            items_to_remove = len(self.messages) - messages_cutoff
            if self.debug:
                print(f"[DEBUG] Messages cutoff reached ({len(self.messages)} > {messages_cutoff}). "
                      f"Removing {items_to_remove} oldest items.")
            self.messages = self.messages[items_to_remove:]
        
        return result

