from typing import Dict, Any, List, Union, Optional, Tuple
from .exception import IncompleteResponseError
import requests
import logging
import uuid
import json
from datetime import datetime
from .base import Base
from .cache import CacheManager, InteractionCacheManager
import os
import hashlib
import tempfile
from pathlib import Path
import mimetypes
from bson import ObjectId
import time
from openai import OpenAI
import openai
import re

import anthropic

from google import genai
from google.genai import types
from google.genai.types import FinishReason
from google.oauth2 import service_account

import httpx
import base64

import pickle
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor

PROMPT_TO_GENERATE_SUMMARIZED_CONTENT = "Summarize the above conversation in a detailed, concise, and well-structured manner. ensuring the summary does not exceed 250 words. Capture the key points and context, including important questions, answers, and relevant follow-up, while avoiding unnecessary repetition. Present the summary in a well-structured paragraph, focusing on the most important content exchanged"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,  # This ensures our configuration takes precedence
    handlers=[logging.StreamHandler()],  # This ensures output goes to console
)
logger = logging.getLogger(__name__)


class MessageQueue:
    def __init__(self, prompt_manager: "PromptManager"):
        self.queue = deque()
        self.is_processing = False
        self.prompt_manager = prompt_manager
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._shutdown = False

    async def add_message(self, message_data: Dict):
        """Add message to queue"""
        if not self._shutdown:
            self.queue.append(message_data)
            if not self.is_processing:
                asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process messages in queue"""
        if self.is_processing:
            return

        self.is_processing = True
        try:
            while self.queue and not self._shutdown:
                message_data = self.queue.popleft()
                try:
                    # Add error handling and validation
                    if not message_data.get("user_prompt_id"):
                        raise ValueError("Missing required field: user_prompt_id")

                    # Ensure the request URL is properly formatted
                    endpoint = f"/save_bypass_logs/{message_data['user_prompt_id']}"

                    # Create payload with error checking
                    payload = {
                        "user_message": message_data.get("user_message", ""),
                        "ai_response": message_data.get("ai_response", {}),
                        "session_id": message_data.get("session_id", ""),
                        "memory_type": message_data.get("memory_type", ""),
                        "window_size": message_data.get("window_size", 0),
                        "summarized_content": message_data.get(
                            "summarized_content", ""
                        ),
                        "request_from": message_data.get("request_from", "sdk"),
                    }

                    # Make the request with timeout
                    response = await self.prompt_manager.request(
                        endpoint,
                        method="POST",
                        json=payload,
                        timeout=30,  # Add reasonable timeout
                    )

                    if response:
                        logger.info(
                            f"Successfully stored message. Response: {response}"
                        )
                    else:
                        logger.warning("Received empty response from server")

                except Exception as e:
                    logger.error(f"Failed to store message: {str(e)}", exc_info=True)
                    # Optionally retry or handle specific errors

        finally:
            self.is_processing = False

    async def shutdown(self):
        """Gracefully shutdown the message queue"""
        self._shutdown = True
        # Wait for queue to empty
        while self.queue and self.is_processing:
            await asyncio.sleep(0.1)
        # Shutdown executor
        if self.executor:
            self.executor.shutdown(wait=True)


class PromptManager(Base):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Set up persistent cache directory
        self.cache_dir = Path("./persistent_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self._supported_memory_types = [
            "windowMemory",
            "fullMemory",
            "summarizedMemory",
        ]  # Define supported memory types
        self.message_queue = MessageQueue(self)  # Add message queue

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file"""
        return self.cache_dir / f"{cache_key}.pkl"

    def _save_to_persistent_cache(self, cache_key: str, data: Dict):
        """Save data to persistent cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving to persistent cache: {str(e)}")

    def _load_from_persistent_cache(self, cache_key: str) -> Optional[Dict]:
        """Load data from persistent cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                with open(cache_path, "rb") as f:
                    data = pickle.load(f)
                return data
        except Exception as e:
            logger.error(f"Error loading from persistent cache: {str(e)}")
        return None

    async def request(self, endpoint: str, method: str, **kwargs):
        """Public method to make requests."""
        return await self._request(endpoint, method, **kwargs)

    def _print_persistent_cache_contents(self):
        """Print contents of persistent cache"""
        cache_files = list(self.cache_dir.glob("*.pkl"))

        for cache_file in cache_files:
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
            except Exception as e:
                logger.error(f"Error reading cache file {cache_file}: {str(e)}")

    async def get_all_prompts(self, folder_id: str) -> Dict:
        """
        Get all prompts for a given folder

        Args:
            folder_id: ID of the folder

        Returns:
            Dictionary containing prompt versions
        """
        response = await self._request(f"/{folder_id}")
        return response

    async def windowmemory_save_log_ai_interaction_prompt(
        self,
        user_prompt_id: str,
        interaction_request: Dict,
    ) -> Dict:
        """Process and save AI interaction using window memory cache"""
        try:

            # Generate session_id if not present
            session_id = interaction_request.get("session_id") or str(uuid.uuid4())


            # Get version (either from request or fetch latest)
            version = interaction_request.get("version")
            cache_key = f"{user_prompt_id}_{session_id}"
            prompt_details = CacheManager.get_prompt_details(cache_key)

            if not prompt_details:
                # Fetch and cache if not found
                prompt_details = await self._fetch_and_cache_prompt_details(
                    user_prompt_id, session_id, version
                )

            user_prompt_id = prompt_details["prompt_id"] 
            is_session_enabled = interaction_request.get("is_session_enabled")
            prompt_details["is_session_enabled"] = is_session_enabled

            # Get interaction history
            interaction_history = InteractionCacheManager.get_interaction_history(
                user_prompt_id, session_id, version
            )

            def_variables = prompt_details["variables"] if prompt_details else []
            default_variables = {}
            if (
                def_variables
                and (isinstance(def_variables, list) and len(def_variables) > 0)
                or (isinstance(def_variables, dict) and def_variables)
            ):

                default_variables = self.convert_data(def_variables)
                
            platform_name = prompt_details["ai_platform"]
            if platform_name == "custom":
                platform_key = ""
            else:
                platform_key = prompt_details["platform_config"]["platformKey"]

            # Determine which variables to use based on the conditions
            if not interaction_request.get("variables"):
                # Condition 1: No variables given in interaction_request
                variables = default_variables
            else:
                # Condition 2 and 3: Check how many variables are provided
                provided_variables = interaction_request.get("variables")
                variables = {**default_variables}  # Start with default variables
                # Count how many variables are in default_variables
                default_keys = set(default_variables.keys())
                provided_keys = set(provided_variables.keys())
                if provided_keys.issubset(default_keys):
                    # Condition 3: All provided variables are in default_variables
                    variables = provided_variables
                else:
                    # Condition 2: Some variables are provided
                    for key in provided_keys:
                        if key in default_keys:
                            variables[key] = provided_variables[key]
                    # Add remaining default variables
                    for key in default_keys:
                        if key not in provided_keys:
                            variables[key] = default_variables[key]

            prompt_collection_msg = []
            messages = []
            window_size = interaction_request.get("window_size")
            if window_size % 2 != 0:
                window_size += 1

            # Add system message if platform is OpenAI
            if platform_name == "openai":
                if prompt_details["system_prompt"]:
                    prompt_collection_msg.append(
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": prompt_details["system_prompt"]}
                        ],
                    }
                )
                else:
                    prompt_collection_msg.append(
                        {
                            "role": "system",
                            "content": [
                            {"type": "text", "text": ""}
                        ],
                    }
                )
            if platform_name == "groq" or platform_name == "grok" or platform_name == "custom":
                prompt_collection_msg.append(
                    {
                        "role": "system",
                        "content": prompt_details["system_prompt"],
                    }
                )
          
            # Add previous messages from history based on shot size
            if prompt_details and "messages" in prompt_details:

                published_messages = prompt_details["messages"]
                shot_size = interaction_request.get(
                    "shot", -1
                )  # Default to -1 for all messages

                if published_messages and shot_size != 0:
                    if shot_size > 0:
                        # Calculate number of messages to include (2 messages per shot)
                        messages_to_include = shot_size * 2
                        published_messages = published_messages[:messages_to_include]
                    # If shot_size is -1, use all messages (default behavior)
                    prompt_collection_msg.extend(published_messages)

            # Add previous messages within window size
            if interaction_history and interaction_history.get("messages"):
                # Get last N messages based on window size
                messages.extend(interaction_history["messages"])
                start_idx = max(
                    0, len(messages) - (window_size)
                )  # *2 for pairs of messages
                window_messages = messages[start_idx:]
                prompt_collection_msg.extend(window_messages)

            if platform_name == "claude":
                prompt_collection_msg = self.modify_messages_for_claude(
                    prompt_collection_msg
                )

                interaction_request["user_message"] = (
                    self.modify_new_user_message_for_claude(
                        interaction_request["user_message"]
                    )
                )
            # Add new user message
            # prompt_collection_msg.append(
            #     {
            #         "role": "user",
            #         "content": interaction_request["user_message"],
            #     }
            # )

            user_msg = interaction_request["user_message"]

            if user_msg and isinstance(user_msg[0], dict) and "role" in user_msg[0] and "content" in user_msg[0]:
                # Already in role-content format; append all
                prompt_collection_msg.extend(user_msg)
            else:
                # Old format; wrap under role=user
                prompt_collection_msg.append({
                    "role": "user",
                    "content": user_msg
                })
            
            prompt_details["system_prompt"] = self.replace_placeholders(prompt_details["system_prompt"], variables)
            # Replace placeholders in prompt_collection_msg
            prompt_collection_msg = self.replace_placeholders(prompt_collection_msg, variables)

            # Make AI platform request
            response = await self._make_ai_platform_request(
                platform_name=platform_name,
                prompt_details=prompt_details,
                messages=prompt_collection_msg,
                system_message=prompt_details["system_prompt"],
                platform_key=platform_key,
                variables=variables,
                prompt_id=user_prompt_id,
                base_url=interaction_request.get("base_url",None),
                format=interaction_request.get("format",None),
                credentials=interaction_request.get("credentials",None),
                grounding=interaction_request.get("grounding",None)

            )
           
            assistant_reply = response["response"]
            input_tokens = response["input_tokens"]
            output_tokens = response["output_tokens"]
            total_tokens = response["total_tokens"]

            # Create new messages to save
            current_time = datetime.now().isoformat()
            # new_messages = [
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "user",
            #         "content": interaction_request["user_message"],
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "assistant",
            #         "content": [{"type": "text", "text": f"{assistant_reply}"}],
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            # ]

            user_messages = interaction_request["user_message"]
            request_from = interaction_request.get("request_from", "sdk")

            # Determine if role-based format or flat content list
            if isinstance(user_messages, list) and all("role" in msg and "content" in msg for msg in user_messages):
                # It's a list of role-based messages — use as is
                new_messages = []

                for msg in user_messages:
                    new_messages.append({
                        "id": str(uuid.uuid4()),
                        "role": msg["role"],
                        "content": msg["content"],
                        "requestFrom": request_from,
                        "initiatedAt": current_time,
                    })

            else:
                # Flat list like: [{"type": "text", "text": "okay wt abt audi?"}]
                new_messages = [{
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": user_messages,
                    "requestFrom": request_from,
                    "initiatedAt": current_time,
                }]

            # Add assistant reply as the last message
            new_messages.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": [{"type": "text", "text": f"{assistant_reply}"}],
                "requestFrom": request_from,
                "initiatedAt": current_time,
            })

            # Save to cache with window memory configuration
            InteractionCacheManager.save_interaction(
                session_id=session_id,
                interaction_data={
                    "messages": new_messages,
                    "lastResponseAt": current_time,
                    "memory_type": "windowMemory",
                    "window_size": window_size,
                },
                prompt_id=user_prompt_id,
                version=version,
            )

            if self.is_logging:
    
                endpoint = f"/save_bypass_logs/{prompt_details['version_id']}"
                payload = {
                    "user_message": interaction_request["user_message"],
                    "ai_response": {"type": "text", "text": f"{assistant_reply}"},
                    "session_id": session_id,
                    "memory_type": "windowMemory",
                    "window_size": window_size,
                    "summarized_content": "",
                    "request_from": "python_sdk",
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "versionId":prompt_details["version_id"],
                    "platform":platform_name,
                    "model":prompt_details["model"],
                }

                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                    endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )
               
            if self.is_logging is False:

                endpoint = "/save_transaction_logs"
                payload = { 
                    "promptId":user_prompt_id,
                    "versionId":prompt_details["version_id"],
                    "platform":platform_name,
                    "model":prompt_details["model"],
                    "input_tokens":input_tokens,
                    "output_tokens":output_tokens,
                    "transaction_at":"python_sdk",
                    "session_id":session_id
                    
                }

                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                      endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )

            price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : platform_name,
                        "model" : prompt_details["model"],
                        "input_tokens" : input_tokens,
                        "output_tokens" : output_tokens
                        }
                )
            
            return {"response": assistant_reply,
                     "session_id": session_id,
                     "input_tokens": input_tokens,
                     "output_tokens": output_tokens,
                     "total_tokens": total_tokens,
                     "price": price_data["data"],
                     "promptId":user_prompt_id
                     }
                        
        except Exception as e:
            error_message = (
                f"An error occurred while processing AI interaction: {str(e)}"
            )
            logger.error(error_message)
            raise ValueError(error_message)


    # def modify_new_user_message_for_claude(self, messages):
    #     """
    #     Process direct messages for Claude API format by converting file_url to base64 encoded images.
    #     Args:
    #         messages (list): List of direct messages containing potential image content
    #     Returns:
    #         list: Processed messages with images converted to Claude's format
    #     """
    #     # Define supported image types and their corresponding media types
    #     supported_media_types = {
    #         ".png": "image/png",
    #         ".jpg": "image/jpeg",
    #         ".jpeg": "image/jpeg",
    #         ".jfif": "image/jpeg",
    #         # '.webp': 'image/webp',
    #         # '.heic': 'image/heic',
    #         # '.heif': 'image/heif',
    #         # '.gif': 'image/gif'
    #     }
    #     for message in messages:
    #         if "type" in message and message["type"] == "file":
    #             # Fetch the image URL dynamically
    #             file_url = message["file_url"]["url"]
    #             # Extract file extension from URL
    #             _, file_extension = os.path.splitext(file_url.lower())
    #             # Check if file extension is supported
    #             if file_extension not in supported_media_types:
    #                 raise ValueError(
    #                     f"Unsupported image format: {file_extension}. "
    #                     f"Supported formats are: {', '.join(supported_media_types.keys())}"
    #                 )
    #             # Get the corresponding media type
    #             image_media_type = supported_media_types[file_extension]
    #             # Fetch the image data and encode it in base64
    #             image_data = base64.b64encode(httpx.get(file_url).content).decode(
    #                 "utf-8"
    #             )
    #             # Update the message structure to Claude format
    #             message["type"] = "image"
    #             message["source"] = {
    #                 "type": "base64",
    #                 "media_type": image_media_type,
    #                 "data": image_data,
    #             }
    #             # Remove the old 'file_url' key
    #             message.pop("file_url", None)
    #     return messages



    def modify_new_user_message_for_claude(self, messages):
        """
        Modify user message to be compatible with Claude format.
        Handles both direct message format and role-based format.
        Converts file URLs to base64-encoded images for Claude.
        
        Args:
            messages (list): Either a flat list of content blocks or a list of role-based messages.
            
        Returns:
            list: Modified messages compatible with Claude's input format.
        """
        import os
        import base64
        import httpx

        supported_media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".jfif": "image/jpeg",
            # Add more if needed
        }

        def process_content_list(content_list):
            """Convert file_url entries in content list to Claude-compatible image blocks."""
            for content in content_list:
                if content.get("type") == "file":
                    file_url = content["file_url"]["url"]
                    _, ext = os.path.splitext(file_url.lower())
                    if ext not in supported_media_types:
                        raise ValueError(f"Unsupported image format: {ext}. Supported: {', '.join(supported_media_types)}")
                    media_type = supported_media_types[ext]
                    image_data = base64.b64encode(httpx.get(file_url).content).decode("utf-8")

                    # Update to Claude-compatible image format
                    content["type"] = "image"
                    content["source"] = {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data
                    }
                    content.pop("file_url", None)
            return content_list

        # Case 1: Role-based messages with "role" and "content"
        if all("role" in msg and "content" in msg for msg in messages):
            for msg in messages:
                msg["content"] = process_content_list(msg["content"])
            return messages

        # Case 2: Flat content list
        elif all("type" in msg for msg in messages):
            return process_content_list(messages)

        else:
            raise ValueError("Unsupported user_message format. Expecting role-based or flat content list.")



    async def fullmemory_save_log_ai_interaction_prompt(
        self,
        user_prompt_id: str,
        interaction_request: Dict,
    ) -> Dict:
        """Process and save AI interaction using cache memory"""
        try:
            # Generate session_id if not present
            session_id = interaction_request.get("session_id") or str(uuid.uuid4())

            # Get version (either from request or fetch latest)
            version = interaction_request.get("version")
            cache_key = f"{user_prompt_id}_{session_id}"
            prompt_details = CacheManager.get_prompt_details(cache_key)

            if not prompt_details:
                # Fetch and cache if not found
                prompt_details = await self._fetch_and_cache_prompt_details(
                    user_prompt_id, session_id, version
                )
                
            user_prompt_id = prompt_details["prompt_id"] 
            is_session_enabled = interaction_request.get("is_session_enabled")
            prompt_details["is_session_enabled"] = is_session_enabled

            # Get interaction history
            interaction_history = InteractionCacheManager.get_interaction_history(
                user_prompt_id, session_id, version
            )

            def_variables = prompt_details["variables"] if prompt_details else []
            default_variables = {}
            if (
                def_variables
                and (isinstance(def_variables, list) and len(def_variables) > 0)
                or (isinstance(def_variables, dict) and def_variables)
            ):
                default_variables = self.convert_data(def_variables)

            platform_name = prompt_details["ai_platform"]

            if platform_name == "custom":
                platform_key = ""
            else:
                platform_key = prompt_details["platform_config"]["platformKey"]

            # Determine which variables to use based on the conditions
            if not interaction_request.get("variables"):
                # Condition 1: No variables given in interaction_request
                variables = default_variables
            else:
                # Condition 2 and 3: Check how many variables are provided
                provided_variables = interaction_request.get("variables")
                variables = {**default_variables}  # Start with default variables
                # Count how many variables are in default_variables
                default_keys = set(default_variables.keys())
                provided_keys = set(provided_variables.keys())
                if provided_keys.issubset(default_keys):
                    # Condition 3: All provided variables are in default_variables
                    variables = provided_variables
                else:
                    # Condition 2: Some variables are provided
                    for key in provided_keys:
                        if key in default_keys:
                            variables[key] = provided_variables[key]
                    # Add remaining default variables
                    for key in default_keys:
                        if key not in provided_keys:
                            variables[key] = default_variables[key]

            # Build message collection
            prompt_collection_msg = []

            # Add system message if platform is OpenAI
            if platform_name == "openai":
                if prompt_details["system_prompt"]:
                    prompt_collection_msg.append(
                        {
                            "role": "system",
                            "content": [
                            {"type": "text", "text": prompt_details["system_prompt"]}
                        ],
                    }
                )
                else:
                    prompt_collection_msg.append(
                        {
                            "role": "system",
                            "content": [
                            {"type": "text", "text": ""}
                        ],
                    }
                )
                    
            if platform_name == "groq" or platform_name == "grok" or platform_name == "custom":
                prompt_collection_msg.append(
                    {
                        "role": "system",
                        "content": prompt_details["system_prompt"],
                    }
                )
            
            # Add previous messages from history based on shot size
            if prompt_details and "messages" in prompt_details:
                published_messages = prompt_details["messages"]
                shot_size = interaction_request.get(
                    "shot", -1
                )  # Default to -1 for all messages

                if published_messages and shot_size != 0:
                    if shot_size > 0:
                        # Calculate number of messages to include (2 messages per shot)
                        messages_to_include = shot_size * 2
                        published_messages = published_messages[:messages_to_include]
                    # If shot_size is -1, use all messages (default behavior)
                    prompt_collection_msg.extend(published_messages)

            # Add interaction messages from interaction history
            if interaction_history and interaction_history.get("messages"):
                prompt_collection_msg.extend(interaction_history["messages"])

            if platform_name == "claude":
                prompt_collection_msg = self.modify_messages_for_claude(
                    prompt_collection_msg
                )

                interaction_request["user_message"] = (
                    self.modify_new_user_message_for_claude(
                        interaction_request["user_message"]
                    )
                )

            # Add new user message
            # prompt_collection_msg.append(
            #     {
            #         "role": "user",
            #         "content": interaction_request["user_message"],
            #     }
            # )

            user_msg = interaction_request["user_message"]

            if user_msg and isinstance(user_msg[0], dict) and "role" in user_msg[0] and "content" in user_msg[0]:
                # Already in role-content format; append all
                prompt_collection_msg.extend(user_msg)
            else:
                # Old format; wrap under role=user
                prompt_collection_msg.append({
                    "role": "user",
                    "content": user_msg
                })

            prompt_details["system_prompt"] = self.replace_placeholders(prompt_details["system_prompt"], variables)
            # Replace placeholders in prompt_collection_msg
            prompt_collection_msg = self.replace_placeholders(prompt_collection_msg, variables)
           
            response = await self._make_ai_platform_request(
                platform_name=platform_name,
                prompt_details=prompt_details,
                messages=prompt_collection_msg,
                system_message=prompt_details["system_prompt"],
                platform_key=platform_key,
                variables=variables,
                prompt_id=user_prompt_id,
                base_url=interaction_request.get("base_url",None),
                format=interaction_request.get("format",None),
                credentials=interaction_request.get("credentials",None),
                grounding=interaction_request.get("grounding",None)
            )
            
            assistant_reply = response["response"]
            input_tokens = response["input_tokens"]
            output_tokens = response["output_tokens"]
            total_tokens = response["total_tokens"]
           

            # Create new messages to save
            current_time = datetime.now().isoformat()
            # new_messages = [
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "user",
            #         "content": interaction_request["user_message"],
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "assistant",
            #         "content": [{"type": "text", "text": f"{assistant_reply}"}],
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            # ]

            user_messages = interaction_request["user_message"]
            request_from = interaction_request.get("request_from", "sdk")

            # Determine if role-based format or flat content list
            if isinstance(user_messages, list) and all("role" in msg and "content" in msg for msg in user_messages):
                # It's a list of role-based messages — use as is
                new_messages = []

                for msg in user_messages:
                    new_messages.append({
                        "id": str(uuid.uuid4()),
                        "role": msg["role"],
                        "content": msg["content"],
                        "requestFrom": request_from,
                        "initiatedAt": current_time,
                    })

            else:
                # Flat list like: [{"type": "text", "text": "okay wt abt audi?"}]
                new_messages = [{
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": user_messages,
                    "requestFrom": request_from,
                    "initiatedAt": current_time,
                }]

            # Add assistant reply as the last message
            new_messages.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": [{"type": "text", "text": f"{assistant_reply}"}],
                "requestFrom": request_from,
                "initiatedAt": current_time,
            })

          
            # Save to cache with all required information
            InteractionCacheManager.save_interaction(
                session_id=session_id,
                interaction_data={
                    "messages": new_messages,
                    "lastResponseAt": current_time,
                    "memory_type": interaction_request.get("memory_type", "fullMemory"),
                    "window_size": interaction_request.get("window_size", 10),
                },
                prompt_id=user_prompt_id,
                version=version,
            )

            if self.is_logging:
            
                endpoint = f"/save_bypass_logs/{prompt_details['version_id']}"
                payload = {
                    "user_message": interaction_request["user_message"],
                    "ai_response": {"type": "text", "text": f"{assistant_reply}"},
                    "session_id": session_id,
                    "memory_type": "fullMemory",
                    "window_size": 0,
                    "summarized_content": "",
                    "request_from": "python_sdk",
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "platform":platform_name,
                    "model":prompt_details["model"],
    
                }

                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                    endpoint,
                    method="POST",
                    json=payload,
                    timeout=30, # Add reasonable timeout
                )

            if self.is_logging is False:

                endpoint = "/save_transaction_logs"
                payload = { 
                    "promptId":user_prompt_id,
                    "versionId":prompt_details["version_id"],
                    "platform":platform_name,
                    "model":prompt_details["model"],
                    "input_tokens":input_tokens,
                    "output_tokens":output_tokens,
                    "transaction_at":"python_sdk",
                    "session_id":session_id

                }
               
                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                    endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )

            price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : platform_name,
                        "model" : prompt_details["model"],
                        "input_tokens" : input_tokens,
                        "output_tokens" : output_tokens
                        }
                )
            
            return {"response": assistant_reply, 
                    "session_id": session_id,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "price": price_data["data"],
                    "promptId":user_prompt_id
                    }

        except Exception as e:
            error_message = (
                f"An error occurred while processing AI interaction: {str(e)}"
            )
            logger.error(error_message)
            raise ValueError(error_message)
        

    def replace_placeholders(self, msg_list, variables):
        # Check if variables is empty
        if not variables:
            return msg_list  # Return original list if variables is empty
        # Handle different types of input
        if isinstance(msg_list, dict):
            # If input is a dictionary, recursively process each value
            return {
                k: self.replace_placeholders(v, variables) for k, v in msg_list.items()
            }
        elif isinstance(msg_list, list):
            # If input is a list, recursively process each item
            return [self.replace_placeholders(msg, variables) for msg in msg_list]
        elif isinstance(msg_list, str):
            # If input is a string, replace placeholders
            for key, value in variables.items():
                msg_list = msg_list.replace(f"{{{{{key}}}}}", str(value))
            return msg_list
        else:
            # For any other type, return unchanged
            return msg_list
        # The following code is for handling specific message structures
        # Create a new list to store the modified messages
        modified_msg_list = []
        for msg in msg_list:
            new_msg = msg.copy()  # Create a copy of the message to modify
            if isinstance(new_msg, dict) and "content" in new_msg:
                if isinstance(new_msg["content"], str):
                    # Handle string content
                    for key, value in variables.items():
                        new_msg["content"] = new_msg["content"].replace(
                            f"{{{{{key}}}}}", str(value)
                        )
                elif isinstance(new_msg["content"], list):
                    # Handle list of content
                    new_content = []
                    for content in new_msg["content"]:
                        new_content_item = content.copy()
                        if (
                            isinstance(new_content_item, dict)
                            and "text" in new_content_item
                        ):
                            for key, value in variables.items():
                                new_content_item["text"] = new_content_item[
                                    "text"
                                ].replace(f"{{{{{key}}}}}", str(value))
                        new_content.append(new_content_item)
                    new_msg["content"] = new_content
            modified_msg_list.append(new_msg)
        return modified_msg_list  # Return the new list with modified messages


    def convert_data(self, data):
        # Create an empty dictionary to hold the converted data
        result = {}
        # Iterate through each item in the input data
        for item in data:
            # Extract 'name' and 'value' and add them to the result dictionary
            if "name" in item and "value" in item:
                result[item["name"]] = item["value"]
        return result


    def modify_messages_for_claude(self, messages):
        """
        Process images in messages for Claude API format by converting file_url to base64 encoded images.
        Args:
            messages (list): List of messages containing potential image content
            Returns:
            list: Processed messages with images converted to Claude's format
        """
        # Define supported image types and their corresponding media types
        supported_media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".jfif": "image/jpeg",
            # '.webp': 'image/webp',
            # '.heic': 'image/heic',
            # '.heif': 'image/heif',
            # '.gif': 'image/gif'
        }
        for message in messages:
            if "content" in message:
                for content in message["content"]:
                    if content.get("type") == "file":
                        # Fetch the image URL dynamically
                        file_url = content["file_url"]["url"]
                        # Extract file extension from URL
                        _, file_extension = os.path.splitext(file_url.lower())
                        # Check if file extension is supported
                        if file_extension not in supported_media_types:
                            raise ValueError(
                                f"Unsupported image format: {file_extension}. "
                                f"Supported formats are: {', '.join(supported_media_types.keys())}"
                            )
                        # Get the corresponding media type
                        image_media_type = supported_media_types[file_extension]
                        # Fetch the image data and encode it in base64
                        image_data = base64.b64encode(
                            httpx.get(file_url).content
                        ).decode("utf-8")
                        # Update the content structure
                        content["type"] = "image"
                        content["source"] = {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        }
                        # Remove the old 'file_url' key
                        content.pop("file_url", None)
        return messages


    def update_messages_collection(self, platform_name, system_message, old_messages):
        messages_collection = []
        # Add system message if platform is not Claude
        if platform_name == "openai":
            if system_message:
                system_content = [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": system_message}],
                    }
                ]
            else:
                system_content = [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": ""}],
                    }
                ]   
            messages_collection.extend(system_content)
        if platform_name == "groq" or platform_name == "grok" or platform_name == "custom":
            system_content = [
                {
                    "role": "system",
                    "content": system_message,
                }
            ]
            messages_collection.extend(system_content)

        if old_messages and len(old_messages) > 0:
            for message in old_messages:
                # Extract only the 'role' and 'content' fields
                simplified_message = {
                    "role": message["role"],
                    "content": message["content"],
                }
                messages_collection.append(simplified_message)

        return messages_collection


    async def summarizedmemory_save_log_ai_interaction_prompt(
        self,
        user_prompt_id: str,
        interaction_request: Dict,
    ) -> Dict:
        """Process and save AI interaction using summary memory cache"""
        try:

            session_type, session_id = self._fetch_session_id(interaction_request)
            # cache_key = f"{user_prompt_id}_{session_id}"
            cache_key_prompt_details = f"{user_prompt_id}_{session_id}_prompt_details"

            # Get version (either from request or fetch latest)
            version = interaction_request.get("version")

            # First fetch and cache prompt details
            prompt_details = CacheManager.get_prompt_details(cache_key_prompt_details)

            if not prompt_details:
                # Fetch and cache if not found
                prompt_details = await self._fetch_and_cache_prompt_details(
                    user_prompt_id, session_id, version
                )

            user_prompt_id = prompt_details["prompt_id"] 
            cache_key = f"{user_prompt_id}_{session_id}"
            prompt_details["is_session_enabled"] = interaction_request.get("is_session_enabled", True)

            system_message = (
                prompt_details["system_prompt"]
                if prompt_details.get("system_prompt")
                else ""
            )

            old_messages = []
            # Get messages from history based on shot size
            if prompt_details:
                shot_size = interaction_request.get("shot", -1)  # Default to -1 for all messages

                if prompt_details.get("messages") and shot_size != 0:
                    messages = prompt_details.get("messages", [])
                    if shot_size > 0:
                        # Calculate number of messages to include (2 messages per shot)
                        messages_to_include = shot_size * 2
                        old_messages = messages[:messages_to_include]
                    else:
                        # If shot_size is -1, use all messages
                        old_messages = messages

            variables = (prompt_details["variables"] if prompt_details.get("variables") else {})
            default_variables = convert_variables_data(variables)
            variables = merge_default_and_provided_variables(interaction_request, default_variables)

            result = await self.get_summarized_content(prompt_id=user_prompt_id,session_id=session_id)

            # Initialize summarized_content
            summarized_content = ""
            if result["status"] == "success":
                summarized_content = result["summarized_content"]
            

            new_user_message = interaction_request["user_message"]
            if prompt_details["ai_platform"] == "claude":
                new_user_message = self.modify_new_user_message_for_claude(new_user_message)

            messages_collection = self.update_messages_collection(prompt_details["ai_platform"], system_message, old_messages)

            # if session_type == "new_session":
            #     messages_collection.extend(
            #         [
            #             {
            #                 "role": "user",
            #                 "content": new_user_message,
            #             }
            #         ]
            #     )

            # elif session_type == "existing_session":
            #     content = [
            #         {
            #             "type": "text",
            #             "text": f"Summary of previous AI Interaction: {summarized_content}\n\nNew user message that needs to be responded is in next message:",
                        
            #         }
            #     ]

            #     for message in new_user_message:
            #         if isinstance(message, dict) and message.get("type") == "file":
            #             content.append(message)
            #         else:
            #             content.append(message)

            #     if prompt_details["ai_platform"] == "gemini":
            #         messages_collection.extend(
            #             [
            #                 {
            #                     "role": "user",
            #                     "content": new_user_message,
            #                 }
            #             ]
            #         )

            #     else:

            #         messages_collection.extend(
            #             [
            #                 {
            #                     "role": "user",
            #                     "content": content,
            #                 }
            #             ]
            #         )


            # Check format: is it already a list of role-content messages?
            is_role_based = (
                isinstance(new_user_message, list)
                and isinstance(new_user_message[0], dict)
                and "role" in new_user_message[0]
                and "content" in new_user_message[0]
            )

            if session_type == "new_session":
                if is_role_based:
                    messages_collection.extend(new_user_message)
                else:
                    messages_collection.append({
                        "role": "user",
                        "content": new_user_message
                    })

            elif session_type == "existing_session":
                if is_role_based:
                    first_msg = new_user_message[0]

                    if first_msg.get("role") == "user":
                        summary_block = {
                            "type": "text",
                            "text": f"Summary of previous AI Interaction: {summarized_content}\n\nNew user message that needs to be responded is in next message:"
                        }

                        content = first_msg["content"]

                        if isinstance(content, list):
                            content.insert(0, summary_block)

                        messages_collection.extend(new_user_message)

                    else:
                        messages_collection.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Summary of previous AI Interaction: {summarized_content}\n\nNew user message that needs to be responded is in next message:"
                                }
                            ]
                        })
                        messages_collection.extend(new_user_message)

                   
                else:
                    # Old format: include summary and then the content as new user message
                    content = [
                        {
                            "type": "text",
                            "text": f"Summary of previous AI Interaction: {summarized_content}\n\nNew user message that needs to be responded is in next message:",
                        }
                    ]

                    for message in new_user_message:
                        content.append(message)  # handles both file and text types

                    # if prompt_details["ai_platform"] == "gemini":
                    #     messages_collection.append({
                    #         "role": "user",
                    #         "content": new_user_message
                    #     })
                    # else:
                    messages_collection.append({
                            "role": "user",
                            "content": content
                    })


            if prompt_details["ai_platform"] == "custom":
                platform_key = ""
            else:
                platform_key = prompt_details["platform_config"]["platformKey"]
            system_message = self.replace_placeholders(system_message, variables)
            messages_collection = self.replace_placeholders(messages_collection, variables)

            response = await self._make_ai_platform_request(
                platform_name=prompt_details["ai_platform"],
                prompt_details=prompt_details,
                messages=messages_collection,
                system_message=system_message,
                platform_key=platform_key,
                variables=variables,
                prompt_id=user_prompt_id,
                base_url= interaction_request.get("base_url",None),
                format=interaction_request.get("format",None),
                credentials=interaction_request.get("credentials",None),
                grounding=interaction_request.get("grounding",None)
            )
            
            # Get both response and summary in one call
            if prompt_details["ai_platform"] == "claude":

                response1 = response["response"]
                input_tokens0 = response["input_tokens"]
                output_tokens0 = response["output_tokens"]
                total_tokens0 = response["total_tokens"]

                
                # Generate summary using the same messages plus the new response
                summary_messages = messages_collection.copy()
                summary_messages.append(
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": response1}],
                    }
                )
                summary_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": PROMPT_TO_GENERATE_SUMMARIZED_CONTENT,
                            }
                        ],
                    }
                )

                # Add summary request to the same API call
                summary_response = await self._make_ai_platform_request(
                    platform_name=prompt_details["ai_platform"],
                    prompt_details=prompt_details,
                    messages=summary_messages,
                    system_message=system_message,
                    platform_key=platform_key,
                    variables=variables,
                    prompt_id=user_prompt_id,
                    base_url= interaction_request.get("base_url",None),
                    format=interaction_request.get("format",None),
                    credentials=interaction_request.get("credentials",None),
                    grounding=interaction_request.get("grounding",None)
                )

                new_summarized_content = summary_response["response"]
                input_tokens1 = summary_response["input_tokens"]
                output_tokens1 = summary_response["output_tokens"]
                total_tokens1 = summary_response["total_tokens"]
                    
                ai_response = {"type": "text", "text": response1}
            else:
                response1 = response["response"]
                input_tokens0 = response["input_tokens"]
                output_tokens0 = response["output_tokens"]
                total_tokens0 = response["total_tokens"]
                
                # Generate summary using the same messages plus the new response
                summary_messages = messages_collection.copy()
                summary_messages.append(
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": f"{response1}"}],
                    }
                )
                summary_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": PROMPT_TO_GENERATE_SUMMARIZED_CONTENT,
                            }
                        ],
                    }
                )

                # Add summary request to the same API call
                summary_response = await self._make_ai_platform_request(
                    platform_name=prompt_details["ai_platform"],
                    prompt_details=prompt_details,
                    messages=summary_messages,
                    system_message=system_message,
                    platform_key=platform_key,
                    variables=variables,
                    prompt_id=user_prompt_id,
                )
                new_summarized_content = summary_response["response"]
                input_tokens1 = summary_response["input_tokens"]
                output_tokens1 = summary_response["output_tokens"]
                total_tokens1 = summary_response["total_tokens"]
                ai_response = {"type": "text", "text": response1}

            current_time = datetime.now().isoformat()
            # new_messages = [
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "user",
            #         "content": interaction_request["user_message"],
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            #     {
            #         "id": str(uuid.uuid4()),
            #         "role": "assistant",
            #         "content": ai_response,
            #         "requestFrom": interaction_request.get("request_from", "sdk"),
            #         "initiatedAt": current_time,
            #     },
            # ]

            user_messages = interaction_request["user_message"]
            request_from = interaction_request.get("request_from", "sdk")

            # Determine if role-based format or flat content list
            if isinstance(user_messages, list) and all("role" in msg and "content" in msg for msg in user_messages):
                # It's a list of role-based messages — use as is
                new_messages = []

                for msg in user_messages:
                    new_messages.append({
                        "id": str(uuid.uuid4()),
                        "role": msg["role"],
                        "content": msg["content"],
                        "requestFrom": request_from,
                        "initiatedAt": current_time,
                    })

            else:
                
                new_messages = [{
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": user_messages,
                    "requestFrom": request_from,
                    "initiatedAt": current_time,
                }]

            # Add assistant reply as the last message
            new_messages.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": ai_response,
                "requestFrom": request_from,
                "initiatedAt": current_time,
            })

            # Save to cache in background
            interaction_data = {
                "messages": new_messages,
                "lastResponseAt": current_time,
                "memory_type": "summarizedMemory",
                "summarized_content": new_summarized_content,
            }
               
            # Create background task for caching
            asyncio.create_task(
                self._background_cache_save(cache_key, interaction_data)
            )

            if self.is_logging:
               
                input_tokens = input_tokens0 + input_tokens1
                output_tokens = output_tokens0 + output_tokens1
                total_tokens = total_tokens0 + total_tokens1
               
                endpoint = f"/save_bypass_logs/{prompt_details['version_id']}"
                payload = {
                    "user_message": interaction_request["user_message"],
                    "ai_response": {"type": "text", "text": f"{response1}"},
                    "session_id": session_id,
                    "memory_type": "summarizedMemory",
                    "window_size": 0,
                    "summarized_content": f"{new_summarized_content}",
                    "request_from": "python_sdk",
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "platform":prompt_details["ai_platform"],
                    "model":prompt_details["model"]
                }

                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                    endpoint,
                    method="POST",
                    json=payload,
                    timeout=30, # Add reasonable timeout
                )
               
            if self.is_logging is False:

                input_tokens = input_tokens0 + input_tokens1
                output_tokens = output_tokens0 + output_tokens1
                total_tokens = total_tokens0 + total_tokens1

                endpoint = "/save_transaction_logs"
                payload = { 
                    "promptId":user_prompt_id,
                    "versionId":prompt_details["version_id"],
                    "platform":prompt_details["ai_platform"],
                    "model":prompt_details["model"],
                    "input_tokens":input_tokens,
                    "output_tokens":output_tokens,
                    "transaction_at":"python_sdk" ,  
                    "session_id":session_id
                }

                if interaction_request["tag"] is not None:
                    payload["tag"] = interaction_request["tag"]

                response = await self.request(
                      endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )

            price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : prompt_details["ai_platform"],
                        "model" : prompt_details["model"],
                        "input_tokens" : input_tokens,
                        "output_tokens" : output_tokens
                        }
                )
            
            return {"response": response1, 
                    "session_id": session_id,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "price": price_data["data"],
                    "promptId":user_prompt_id
                    }

        except Exception as e:
            error_message = (
                f"An error occurred while processing AI interaction: {str(e)}"
            )
            logger.error("\nERROR OCCURRED:")
            logger.error(error_message)
            logger.error("Cache state at error:")
            raise ValueError(error_message)


    async def _background_cache_save(self, cache_key: str, interaction_data: Dict):
        """Background task to save cache data with error handling"""
        try:
            self._save_to_persistent_cache(cache_key, interaction_data)
        except Exception as e:
            logger.error(f"Error saving to cache in background: {str(e)}")


    async def _fetch_and_cache_prompt_details(
        self, prompt_id: str, session_id: str, version: Optional[str] = None
    ) -> Dict:
        """
        Fetch prompt details from PromptStudio

        Args:
            prompt_id: ID of the prompt
            session_id: Session ID
            version: Optional version number (if None, will use null in request)

        Returns:
            Dictionary containing prompt details
        """
        try:
            # Clean the prompt_id
            prompt_id = prompt_id.strip()

            # Prepare request body with proper version format and stringify
            request_body = json.dumps({"version": float(version) if version else None})

            # Make request to version_data endpoint with proper headers
            response = await self._request(
                f"/fetch/prompt/version_data/{prompt_id}",
                method="POST",
                data=request_body,  # Use data instead of json for stringified content
            )
            
            if not response.get("data") or not response["data"].get("result"):
                logger.error(f"Invalid response format for prompt_id: {prompt_id}")
                raise ValueError("Invalid response format from API")

            # Extract data from response
            result = response["data"]["result"]
            prompt = result["prompt"]
            version_id = prompt["_id"]
            ai_platform = prompt["aiPlatform"]
            messages = result["messages"]
            platform_config = result.get("platformConfig", {})
            variables = messages.get("variable", {})
            

            # Extract and format the prompt details
            prompt_details = {
                "ai_platform": ai_platform["platform"],
                "model": ai_platform["model"],
                "system_prompt": messages.get("systemMessage", ""),
                "temperature": ai_platform["temp"],
                "max_tokens": ai_platform["max_tokens"],
                "messages": messages.get("messages", []),
                "top_p": ai_platform["top_p"],
                "frequency_penalty": ai_platform["frequency_penalty"],
                "presence_penalty": ai_platform["presence_penalty"],
                "response_format": ai_platform["response_format"],
                "version": prompt["version"],
                "platform_config": platform_config,  # Include platform config if needed
                "variables": variables,
                "version_id": version_id,
                "prompt_id": result["promptId"],
                "grounding":ai_platform.get("grounding",False)
            }

            # Cache the prompt details
            cache_key = f"{prompt_id}_{session_id}"
            CacheManager.set_prompt_details(cache_key, prompt_details)

            return prompt_details

        except Exception as e:
            logger.error(f"Error in _fetch_and_cache_prompt_details: {str(e)}")
            raise

    def modify_messages_for_openai(self, messages):
        """Convert file types to image_url format for OpenAI"""
        modified_messages = []
        supported_extensions = [".png", ".jpeg", ".jpg", ".webp", ".jfif"]

        for message in messages:
            modified_content = []
            for content in message.get("content", []):
                if content.get("type") == "file" and content.get("file_url", {}).get(
                    "url"
                ):
                    image_url = content["file_url"]["url"]
                    _, extension = os.path.splitext(image_url)
                    if extension.lower() not in supported_extensions:
                        raise ValueError(
                            f"Unsupported image extension: {extension}. "
                            "We currently support PNG (.png), JPEG (.jpeg and .jpg), "
                            "WEBP (.webp), and JFIF (.jfif)"
                        )
                    modified_content.append(
                        {"type": "image_url", "image_url": {"url": image_url}}
                    )
                else:
                    modified_content.append(content)

            modified_messages.append(
                {"role": message["role"], "content": modified_content}
            )
        return modified_messages
    

    async def _make_openai_request(self, prompt_details: Dict, payload: Dict, platform_key :str, prompt_id: str) -> Dict:
        """Make a direct request to OpenAI"""
        # Get OpenAI API key from environment when in bypass mode
        openai_api_key = platform_key
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY  variable is required , bypass mode is true. which is set while publishing the prompt"
            )

        # Extract messages from payload
        messages = payload.get("user_message", [])
        
        # Process each message and handle file types
        messages = self.modify_messages_for_openai(messages)
        

        try:
            response = openai_interaction(
                secret_key=openai_api_key,  
                model=prompt_details["model"],
                messages=messages,
                temperature=prompt_details.get("temp", 0.7),
                max_tokens=prompt_details["max_tokens"],
                top_p=prompt_details.get("top_p", 0.5),
                frequency_penalty=prompt_details.get("frequency_penalty", 0.7),
                presence_penalty=prompt_details.get("presence_penalty", 0.3),
                response_format=prompt_details.get("response_format"),
                timeout=self.timeout
            )
            
            if prompt_details.get("is_session_enabled") is True:
                return response

            else:
                price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : "openai",
                        "model" : prompt_details["model"],
                        "input_tokens" : response["input_tokens"],
                        "output_tokens" : response["output_tokens"]
                        }
                )

                return {
                        "message": "AI interactions log saved successfully",
                        "data": {
                            "message": "AI interaction saved successfully ",
                            "user_prompt_id": prompt_id,
                            "response": response["response"],
                            "input_tokens": response["input_tokens"],
                            "output_tokens": response["output_tokens"],
                            "total_tokens": response["total_tokens"],
                            "price": price_data["data"],
                            "session_id": None,
                        },
                    }
        except Exception as e:
            logger.error(f"Error making OpenAI request: {str(e)}")
            raise

    
    async def claude_interaction_chat_with_prompt(
        self,
        secret_key,
        model,
        max_tokens,
        temperature,
        messages,
        system_message,
        is_session_enabled,
        timeout
    ):
        messages = remove_id_from_messages(messages)
        messages = self.modify_messages_for_claude(messages)
        client = anthropic.Anthropic(api_key=secret_key,
                                    timeout=float(timeout)
                                    )

        try:
            if system_message and system_message.strip():
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages,
                    system=system_message,  # Pass system message as a separate parameter
                )
            else:
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages,
                )
            if not response.content:
                logger.warning(
                    "Empty response content from Claude API. This may occur if the API returned an empty array."
                )
                return {
                    "response": "No content was generated. Please try again or rephrase your query."
                }
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
           
            assistant_reply = response.content[0].text
            ai_response = {
                "role": "assistant",
                "content": [{"type": "text", "text": assistant_reply}],
            }
            return { "response": assistant_reply, 
                    "input_tokens": input_tokens, 
                    "output_tokens": output_tokens, 
                    "total_tokens": total_tokens }

        except Exception as e:
            raise ValueError(f"API interaction error: {str(e)}")


    async def _no_cache_direct_ai_request(
        self,
        prompt_id: str,
        user_message: List[Dict[str, Union[str, Dict[str, str]]]],
        variables: Dict[str, str],
        version: Optional[int] = None,
        shot: Optional[int] = -1,
        memory_type: Optional[str] = None,
        tag: Optional[Dict] = None,
        base_url : Optional[str] = None,
        format: Optional[str] = None,
        credentials: Optional[dict] = None,
        grounding:Optional[bool] = None
    ) -> Dict:
        """Handle direct AI platform requests without caching"""
        # return await self._direct_ai_request(prompt_id, session_id, payload)
        try:
            # Clean the prompt_id
            prompt_id = prompt_id.strip()
            requested_variables = variables
            # Prepare request body with proper version format and stringify
            request_body = json.dumps({"version": float(version) if version else None})
            # Make request to version_data endpoint with proper headers
            response = await self._request(
                f"/fetch/prompt/version_data/{prompt_id}",
                method="POST",
                data=request_body,  # Use data instead of json for stringified content
            )
            if not response.get("data") or not response["data"].get("result"):
                raise ValueError("Invalid response format from API")
            
            # Extract data from response

            result = response["data"]["result"]
            prompt_id = result["promptId"]
            prompt = result["prompt"]
            version_id = prompt["_id"]
            ai_platform = prompt["aiPlatform"]
            system_message = self.clean_system_message(result["messages"]["systemMessage"])
            messages = result["messages"]["messages"]
            variables = result["messages"].get("variable", {})
         
            # Add shot-based message slicing
            shot_size = shot if shot is not None else -1  # Use provided shot or default to -1
            if shot_size == 0:
                messages = []  # Return empty messages list if shot is 0
            elif messages:  # Only process if messages exist and shot isn't 0
                if shot_size > 0:
                    # Calculate number of messages to include (2 messages per shot)
                    messages_to_include = shot_size * 2
                    messages = messages[:messages_to_include]
                # If shot_size is -1, use all messages (default behavior)

            if ai_platform["platform"] == "openai":
                if system_message:
                    messages.insert(0,{"role": "system", "content": [{"type": "text", "text": system_message}]})
                else:
                    messages.insert(0,{"role": "system", "content": [{"type": "text", "text": ""}]})

            if ai_platform["platform"] == "groq" or ai_platform["platform"] == "grok" or ai_platform["platform"] == "custom" :
                messages.insert(0,{"role": "system", "content": system_message})

            
            # messages.extend([{"role": "user", "content": user_message}])
            if user_message and isinstance(user_message[0], dict) and "role" in user_message[0] and "content" in user_message[0]:
            # Already in new format (list of role-content dicts)
                messages.extend(user_message)
            else:
            # Old format — wrap it in a role-content dict
                messages.append({"role": "user", "content": user_message})


            platform_config = result.get("platformConfig", {})
            
            # Extract and format the prompt details
            prompt_details = {
                "ai_platform": ai_platform["platform"],
                "model": ai_platform["model"],
                "system_prompt": system_message,
                "temperature": ai_platform["temp"],
                "max_tokens": ai_platform["max_tokens"],
                "messages": messages,  # Use the extended messages
                "top_p": ai_platform["top_p"],
                "frequency_penalty": ai_platform["frequency_penalty"],
                "presence_penalty": ai_platform["presence_penalty"],
                "response_format": ai_platform["response_format"],
                "version": prompt["version"],
                "platform_config": platform_config,  # Include platform config if needed
                "variables": variables,
                "is_session_enabled": False,
                "grounding":ai_platform.get("grounding",False)
            }
            def_variables = prompt_details["variables"] if prompt_details else []
            default_variables = {}
            if (
                def_variables
                and (isinstance(def_variables, list) and len(def_variables) > 0)
                or (isinstance(def_variables, dict) and def_variables)
            ):
                default_variables = self.convert_data(def_variables)


            # Determine which variables to use based on the conditions
            if not requested_variables:
                # Condition 1: No variables given in interaction_request
                variables = default_variables
            else:
                # Condition 2 and 3: Check how many variables are provided
                provided_variables = requested_variables
                variables = {**default_variables}  # Start with default variables
                # Count how many variables are in default_variables
                default_keys = set(default_variables.keys())
                provided_keys = set(provided_variables.keys())
                if provided_keys.issubset(default_keys):
                    # Condition 3: All provided variables are in default_variables
                    variables = provided_variables
                else:
                    # Condition 2: Some variables are provided
                    for key in provided_keys:
                        if key in default_keys:
                            variables[key] = provided_variables[key]
                    # Add remaining default variables
                    for key in default_keys:
                        if key not in provided_keys:
                            variables[key] = default_variables[key]
            
            system_message = self.replace_placeholders(system_message, variables)
            messages = self.replace_placeholders(messages, variables)

            if ai_platform["platform"] == "custom":
                platform_key = ""
            else:
                platform_key= platform_config["platformKey"]

            platform_response = await self._make_ai_platform_request(
                platform_name=ai_platform["platform"],  # Use platform string directly
                prompt_details=prompt_details,
                messages=messages,
                system_message=system_message,
                platform_key=platform_key,
                variables=variables,
                prompt_id=prompt_id,
                base_url=base_url,
                format=format,
                credentials=credentials,
                grounding=grounding
            )
            
            if self.is_logging:
            
                endpoint = f"/save_bypass_logs/{version_id}"
                payload = {
                    "user_message": user_message,
                    "ai_response": {"type": "text", "text": f"{platform_response['data']['response']}"},
                    "session_id": "",
                    "memory_type": memory_type,
                    "window_size": 0,
                    "summarized_content": "",
                    "request_from": "python_sdk",
                    "input_tokens": platform_response["data"]["input_tokens"],
                    "output_tokens": platform_response["data"]["output_tokens"],
                    "platform":prompt_details["ai_platform"],
                    "model":prompt_details["model"]
                    
                }
                if tag is not None:
                    payload["tag"] = tag
                
                response = await self.request(
                    endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )
              

            if self.is_logging is False:

                endpoint = "/save_transaction_logs"
                payload = { 
                    "promptId":prompt_id,
                    "versionId":version_id,
                    "platform":prompt_details["ai_platform"],
                    "model":prompt_details["model"],
                    "input_tokens":platform_response["data"]["input_tokens"],
                    "output_tokens":platform_response["data"]["output_tokens"],
                    "transaction_at":"python_sdk"
                }

                if tag is not None:
                    payload["tag"] = tag

                response = await self.request(
                      endpoint,
                    method="POST",
                    json=payload,
                    timeout=30,  # Add reasonable timeout
                )

            return platform_response    
        except Exception as e:
            logger.error(f"Error in _no_cache_direct_ai_request: {str(e)}")
            raise

  
    async def _get_existing_summarized_content(
        self, interaction_history: Dict, session_id: str, version: str
    ) -> str:
        """Get existing summarized content from interaction history"""
        if (
            interaction_history
            and interaction_history.get("memory_type") == "summarizedMemory"
            and "summarized_content" in interaction_history
        ):
            return interaction_history["summarized_content"]
        return ""
    

    async def get_prompt_data(self, prompt_id: str,version: Optional[float] = None):
        """
        Fetch and return detailed prompt information for the given prompt_id.

        Args:
            prompt_id (str): The ID of the prompt to fetch.

        Returns:
            dict: A dictionary containing the prompt details.
        """
        
        request_body = json.dumps({"version": float(version) if version else None})

        # Make request to version_data endpoint with proper headers
        response = await self._request(
            f"/fetch/prompt/version_data/{prompt_id}",
            method="POST",
            data=request_body,  # Use data instead of json for stringified content
        )

        if not response.get("data") or not response["data"].get("result"):
            logger.error(f"Invalid response format for prompt_id: {prompt_id}")
            raise ValueError("Invalid response format from API")

        # Extract data from response
        result = response["data"]["result"]
        prompt = result["prompt"]
        version_id = prompt["_id"]
        ai_platform = prompt["aiPlatform"]
        messages = result["messages"]
        platform_config = result.get("platformConfig", {})
        variables = messages.get("variable", {})

        # Extract and format the prompt details
        prompt_details = {
            "ai_platform": ai_platform["platform"],
            "model": ai_platform["model"],
            "system_prompt": messages.get("systemMessage", ""),
            "temperature": ai_platform["temp"],
            "max_tokens": ai_platform["max_tokens"],
            "messages": messages.get("messages", []),
            "top_p": ai_platform["top_p"],
            "frequency_penalty": ai_platform["frequency_penalty"],
            "presence_penalty": ai_platform["presence_penalty"],
            "response_format": ai_platform["response_format"],
            "version": prompt["version"],
            # "platform_config": platform_config,
            "variables": variables,
            "version_id": version_id,
            "prompt_id": result["promptId"],
            "grounding": ai_platform.get("grounding", False)
        }

        return prompt_details



    async def get_session(self, session_id: str) -> Dict:
        """
        Get session details either from cache or API based on bypass flag.
        
        Args:
            session_id (str): The session ID to fetch details for
            
        Returns:
            Dict: Session details either from cache or API
        """
        try:
            if self.bypass:
                cached_interactions = InteractionCacheManager.get_all_interactions_by_session(session_id)
                
                if not cached_interactions:
                    return {
                        "message": "No session data found",
                        "data": {
                            "messages": []
                        }
                    }
                    
                return cached_interactions
                
            else:
                endpoint = f"/get_session/{session_id}"
                
                response = await self.request(
                    endpoint,
                    method="GET",
                    timeout=30
                )
                
                return response
                    
        except Exception as e:
            return {
                "message": f"Error retrieving session data: {str(e)}",
                "data": {
                    "messages": []
                }
            }


    async def chat_with_prompt(
        self,
        prompt_id: str,
        user_message: List[Dict[str, Union[str, Dict[str, str]]]],
        memory_type: str,
        window_size: int,
        session_id: str,
        variables: Dict[str, str],
        version: Optional[int] = None,
        is_session_enabled: Optional[bool] = True,
        shot: Optional[int] = -1,
        tag: Optional[Dict] = None,
        base_url: Optional[str] = None,
        format: Optional[str] = None,
        credentials: Optional[dict] = None,
        grounding: Optional[bool] =None,
    ) -> Dict[str, str]:
        """
        Chat with a specific prompt

        Args:
            prompt_id: ID of the prompt
            user_message: List of message dictionaries
            memory_type: Type of memory ('fullMemory', 'windowMemory', or 'summarizedMemory')
            window_size: Size of the memory window
            session_id: Session identifier
            variables: Dictionary of variables
            version: Optional version number

        Returns:
            Dictionary containing the response
        """
        if memory_type not in self._supported_memory_types:
            raise ValueError(
                f"Unsupported memory type: {memory_type}. Supported types are: {', '.join(self._supported_memory_types)}"
            )
        
        if self.bypass is False:
            # Check if user_message is a role-based format (which is NOT allowed here)
            if isinstance(user_message, list) and all(
                isinstance(msg, dict) and "role" in msg and "content" in msg for msg in user_message
            ):
                raise ValueError(
                    "Role-based user_message format is not allowed when 'bypass' is False. "
                    "Please provide a plain content list, e.g., [{'type': 'text', 'text': 'hello'}]."
                )

        payload = {
            "user_message": user_message,
            "memory_type": memory_type,
            "window_size": window_size,
            "session_id": session_id,
            "env": self.env,
            "request_from": "python_sdk",
            "variables": variables,
            "version": version,
            "shot": shot,
            "is_session_enabled": is_session_enabled,
            "tag":tag  
        }
     
        no_bypass_payload = {
            "user_message": user_message,
            "memory_type": memory_type,
            "window_size": window_size,
            "session_id": session_id,
            "variables": variables,
            "request_from": "python_sdk",
            "shot": shot,
            "tag": tag,
            "timeout":self.timeout
        }

        if base_url and format is not None:
            payload["base_url"] = base_url
            no_bypass_payload["base_url"] = base_url
            payload["format"] = format
            no_bypass_payload["format"] = format

        if credentials is not None:
            payload["credentials"] = credentials
            no_bypass_payload["credentials"] = credentials

        if version is not None:
            payload["version"] = version
            no_bypass_payload["version"] = version

        if grounding is not None:
            payload["grounding"] = grounding
            no_bypass_payload["grounding"] = grounding

        try:
            if self.bypass:

                if is_session_enabled is False:
                    return await self._no_cache_direct_ai_request(
                        prompt_id, user_message, variables, version, shot,
                        memory_type, tag , base_url , format , credentials , grounding
                    )
                if memory_type == "summarizedMemory":
                    response = await self.summarizedmemory_save_log_ai_interaction_prompt(
                        prompt_id, payload
                    )

                elif memory_type == "windowMemory":
                    response = await self.windowmemory_save_log_ai_interaction_prompt(
                        prompt_id, payload
                    )
                
                elif memory_type == "fullMemory":
                    response = await self.fullmemory_save_log_ai_interaction_prompt(
                        prompt_id, payload
                    )
                
                else:
                    raise ValueError(
                        f"Invalid memory type: {memory_type}. Supported types are: {', '.join(self._supported_memory_types)}"
                    )

            else:
                response = await self._request(
                    f"/chat_with_prompt_version/{prompt_id}",
                    method="POST",
                    json=no_bypass_payload,
                )

            if self.bypass:
                # session_details = await self.get_session(session_id=session_id)
                return {
                    "message": "AI interactions log saved successfully",
                    "data": {
                            "message": f"AI interaction saved successfully for memory type: {memory_type}",
                            "user_prompt_id": response["promptId"],
                            "response": response["response"],
                            "input_tokens": response["input_tokens"],
                            "output_tokens": response["output_tokens"],
                            "total_tokens": response["total_tokens"],
                            "price": response["price"],
                            "session_id": response["session_id"]   
                            # "session_details":session_details
                    },
                }
            else:
                return response
        except Exception as e:
            logger.error(f"Error in chat_with_prompt: {str(e)}")
            raise


    async def _make_ai_platform_request(
        self,
        platform_name: str,
        prompt_details: Dict,
        messages: List[Dict],
        system_message: str,
        platform_key: str,
        variables: Dict,
        prompt_id: str,
        base_url :Optional[str] = None,
        format: Optional[str] = None,
        credentials:Optional[dict] =None,
        grounding:Optional[bool] = None
    ) -> Dict:
        """
        Make request to the appropriate AI platform

        Args:
            platform_name: Name of the AI platform (openai, anthropic, etc.)
            prompt_details: Dictionary containing prompt configuration
            messages: List of messages to send
            system_message: System message to use

        Returns:
            Dictionary containing the response
        """
        
        if system_message:
            system_message = self.clean_system_message(system_message)

        try:
            if platform_name.lower() == "openai":
                return await self._make_openai_request(prompt_details, {"user_message": messages}, platform_key, prompt_id)
            
            elif platform_name.lower() == "claude":
                if not platform_key:
                    raise ValueError(
                        "CLAUDE_API_KEY  is required when using Claude, which is set while publishing the prompt. bypass mode is true"
                    )
                response = await self.claude_interaction_chat_with_prompt(
                    secret_key=platform_key,
                    model=prompt_details["model"],
                    max_tokens=prompt_details["max_tokens"],
                    temperature=prompt_details["temperature"],
                    messages=messages,
                    system_message=system_message,
                    is_session_enabled=prompt_details.get("is_session_enabled"),
                    timeout=self.timeout
                )
                
                if prompt_details.get("is_session_enabled") is True:
                    return response
                
                else:
                    price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : "claude",
                        "model" : prompt_details["model"],
                        "input_tokens" : response["input_tokens"],
                        "output_tokens" : response["output_tokens"]
                        }
                    )
                    
                    return {
                        "message": "AI interactions log saved successfully",
                        "data": {
                            "message": "AI interaction saved successfully ",
                            "user_prompt_id": prompt_id,
                            "response": response["response"],
                            "input_tokens": response["input_tokens"],
                            "output_tokens": response["output_tokens"],
                            "total_tokens": response["total_tokens"],
                            "price": price_data["data"],
                            "session_id": None,
                        },
                    }
            
            elif platform_name.lower() == "gemini":
         
                if grounding is None:
                    grounding=prompt_details.get("grounding")
                 
                if not platform_key:
                    raise ValueError(
                        "GEMINI_API_KEY  is required when using Gemini, which is set while publishing the prompt. bypass mode is true"
                    )

                gemini_response = gemini_interaction_chat_with_prompt(
                    secret_key=platform_key,  
                    model=prompt_details["model"],
                    messages=messages,
                    system_message=system_message,
                    temperature=prompt_details.get("temp", 0.7),
                    max_output_tokens=prompt_details.get("max_tokens", 1000),
                    top_p=prompt_details.get("top_p", 0.8),
                    top_k=prompt_details.get("top_k", 40),
                    response_format=prompt_details.get("response_format"),
                    timeout=self.timeout,
                    grounding=grounding
                )
                
                # return gemini_response
                if prompt_details.get("is_session_enabled") is True:
                    return gemini_response
                
                else:
                    price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : "gemini",
                        "model" : prompt_details["model"],
                        "input_tokens" : gemini_response["input_tokens"],
                        "output_tokens" : gemini_response["output_tokens"]
                        }
                    )
    
                    return {
                        "message": "AI interactions log saved successfully",
                        "data": {
                                "message": "AI interaction saved successfully for memory type: full memory",
                                "user_prompt_id": prompt_id,
                                "response": gemini_response["response"],
                                "input_tokens": gemini_response["input_tokens"],
                                "output_tokens": gemini_response["output_tokens"],
                                "total_tokens": gemini_response["total_tokens"],
                                "price": price_data["data"],
                                "session_id": None,
                        },
                    }
            elif platform_name.lower() == "groq" or platform_name.lower() == "grok" or platform_name.lower() == "custom":
                response = openai_supported_models_interaction(
                secret_key=platform_key,
                model=prompt_details["model"],
                messages=messages,
                temperature=prompt_details["temperature"],
                max_tokens=prompt_details["max_tokens"],
                top_p=prompt_details["top_p"],
                frequency_penalty=prompt_details["frequency_penalty"],
                presence_penalty=prompt_details["presence_penalty"],
                response_format=prompt_details["response_format"],
                platform= platform_name,
                timeout=self.timeout,
                base_url=base_url,
                format=format,
                credentials=credentials,
                platform_config=prompt_details["platform_config"]
            )
                if prompt_details.get("is_session_enabled"):
                    return response

                else:
                    price_data = await self.request(
                    f"/calculate_price",
                    method="POST",
                    json= {"platform" : platform_name,
                        "model" : prompt_details["model"],
                        "input_tokens" : response["input_tokens"],
                        "output_tokens" : response["output_tokens"]
                        }
                    )

                    return {
                        "message": "AI interactions log saved successfully",
                        "data": {
                            "message": "AI interaction saved successfully ",
                            "user_prompt_id": prompt_id,
                            "response": response["response"],
                            "input_tokens": response["input_tokens"],
                            "output_tokens": response["output_tokens"],
                            "total_tokens": response["total_tokens"],
                            "price": price_data["data"],
                            "session_id": None,
                        },
                    }
            else:
                error_msg = f"Unsupported AI platform: {platform_name}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            logger.error(f"Error in _make_ai_platform_request: {str(e)}")
            raise


    def _fetch_session_id(self, interaction_request: Dict) -> Tuple[str, str]:
        """
        Determine session type and get session ID from interaction request

        Args:
            interaction_request: Dictionary containing the interaction request

        Returns:
            Tuple containing (session_type, session_id)
        """
        session_id = interaction_request.get("session_id", "")
        if not session_id:
            new_session = str(ObjectId())
            return "new_session", new_session
        else:
            return "existing_session", session_id


    async def get_summarized_content(
        self, prompt_id: str, session_id: str
    ) -> Dict[str, Any]:
        """
        Fetch summarized content for a specific prompt session.

        Args:
            prompt_id: ID of the prompt
            session_id: Session identifier

        Returns:
            Dictionary containing the summarized content and status
        """
        try:

            # Generate cache key
            cache_key = f"{prompt_id}_{session_id}"

            # Try to load from persistent cache
            cached_data = self._load_from_persistent_cache(cache_key)

            if cached_data and "summarized_content" in cached_data:
                return {
                    "status": "success",
                    "summarized_content": cached_data["summarized_content"],
                    "memory_type": cached_data.get("memory_type", "summarizedMemory"),
                    "session_id": session_id,
                }

            return {
                "status": "not_found",
                "message": "No summarized content found for this session",
                "session_id": session_id,
            }

        except Exception as e:
            error_message = f"Error fetching summarized content: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "session_id": session_id,
            }


    def clean_system_message(self, system_message):
        """Clean the system message by removing comment blocks."""
        if not system_message:
            return None
        in_comment_block = False
        cleaned_lines = []
        for line in system_message.split("\n"):
            stripped_line = line.strip()
            # Check for comment block start
            if stripped_line.startswith("```comment"):
                in_comment_block = True
                continue
            # Check for comment block end
            if stripped_line == "```" and in_comment_block:
                in_comment_block = False
                continue
            # Add line only if we're not in a comment block
            if not in_comment_block:
                cleaned_lines.append(line.rstrip())
        return "\n".join(cleaned_lines)


    def clear_cache(
        self, session_id: Optional[str] = None, prompt_id: Optional[str] = None
    ):
        """
        Clear cache memory from both persistent storage and local cache managers.
        """
        try:
            cleared_items = []

            if session_id and prompt_id:
                # Clear specific session and prompt from persistent cache
                cache_key = f"{prompt_id}_{session_id}"
                prompt_details_key = f"{cache_key}_prompt_details"

                # Clear regular cache file
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                    cleared_items.append("persistent cache")

                # Clear prompt details cache file
                details_cache_path = self._get_cache_path(prompt_details_key)
                if details_cache_path.exists():
                    details_cache_path.unlink()
                    cleared_items.append("persistent prompt details cache")

                # Clear from CacheManager
                CacheManager.delete_prompt_details(cache_key)
                cleared_items.append("prompt cache")

                # Clear from InteractionCacheManager
                InteractionCacheManager.delete_interaction(prompt_id, session_id)
                cleared_items.append("interaction cache")

                return {
                    "status": "success",
                    "message": f"Cache cleared for session {session_id} and prompt {prompt_id}",
                    "cleared": cleared_items,
                }

        except Exception as e:
            error_message = f"Error clearing cache: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "cleared": cleared_items,
            }


