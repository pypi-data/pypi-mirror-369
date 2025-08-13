from datetime import datetime, timezone
import uuid
import os


def extract_message_content(msg, include_tool_use=False):
    """
    Extract text content from a message, handling all formats:
    - Standard format: {"role": "...", "content": "..."}
    - Qwen format: {"role": "...", "parts": [{"text": "..."}]}
    - Claude format: {"type": "...", "message": {"content": [{"type": "text", "text": "..."}]}}
    
    Args:
        msg: The message dict to extract content from
        include_tool_use: If True, also include tool use information (for Claude messages)
    
    Returns the extracted text content or empty string if not found.
    """
    if not isinstance(msg, dict):
        return ''
    
    # Standard format - content is directly available
    if 'content' in msg and isinstance(msg['content'], str):
        return msg['content']
    
    # Qwen format - content is in parts[0]['text']
    if 'parts' in msg:
        parts = msg.get('parts', [])
        if parts and isinstance(parts[0], dict) and 'text' in parts[0]:
            return parts[0]['text']
        elif parts:
            return str(parts[0])
    
    # Claude format - content is in message.content[{type: text/tool_use/tool_result}]
    def extract_from_content_list(content_list):
        """Helper to extract text from Claude's content list format"""
        text_parts = []
        for item in content_list:
            if isinstance(item, dict):
                content_type = item.get('type')
                
                if content_type == 'text':
                    text = item.get('text', '').strip()
                    if text and text != '[Request interrupted by user]':
                        text_parts.append(text)
                
                elif include_tool_use and content_type == 'tool_use':
                    # Include tool use information
                    tool_name = item.get('name', 'unknown_tool')
                    tool_input = item.get('input', {})
                    text_parts.append(f"[Tool Use: {tool_name}]")
                    
                    # Extract key information from common tools
                    if tool_name in ['Write', 'Edit', 'Read']:
                        file_path = tool_input.get('file_path', '')
                        text_parts.append(f"{tool_name}: {file_path}")
                    elif tool_name == 'Bash':
                        command = tool_input.get('command', '')
                        text_parts.append(f"Running: {command}")
                    elif tool_name == 'Task':
                        description = tool_input.get('description', '')
                        text_parts.append(f"Task: {description}")
                    elif tool_name == 'Grep':
                        pattern = tool_input.get('pattern', '')
                        path = tool_input.get('path', '.')
                        text_parts.append(f"Searching '{pattern}' in {path}")
                    elif tool_name == 'LS':
                        path = tool_input.get('path', '')
                        text_parts.append(f"Listing: {path}")
                
                elif include_tool_use and content_type == 'tool_result':
                    # Include tool results
                    result = item.get('content', '')
                    if isinstance(result, str):
                        result = result.strip()
                        if result:
                            # Show more of the result for useful output
                            if len(result) <= 500:
                                text_parts.append(f"[Tool Result]\n{result}")
                            else:
                                text_parts.append(f"[Tool Result]\n{result[:500]}...")
                        else:
                            # Even empty results can be meaningful (successful execution with no output)
                            text_parts.append("[Tool executed successfully]")
                    elif isinstance(result, list):
                        # Handle list content
                        text_parts.append("[Tool Result]")
                        for res_item in result[:5]:  # Show more items
                            if isinstance(res_item, str):
                                res_item = res_item.strip()
                                if res_item:
                                    text_parts.append(res_item[:200])
        
        return '\n'.join(text_parts) if text_parts else ''
    
    # Claude format with message wrapper
    if 'message' in msg:
        message = msg.get('message', {})
        content = message.get('content', [])
        
        # Handle list of content items
        if isinstance(content, list):
            return extract_from_content_list(content)
        # Handle direct string content
        elif isinstance(content, str):
            return content
    
    # Claude's direct content list format (without message wrapper)
    if 'content' in msg and isinstance(msg['content'], list):
        return extract_from_content_list(msg['content'])
    
    return ''


def normalize_messages_for_display(messages):
    """
    Normalize messages to ensure 'content' and 'role' fields exist at top level for display.
    This creates a copy with extracted content and role, preserving original format.
    """
    normalized = []
    for msg in messages:
        if isinstance(msg, dict):
            norm_msg = msg.copy()
            
            # Normalize content field - include tool use for Claude messages
            if 'content' not in norm_msg or not isinstance(norm_msg.get('content'), str):
                # For Claude messages, include tool results in display
                include_tools = 'message' in msg and 'content' in msg.get('message', {})
                norm_msg['content'] = extract_message_content(msg, include_tool_use=include_tools)
            
            # Normalize role field to top level
            if 'role' not in norm_msg:
                # Claude format: role is in message.role
                if 'message' in norm_msg and isinstance(norm_msg['message'], dict):
                    norm_msg['role'] = norm_msg['message'].get('role', 'unknown')
                # Sometimes type field indicates the role
                elif 'type' in norm_msg:
                    # Map Claude's type to standard role
                    msg_type = norm_msg['type']
                    if msg_type in ['user', 'assistant', 'system']:
                        norm_msg['role'] = msg_type
                    else:
                        norm_msg['role'] = 'user' if msg_type == 'human' else 'assistant'
                else:
                    norm_msg['role'] = 'unknown'
            
            # Normalize 'model' role to 'assistant' for consistency
            if norm_msg.get('role') == 'model':
                norm_msg['role'] = 'assistant'
            
            normalized.append(norm_msg)
        else:
            normalized.append(msg)
    return normalized