def convert_object_ids(data):
    if isinstance(data, dict):
        return {k: convert_object_ids(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_object_ids(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to ISO format string
    else:
        return data


def openai_interaction(
    secret_key,
    model,
    messages,
    temperature,
    max_tokens,
    top_p,
    frequency_penalty,
    presence_penalty,
    response_format,
    timeout
):
    """Make a request to OpenAI API"""
    # Set the OpenAI API key
    client = OpenAI(api_key=secret_key)
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            response_format=response_format,
            timeout=timeout,
        )
        
        # Extract token usage from response
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        # Get the response content using the new API format
        assistant_reply = response.choices[0].message.content.strip()

        return {
            "response": assistant_reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise


def convert_messages_to_contents(messages, client):
    contents = []
    for msg in messages:
        parts = []
        for c in msg["content"]:
            if c["type"] == "text":
                parts.append(types.Part.from_text(text=c["text"]))
            else:
                file_obj = upload_file_to_gemini(c["file_url"]["url"], client)
                parts.append(
                    types.Part.from_uri(
                        file_uri=file_obj.uri,
                        mime_type=file_obj.mime_type
                    )
                )
        
        # Replace "assistant" with "model" in the role
        role = "model" if msg["role"] == "assistant" else msg["role"]
        contents.append(types.Content(role=role, parts=parts))
    return contents


def create_gemini_schema(response_dict: Dict[str, Any]) -> types.Schema:
    """
    Recursively build a google.genai.types.Schema from a JSON-schema–style dict.
    """
    def _to_schema(obj: Any) -> types.Schema:
        # Explicit JSON-schema definitions
        if isinstance(obj, dict) and "type" in obj:
            t = obj["type"].upper()
            # OBJECT
            if t == "OBJECT":
                props = {k: _to_schema(v) for k,v in obj.get("properties", {}).items()}
                return types.Schema(
                    type=types.Type.OBJECT,
                    properties=props,
                    required=obj.get("required", [])
                )
            # ARRAY
            if t == "ARRAY":
                return types.Schema(
                    type=types.Type.ARRAY,
                    items=_to_schema(obj["items"])
                )
            # Primitives & enums
            schema = types.Schema(type=getattr(types.Type, t))
            if "enum" in obj:
                schema.enum = obj["enum"]
            if "description" in obj:
                schema.description = obj["description"]
            return schema
        # Nested dict without explicit type: treat as OBJECT
        if isinstance(obj, dict):
            return types.Schema(
                type=types.Type.OBJECT,
                properties={k: _to_schema(v) for k,v in obj.items()}
            )
        # List of items: treat as ARRAY of first element's type
        if isinstance(obj, list) and obj:
            return types.Schema(
                type=types.Type.ARRAY,
                items=_to_schema(obj[0])
            )
        # Primitive fallback by Python type
        if isinstance(obj, bool):
            return types.Schema(type=types.Type.BOOLEAN)
        if isinstance(obj, int):
            return types.Schema(type=types.Type.INTEGER)
        if isinstance(obj, float):
            return types.Schema(type=types.Type.NUMBER)
        # Default to STRING
        return types.Schema(type=types.Type.STRING)

    return _to_schema(response_dict)


def gemini_interaction_chat_with_prompt(
    secret_key,
    model,
    messages,
    system_message,
    temperature,
    max_output_tokens,
    top_p,
    top_k,
    response_format,
    timeout,
    grounding
):
    """
    Send multimodal + chat messages to Gemini and get structured/text output.
    Returns: (reply, prompt_tokens, output_tokens, total_tokens)
    """
    # 1. Initialize client
    client = genai.Client(api_key=secret_key)

    # 2. Convert messages to contents (handles text + files)
    contents = convert_messages_to_contents(messages, client)
    
    # 3. Build response schema
    if response_format["type"] == "text":
        response_schema = None
        response_mime_type = "text/plain"
    else:
        try:
            response_schema = create_gemini_schema(response_format)
            response_mime_type = "application/json"
        except Exception as e:
            raise ValueError(f"Invalid JSON schema")
        
    if grounding is True:
        if re.search(r"\b1.5\b", model, re.IGNORECASE):
            tools = [
            types.Tool(googleSearchRetrieval=types.DynamicRetrievalConfig(dynamicThreshold=0.3, mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC)),
        ]
        else:
            tools=[
                types.Tool(google_search=types.GoogleSearch()),
            ]

    else:
        tools=[]

    # 4. Configure generation
    gen_config = types.GenerateContentConfig(
        system_instruction=(
            [types.Part.from_text(text=system_message)]
            if system_message else None
        ),
        response_mime_type=response_mime_type,
        response_schema=response_schema,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
        top_k=top_k,
        tools=tools
    )
    try:
        # 5. Call generate_content 
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=gen_config,
        )

        # 6. Extract token usage
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        # output_tokens = usage.candidates_token_count
        output_tokens = usage.candidates_token_count if usage.candidates_token_count is not None else 0
        total_tokens = usage.total_token_count

        # Check if we have a valid response
        if response is None:
            raise ValueError("No valid response received from Gemini API")
        
        if not response.candidates:
                raise ValueError("No candidates returned in response")

        candidate = response.candidates[0]

        # Handle MAX_TOKENS and content filter only
        if candidate.finish_reason == FinishReason.MAX_TOKENS:
            raise ValueError("Response truncated: Maximum token limit reached. Try increasing max tokens in settings and retry.")
            
        elif candidate.finish_reason == FinishReason.SAFETY:
            raise ValueError("Response blocked: Content filtered due to safety policies. Modify your request to comply with content guidelines.")

        # The last response will be the model's reply to the most recent user message
        if response_mime_type == "text/plain":
            assistant_reply = response.text

        else:

            assistant_reply = response.candidates[0].content.parts[0].text

            # Check if response appears to be complete JSON
            if not (assistant_reply.strip().endswith('}') or assistant_reply.strip().endswith(']')):
                    raise ValueError(
                        "Response truncated: Maximum token limit reached. "
                        "Please increase max tokens in settings and retry."
                    )
            
            try:
                assistant_reply = json.loads(assistant_reply)

            except json.JSONDecodeError:
                    raise ValueError(
                        "Invalid JSON response received. Please try again."
                    )

        # assistant_reply = json.loads(assistant_reply)
        return {"response": assistant_reply ,
                "input_tokens": prompt_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                }
    
    except Exception as e:
        logger.error(f"Unexpected error in Gemini interaction: {str(e)}")
        raise ValueError(f"Unexpected error occurred: {str(e)}")


def openai_supported_models_interaction(
    secret_key,
    model,
    messages,
    temperature,
    max_tokens,
    top_p,
    frequency_penalty,
    presence_penalty,
    response_format,
    platform,
    timeout,
    platform_config,
    base_url:Optional[str] = None,
    format: Optional[str] = None,
    credentials:Optional[dict] = None
):
    messages = modify_messages_openai_supported_models(messages)

    if platform == "groq":
        base_url = "https://api.groq.com/openai/v1"

    if platform == "grok":
        base_url = "https://api.x.ai/v1"

    if platform == "custom":
        secret_key="sk-local"
        if base_url is None:
            base_url=platform_config["baseURL"]
            format=platform_config["format"]
            credentials=platform_config["credentials"]
        else:
            base_url=base_url
            format=format
            credentials=credentials

    if platform=="custom" and format=="ollama":

        payload = {
            "model": model,
            "messages": messages,
            "options":{
                "temperature": temperature,
                "num_predict":max_tokens,         
                "top_p": top_p,
                "presence_penalty":presence_penalty,
                "frequency_penalty": frequency_penalty,
            },
            "stream": False            
        }
        
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(base_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            

            # Check for incomplete response
            if not result.get("done", True):  # If "done" is False
                raise IncompleteResponseError()

            assistant_reply = result["message"]["content"].strip()
            
            input_tokens = result["prompt_eval_count"]
            output_tokens = result["eval_count"]
            total_tokens = input_tokens + output_tokens

            return {
                "response": assistant_reply,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            }

        except IncompleteResponseError as ire:
            logger.error(f"{ire.status_code} - {ire.message}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error("Error communicating with the API:", e)
            raise Exception(e)
        
    if platform == "custom" and format == "vertexAi":
        try:
            
            creds = service_account.Credentials.from_service_account_info(
                credentials,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            parts =base_url.split("/")
            project_id = parts[1]
            location   = parts[3]

            # Initialize Vertex AI client
            client = genai.Client(
                credentials =creds,
                vertexai=True,
                project=project_id,
                location=location
            )
            
            # Convert user/assistant messages to Vertex format
            contents, system_promt = modify_messages_vertex_format(messages)

            # Build generation config
            gen_config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
                system_instruction=[types.Part.from_text(text=system_promt)] if system_promt else None
            )

            # Call Vertex model
            response = client.models.generate_content(
                model=base_url,
                contents=contents,
                config=gen_config,
            )
 
            assistant_reply = response.text.strip()
            

            # Note: Token usage data not provided by Vertex SDK
            return {
                "response": assistant_reply,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }

        except Exception as e:
            logger.error(f"Error while calling Vertex AI for model '{model}': {e}")
            raise Exception(e)
            
    else:
        client = OpenAI(api_key=secret_key,
                        base_url=base_url)

        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            timeout=timeout,
        )
        
        # Extract token usage from response
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        assistant_reply = response.choices[0].message.content.strip()
        
        return {
                "response": assistant_reply,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            }
    

def modify_messages_vertex_format(
    messages: List[Dict]
) -> Tuple[List[types.Content], Optional[str]]:
    """
    Convert messages into Vertex AI `contents`, mapping:
      - 'assistant' → 'model'
      - Records the 'system' message separately.
    Returns:
      - contents: list of Content(role, parts)
      - system_prompt: the system message text (or None)
    """
    contents: List[types.Content] = []
    system_prompt: Optional[str] = None

    for msg in messages:
        
        role = msg["role"]
        
        if role == "system":
            # assume system message is always a nonempty string
            if isinstance(msg["content"], str) and msg["content"].strip():
                system_prompt = msg["content"]
            continue

        
        parts: List[types.Part] = []
        content = msg["content"]

        if isinstance(content, list):
            # content is a list of dicts; each dict is either {type:"image_url", ...} or {type:"text", ...}
            for c in content:
                ctype = c.get("type")
                if ctype == "image_url":
                    file_url = c["image_url"]["url"]
                    mime_type = identify_mime_type(file_url=file_url)
                    parts.append(
                        types.Part.from_uri(
                            file_uri=file_url,
                            mime_type=mime_type
                        )
                    )
                elif ctype == "text":
                    parts.append(types.Part.from_text(text=c["text"]))
                else:
                    raise ValueError(f"Unexpected content type: {c!r}")

        else:
            # content is not a list (presumed to be a simple string)
            parts.append(types.Part.from_text(text=content))

        # 4) Map "assistant" → "model"
        mapped_role = "model" if role == "assistant" else role
        # 5) Append to the Vertex contents list
        contents.append(types.Content(role=mapped_role, parts=parts))

    return contents, system_prompt


def modify_messages_openai_supported_models(messages: List[Dict]) -> List[Dict]:
    """
    - System messages are passed through unchanged (if nonempty string).
    - For assistant/user messages:
        • If content is a list containing any {'type': 'file', 'file_url': {'url': …}} items,
          validate each file’s extension, convert each to {'type': 'image_url', 'image_url': {'url': …}},
          but keep the entire list (including text items) in order.
        • If content is a list of only text items, join them into one string.
        • If content is not a list, pass it through.
    """
    modified_messages = []
    supported_extensions = {'.png', '.jpeg', '.jpg', '.webp', '.jfif'}

    for message in messages:
        role = message["role"]
        content = message["content"]

        # 1. Handle system messages
        if role == "system":
            if isinstance(content, str) and content.strip():
                modified_messages.append({"role": "system", "content": content})
            continue

        # 2. Handle assistant/user messages
        if role in ("assistant", "user"):
            if isinstance(content, list):
                # Determine whether there are any 'file' items
                has_file = any(item.get("type") == "file" for item in content)

                if has_file:
                    transformed_list = []
                    for item in content:
                        if item.get("type") == "file" and "file_url" in item:
                            image_url = item["file_url"].get("url", "")
                            _, ext = os.path.splitext(image_url)
                            if ext.lower() not in supported_extensions:
                                raise ValueError(
                                    f"Unsupported image extension: {ext}. "
                                    "We support PNG, JPEG, WEBP, and JFIF."
                                )
                            # Convert to image_url type
                            transformed_list.append({
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            })
                        elif item.get("type") == "text" and "text" in item:
                            # Keep text items unchanged
                            transformed_list.append(item)
                        else:
                            raise ValueError(f"Unsupported content type or missing field: {item!r}")

                    modified_messages.append({"role": role, "content": transformed_list})

                else:
                    # No file items: join all text parts into one string
                    text_content = " ".join(
                        part["text"]
                        for part in content
                        if part.get("type") == "text" and "text" in part
                    ).strip()
                    modified_messages.append({"role": role, "content": text_content})

            else:
                # Content is not a list (presumed string)
                modified_messages.append({"role": role, "content": content})

            continue


    return modified_messages



def upload_file_to_gemini(file_url: str, client: genai.Client) -> types.File:
    """
    Download a remote URL to a temp file, upload it via the Gen AI File API,
    poll until READY, and return the File object.
    """
    # 1. Download to a secure temp directory
    with tempfile.TemporaryDirectory() as tempdir:  
        temp_path = Path(tempdir)
        resp = requests.get(file_url)              
        resp.raise_for_status()
        data = resp.content

        # 2. Name the file by its SHA‑256 hash for uniqueness
        name = file_url.rsplit("/", 1)[-1]
        digest = hashlib.sha256(data).hexdigest()
        path = temp_path / f"{digest}_{name}"
        path.write_bytes(data)

        # 3. Upload via the new SDK's File API
        file_obj = client.files.upload(file=str(path))  

        # 4. Poll until the upload is processed
        while file_obj.state.name == "PROCESSING":       
            time.sleep(10)
            file_obj = client.files.get(name=file_obj.name)

        if file_obj.state.name == "FAILED":
            raise RuntimeError(f"Upload failed: {file_obj}")  

        return file_obj


def identify_mime_type(file_url):
    # Extract the file extension from the URL
    _, file_extension = os.path.splitext(file_url)
    file_extension = file_extension.lower()

    # Define custom mappings for specific file types
    custom_mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".jfif": "image/jpeg",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".heif": "image/heif",
        ".wav": "audio/wav",
        ".mp3": "audio/mp3",
        ".aiff": "audio/aiff",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        '.pdf': 'application/pdf'
    }

    # Check if the file extension is in our custom mappings
    if file_extension in custom_mime_types:
        return custom_mime_types[file_extension]

    # If not in custom mappings, use mimetypes library as a fallback
    mime_type, _ = mimetypes.guess_type(file_url)

    # If mimetypes library couldn't determine the type, return a default
    if mime_type is None:
        return "application/octet-stream"

    return mime_type


def process_ai_response_by_format(get_ai_response, response_format):
    # Ensure get_ai_response is a string
    if not isinstance(get_ai_response, str):
        get_ai_response = json.dumps(get_ai_response)

    # Remove any surrounding quotes
    get_ai_response = get_ai_response.strip('"')

    # Process based on response_format type
    if response_format.get("type") == "text":
        # For text type, ensure it's a string
        try:
            # If it's valid JSON, convert it to a string
            parsed = json.loads(get_ai_response)
            if isinstance(parsed, (dict, list)):
                content = json.dumps(parsed)
            else:
                content = str(parsed)
        except json.JSONDecodeError:
            # If it's not valid JSON, use it as is
            content = get_ai_response
    elif response_format.get("type") == "object":
        # For object type, ensure it's a valid JSON object
        try:
            content = json.loads(get_ai_response)
            if not isinstance(content, dict):
                # If it's not a dict, wrap it in a dict
                content = {"content": content}
        except json.JSONDecodeError:
            # If it's not valid JSON, wrap it in a dict
            content = {"content": get_ai_response}
    else:
        # Default to treating it as text
        content = str(get_ai_response)

    # Return the processed response in the required format
    return {"role": "assistant", "content": [{"type": "text", "text": content}]}


def convert_variables_data(data):
    # Create an empty dictionary to hold the converted data
    result = {}

    # Iterate through each item in the input data
    for item in data:
        # Extract 'name' and 'value' and add them to the result dictionary
        if "name" in item and "value" in item:
            result[item["name"]] = item["value"]

    return result


def merge_default_and_provided_variables(
    interaction_request: Dict, default_variables: Dict
) -> Dict:
    """
    Merge provided variables with default variables

    Args:
        interaction_request: Dictionary containing the interaction request
        default_variables: Dictionary containing default variables

    Returns:
        Dictionary containing merged variables
    """
    # Get variables from interaction request, defaulting to empty dict
    provided_variables = interaction_request.get("variables", {})

    if not provided_variables:
        return default_variables

    variables = {**default_variables}
    default_keys = set(default_variables.keys())
    provided_keys = set(provided_variables.keys())

    if provided_keys.issubset(default_keys):
        return provided_variables

    for key in provided_keys:
        if key in default_keys:
            variables[key] = provided_variables[key]
    for key in default_keys:
        if key not in provided_keys:
            variables[key] = default_variables[key]

    return variables


def remove_id_from_messages(messages):
    """
    Remove both '_id' and 'id' fields from messages while preserving other fields.

    Args:
        messages (list): List of message dictionaries

    Returns:
        list: Cleaned messages without '_id' and 'id' fields
    """
    cleaned_messages = []
    for message in messages:
        cleaned_message = {
            k: v
            for k, v in message.items()
            if k not in ["_id", "id", "env", "requestFrom", "initiatedAt"]
        }
        cleaned_messages.append(cleaned_message)
    return cleaned_messages