def _get_role_opensouce(message):
    """Helper to get role from either format"""
    if isinstance(message, dict):
        # Direct role field
        if "role" in message:
            role = message["role"]
            # Normalize model to assistant for comparison
            return "user" if role == "user" else ("assistant" if role in ["model", "assistant"] else role)
    return None

def add_user_message_opensouce(messages, user_text: str, position: str = "end", debug=False):
    """
    Adds a user message at specified position, merging with adjacent user messages if needed.
    
    Args:
        user_text: The text content to add
        position: "start" or "end" (default: "end")
    """
    if position == "end":
        # Check if last message is user and merge
        if messages and _get_role_opensouce(messages[-1]) == "user":
            last_msg = messages[-1]
            if "parts" in last_msg:  # Qwen format
                # Append to existing text
                if last_msg["parts"] and "text" in last_msg["parts"][0]:
                    last_msg["parts"][0]["text"] += "\n" + user_text
                else:
                    last_msg["parts"] = [{"text": user_text}]
            else:  # Simple format
                last_msg["content"] = last_msg.get("content", "") + "\n" + user_text
            
            if debug:
                print(f"[DEBUG] Appended to existing user message. Messages size: {len(messages)}")
        else:
            # Add new user message at end
            new_msg = {"role": "user", "content": user_text}
            messages.append(new_msg)
            if debug:
                print(f"[DEBUG] Created new user message. Messages size: {len(messages)}")
            
    elif position == "start":
        # Check if first message is user and merge
        if messages and _get_role_opensouce(messages[0]) == "user":
            first_msg = messages[0]
            if "parts" in first_msg:  # Qwen format
                # Prepend to existing text
                if first_msg["parts"] and "text" in first_msg["parts"][0]:
                    first_msg["parts"][0]["text"] = user_text + "\n" + first_msg["parts"][0]["text"]
                else:
                    first_msg["parts"] = [{"text": user_text}]
            else:  # Simple format
                first_msg["content"] = user_text + "\n" + first_msg.get("content", "")
            
            if debug:
                print(f"[DEBUG] Prepended to existing user message at start. Messages size: {len(messages)}")
        else:
            # Add new user message at start
            new_msg = {"role": "user", "content": user_text}
            messages.insert(0, new_msg)
            if debug:
                print(f"[DEBUG] Created new user message at start. Messages size: {len(messages)}")

def add_user_message_claude(messages, user_text: str, cwd: str | None, position: str = "end", debug=False):
    """
    Adds a user message at specified position, merging with adjacent user messages if needed.
    
    Args:
        user_text: The text content to add
        position: "start" or "end" (default: "end")
    """
    if position == "end":
        # Original logic - merge with last if it's user
        if messages and messages[-1].get('type') == 'user':
            # Last message is already a user message - append to it
            last_message = messages[-1]
            
            # Get the content array from the message
            content = last_message['message']['content']
            
            # Find the last text content item and append to it
            for i in range(len(content) - 1, -1, -1):
                if content[i]['type'] == 'text':
                    # Append with a newline
                    content[i]['text'] += '\nUser: ' + user_text
                    break
            else:
                # No text content found (shouldn't happen), add new text content
                content.append({"type": "text", "text": user_text})
            
            # Update timestamp to current time
            last_message['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            if debug:
                print(f"[DEBUG] Appended to existing user message. Messages size: {len(messages)}")
        else:
            # Last message is not a user message or messages list is empty - create new message
            last_message = messages[-1] if messages else {}
            session_id = last_message.get('sessionId') or str(uuid.uuid4())
            parent_uuid = last_message.get('uuid')
            user_message = _create_user_message(user_text, session_id, parent_uuid, cwd)
            messages.append(user_message)
            if debug:
                print(f"[DEBUG] Created new user message. Messages size: {len(messages)}")
                
    elif position == "start":
        # New logic - merge with first if it's user
        if messages and messages[0].get('type') == 'user':
            # First message is already a user message - prepend to it
            first_message = messages[0]
            
            # Get the content array from the message
            content = first_message['message']['content']
            
            # Find the first text content item and prepend to it
            for item in content:
                if item['type'] == 'text':
                    # Prepend with a newline separator: new + existing
                    item['text'] = user_text + '\nUser: ' + item['text']
                    break
            else:
                # No text content found, insert at beginning
                content.insert(0, {"type": "text", "text": user_text})
            
            # Update timestamp to current time
            first_message['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            if debug:
                print(f"[DEBUG] Prepended to existing user message at start. Messages size: {len(messages)}")
        else:
            # First message is not a user message or messages list is empty - create new message at start
            session_id = messages[0].get('sessionId') if messages else str(uuid.uuid4())
            user_message = _create_user_message(user_text, session_id, None, cwd)  # No parent for first message
            messages.insert(0, user_message)
            if debug:
                print(f"[DEBUG] Created new user message at start. Messages size: {len(messages)}")

def _create_user_message(text_content: str, session_id: str, parent_uuid: str | None, cwd: str | None) -> dict:
    """
    Creates a user message dictionary.
    Always uses list-of-dicts for content, as per ground truth examples.
    """
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    message_content = [{"type": "text", "text": text_content}]
    message_body = {"role": "user", "content": message_content}

    message = {
        "parentUuid": parent_uuid, "isSidechain": False, "userType": "external",
        "cwd": cwd if cwd else os.getcwd(),
        "sessionId": session_id, "version": "1.0.64",
        "gitBranch": "", "type": "user", "message": message_body,
        "uuid": str(uuid.uuid4()), "timestamp": now_iso
    }
    return message

