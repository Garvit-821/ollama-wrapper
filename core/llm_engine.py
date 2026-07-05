"""
VISION AI Assistant - LLM Engine
Ollama phi3 integration with function calling for intent routing.
"""
import json
import re
from typing import Any, Dict, Optional

import requests

import config


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "control_volume",
            "description": "Adjust the system volume. Use when the user wants to change, increase, decrease, mute, or unmute volume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["up", "down", "mute", "unmute", "set"]},
                    "level": {"type": "integer", "description": "Volume level 0-100 (only for 'set' action)"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "control_brightness",
            "description": "Adjust screen brightness. Use when user wants to change display brightness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["up", "down", "set"]},
                    "level": {"type": "integer", "description": "Brightness level 0-100 (only for 'set' action)"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_control",
            "description": "Control media playback - play/pause, next track, previous track.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["play_pause", "next", "previous", "stop"]},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for files or movies on the PC. Can search by name, extension, or browse a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "File name or pattern to search for"},
                    "directory": {"type": "string", "description": "Directory path to search in"},
                    "file_type": {"type": "string", "description": "Type filter like 'video' or '.pdf'"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open a file or folder at a specific path on the PC.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open/launch an application on the PC by name.",
            "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website URL in the browser.",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search for content on YouTube or play a specific video/channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "action": {"type": "string", "enum": ["search", "play"]},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play music on YouTube Music.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "action": {"type": "string", "enum": ["play", "search", "playlist"]},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "Send a WhatsApp message to a contact.",
            "parameters": {
                "type": "object",
                "properties": {"contact": {"type": "string"}, "message": {"type": "string"}},
                "required": ["contact", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Compose and send an email.",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the screen.",
            "parameters": {"type": "object", "properties": {"search_google": {"type": "boolean"}}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city.",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get latest news headlines.",
            "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_prices",
            "description": "Search and compare prices of a product across e-commerce platforms.",
            "parameters": {"type": "object", "properties": {"product": {"type": "string"}}, "required": ["product"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_notes",
            "description": "Create, read, update, or delete notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "read", "list", "delete", "search"]},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_code",
            "description": "Generate code in any programming language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "language": {"type": "string"},
                    "save_to_file": {"type": "string"},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text on behalf of the user at the current cursor position.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_plan",
            "description": "Create, view, or update a plan/to-do list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "view", "add_task", "complete_task", "list"]},
                    "plan_name": {"type": "string"},
                    "task": {"type": "string"},
                    "task_index": {"type": "integer"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet programmatically for real-time information, news, or answers. The results will be returned as text to you.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Read the main text content of a specific webpage/URL. Use this to surf deeper after searching or when a direct link is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The exact URL to retrieve content from"}
                },
                "required": ["url"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_concept",
            "description": "Explain a concept in detail for studying.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "mode": {"type": "string", "enum": ["explain", "summarize", "quiz", "flashcards"]},
                    "level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a safe terminal command (bash on Linux, powershell on Windows) to compile code, run test suites, check git status, run custom python scripts, or run command line programs. The result will be returned in the log.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The exact shell command to execute."}
                },
                "required": ["command"]
            }
        }
    },
]

TOOL_SCHEMA = {tool["function"]["name"]: tool["function"]["parameters"] for tool in TOOL_DEFINITIONS}


def _tool_prompt_guardrail() -> str:
    return (
        "If a tool is needed, call exactly one tool. If no tool is needed, reply naturally. "
        "Never invent tool names or arguments. Prefer concise output."
    )


class LLMEngine:
    """Ollama integration with function calling for VISION."""

    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL.rstrip("/")
        self.model = config.OLLAMA_MODEL
        self.conversation_history = [{"role": "system", "content": f"{config.SYSTEM_PROMPT}\n\n{_tool_prompt_guardrail()}"}]
        self.max_history = 30
        self.tools_supported: Optional[bool] = None

    def _trim_history(self):
        if len(self.conversation_history) > self.max_history + 1:
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-self.max_history:]

    def _direct_intent_from_user_message(self, user_message: str) -> Optional[Dict[str, Any]]:
        msg = user_message.strip()
        lower = msg.lower()

        if lower in {"what can you do", "what can you do?", "help me", "help"}:
            return None

        # System controls
        if any(token in lower for token in ["volume up", "increase volume", "turn up volume"]):
            return {"type": "function_call", "content": None, "function_name": "control_volume", "function_args": {"action": "up"}, "tool_call_id": "direct-intent-1"}
        if any(token in lower for token in ["volume down", "decrease volume", "turn down volume"]):
            return {"type": "function_call", "content": None, "function_name": "control_volume", "function_args": {"action": "down"}, "tool_call_id": "direct-intent-1"}
        if "unmute" in lower:
            return {"type": "function_call", "content": None, "function_name": "control_volume", "function_args": {"action": "unmute"}, "tool_call_id": "direct-intent-1"}
        if "mute" in lower:
            return {"type": "function_call", "content": None, "function_name": "control_volume", "function_args": {"action": "mute"}, "tool_call_id": "direct-intent-1"}
        if any(token in lower for token in ["brightness up", "increase brightness", "more brightness"]):
            return {"type": "function_call", "content": None, "function_name": "control_brightness", "function_args": {"action": "up"}, "tool_call_id": "direct-intent-1"}
        if any(token in lower for token in ["brightness down", "decrease brightness", "less brightness"]):
            return {"type": "function_call", "content": None, "function_name": "control_brightness", "function_args": {"action": "down"}, "tool_call_id": "direct-intent-1"}
        if any(token in lower for token in ["pause", "play/pause", "resume"]):
            return {"type": "function_call", "content": None, "function_name": "media_control", "function_args": {"action": "play_pause"}, "tool_call_id": "direct-intent-1"}
        if "next song" in lower or lower == "next":
            return {"type": "function_call", "content": None, "function_name": "media_control", "function_args": {"action": "next"}, "tool_call_id": "direct-intent-1"}
        if "previous song" in lower or lower == "previous":
            return {"type": "function_call", "content": None, "function_name": "media_control", "function_args": {"action": "previous"}, "tool_call_id": "direct-intent-1"}

        if lower in {"open youtube", "youtube open", "launch youtube"}:
            return {
                "type": "function_call",
                "content": None,
                "function_name": "search_youtube",
                "function_args": {"query": "youtube", "action": "search"},
                "tool_call_id": "direct-intent-1",
            }

        if lower.startswith("play ") and len(lower) > 5:
            query = msg[5:].strip()
            return {
                "type": "function_call",
                "content": None,
                "function_name": "play_music",
                "function_args": {"query": query, "action": "play"},
                "tool_call_id": "direct-intent-1",
            }

        if lower.startswith("open ") and "." in lower and " " not in lower.split("open ", 1)[1]:
            url = msg.split(" ", 1)[1].strip()
            return {
                "type": "function_call",
                "content": None,
                "function_name": "open_website",
                "function_args": {"url": url},
                "tool_call_id": "direct-intent-1",
            }

        if lower.startswith("open "):
            target = msg.split(" ", 1)[1].strip()
            if any(token in lower for token in ["website", "site", ".com", ".in", ".org", ".net"]):
                return {
                    "type": "function_call",
                    "content": None,
                    "function_name": "open_website",
                    "function_args": {"url": target.replace("website", "").replace("site", "").strip()},
                    "tool_call_id": "direct-intent-1",
                }
            return {
                "type": "function_call",
                "content": None,
                "function_name": "open_application",
                "function_args": {"app_name": target},
                "tool_call_id": "direct-intent-1",
            }

        if ("search file" in lower or "search files" in lower or lower.startswith("find ")) and " on this pc" in lower:
            query = self._extract_search_query(msg, ["search file", "search files", "find", "search for"])
            directory = "D:\\" if " d drive" in lower or " in d " in lower else None
            args = {"query": query}
            if directory:
                args["directory"] = directory
            return {
                "type": "function_call",
                "content": None,
                "function_name": "search_files",
                "function_args": args,
                "tool_call_id": "direct-intent-1",
            }

        if lower.startswith("search for ") or lower.startswith("search "):
            query = self._extract_search_query(msg, ["search for", "search"])
            if "youtube" in lower:
                return {
                    "type": "function_call",
                    "content": None,
                    "function_name": "search_youtube",
                    "function_args": {"query": query.replace("youtube", "").strip() or query, "action": "search"},
                    "tool_call_id": "direct-intent-1",
                }
            return {
                "type": "function_call",
                "content": None,
                "function_name": "web_search",
                "function_args": {"query": query},
                "tool_call_id": "direct-intent-1",
            }

        if lower.startswith("take note") or lower.startswith("note "):
            content = msg.split(" ", 1)[1].replace("note", "", 1).strip(": -")
            title = (content[:40] or "Quick Note").strip()
            return {
                "type": "function_call",
                "content": None,
                "function_name": "manage_notes",
                "function_args": {"action": "create", "title": title, "content": content},
                "tool_call_id": "direct-intent-1",
            }

        if "weather" in lower:
            return {"type": "function_call", "content": None, "function_name": "get_weather", "function_args": {}, "tool_call_id": "direct-intent-1"}
        if "news" in lower:
            return {"type": "function_call", "content": None, "function_name": "get_news", "function_args": {}, "tool_call_id": "direct-intent-1"}
        if "price" in lower or "cheapest" in lower:
            query = self._extract_search_query(msg, ["price of", "prices of", "compare prices of", "cheapest", "price"])
            return {"type": "function_call", "content": None, "function_name": "compare_prices", "function_args": {"product": query}, "tool_call_id": "direct-intent-1"}

        if "screenshot" in lower and ("google image" in lower or "image search" in lower):
            return {"type": "function_call", "content": None, "function_name": "take_screenshot", "function_args": {"search_google": True}, "tool_call_id": "direct-intent-1"}
        if "screenshot" in lower:
            return {"type": "function_call", "content": None, "function_name": "take_screenshot", "function_args": {"search_google": False}, "tool_call_id": "direct-intent-1"}

        if lower.startswith("run command ") or lower.startswith("run: "):
            cmd = msg.split(" ", 1)[1].strip()
            return {
                "type": "function_call",
                "content": None,
                "function_name": "execute_command",
                "function_args": {"command": cmd},
                "tool_call_id": "direct-intent-1",
            }

        return None

    def _chat(self, messages: list, temperature: float = 0.7, include_tools: bool = True) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if include_tools:
            payload["tools"] = TOOL_DEFINITIONS
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=90)
        if response.status_code >= 400:
            raise requests.HTTPError(response.text, response=response)
        return response.json().get("message", {})

    def _build_no_tools_router_prompt(self, user_message: str) -> str:
        tools_compact = [{"name": t["function"]["name"], "parameters": t["function"]["parameters"]} for t in TOOL_DEFINITIONS]
        return (
            "You are an intent router.\n"
            "Pick exactly one action based on the user message.\n"
            "If a tool is needed, output ONLY valid JSON in this format:\n"
            '{"type":"function_call","function_name":"<tool_name>","function_args":{...}}\n'
            "If no tool is needed, output ONLY valid JSON in this format:\n"
            '{"type":"text","content":"<assistant reply>"}\n'
            "No markdown, no extra text.\n\n"
            f"Available tools: {json.dumps(tools_compact)}\n\n"
            f"User message: {user_message}"
        )

    def _parse_json_block(self, text: str) -> Optional[Dict[str, Any]]:
        candidate = (text or "").strip()
        if not candidate:
            return None
        if "```" in candidate:
            candidate = candidate.replace("```json", "```").replace("```JSON", "```")
            parts = [p.strip() for p in candidate.split("```") if p.strip()]
            for part in parts:
                if part.startswith("{") and part.endswith("}"):
                    candidate = part
                    break
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    sliced = candidate[start : end + 1]
                    parsed = json.loads(sliced)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    # Attempt to recover from common malformed JSON like extra closing braces.
                    for _ in range(4):
                        if not sliced.endswith("}"):
                            break
                        sliced = sliced[:-1].rstrip()
                        try:
                            parsed = json.loads(sliced)
                            if isinstance(parsed, dict):
                                return parsed
                        except Exception:
                            continue
                    return None
            return None

    def _extract_search_query(self, user_message: str, action_words: list[str]) -> str:
        text = user_message.strip()
        lowered = text.lower()
        for phrase in action_words:
            pos = lowered.find(phrase)
            if pos != -1:
                text = text[pos + len(phrase):].strip(" :,-")
                break
        fillers = [
            "for", "the", "a", "an", "on this pc", "on pc", "in this pc", "please", "in my pc", "on my pc",
            "in d drive", "in c drive", "in e drive"
        ]
        lowered = text.lower()
        for filler in fillers:
            lowered = re.sub(rf"\b{re.escape(filler)}\b", " ", lowered)
        cleaned = re.sub(r"\s+", " ", lowered).strip()
        return cleaned or user_message.strip()

    def _coerce_function_args(self, function_name: Optional[str], function_args: Any, user_message: str) -> Dict[str, Any]:
        if not function_name:
            return {}
        args = function_args if isinstance(function_args, dict) else {}
        schema = TOOL_SCHEMA.get(function_name, {})
        required = schema.get("required", [])

        if function_name == "search_youtube":
            if not args.get("query"):
                args["query"] = self._extract_search_query(user_message, ["search youtube", "open youtube", "play on youtube", "youtube"])
            if not args.get("action"):
                msg = user_message.lower()
                args["action"] = "play" if "play" in msg or "open" in msg else "search"

        elif function_name == "play_music":
            if not args.get("query"):
                args["query"] = self._extract_search_query(user_message, ["play", "play music", "listen to"])
            args.setdefault("action", "play")

        elif function_name in ("search_files", "web_search"):
            if not args.get("query"):
                args["query"] = self._extract_search_query(user_message, ["search file", "search files", "find", "search for", "search"])

        elif function_name == "open_website" and not args.get("url"):
            args["url"] = self._extract_search_query(user_message, ["open", "go to", "launch"])

        elif function_name == "read_webpage" and not args.get("url"):
            args["url"] = self._extract_search_query(user_message, ["read", "read webpage", "scrape", "open webpage", "fetch"])

        elif function_name == "open_application" and not args.get("app_name"):
            args["app_name"] = self._extract_search_query(user_message, ["open", "launch", "start"])

        elif function_name == "execute_command" and not args.get("command"):
            args["command"] = self._extract_search_query(user_message, ["run command", "run", "execute command", "execute"])

        # Final safeguard: required args should never be empty strings.
        for key in list(args.keys()):
            if isinstance(args[key], str):
                args[key] = args[key].strip()
                if not args[key]:
                    del args[key]

        for req in required:
            if req not in args:
                if req == "query":
                    args["query"] = user_message.strip()
                elif req == "command":
                    args["command"] = user_message.strip()
                elif req == "action" and function_name == "search_youtube":
                    args["action"] = "search"

        return args

    def _recover_from_text_response(self, text: str, user_message: str) -> Optional[Dict[str, Any]]:
        parsed = self._parse_json_block(text)
        if not parsed:
            return None
        if parsed.get("type") == "function_call":
            fn = parsed.get("function_name")
            coerced = self._coerce_function_args(fn, parsed.get("function_args") or {}, user_message)
            return {
                "type": "function_call",
                "content": None,
                "function_name": fn,
                "function_args": coerced,
                "tool_call_id": "ollama-recovered-tool-call-1",
            }
        if parsed.get("type") == "text":
            return {
                "type": "text",
                "content": parsed.get("content", ""),
                "function_name": None,
                "function_args": None,
            }
        return None

    def _route_without_native_tools(self, user_message: str) -> Dict[str, Any]:
        router_messages = [
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": self._build_no_tools_router_prompt(user_message)},
        ]
        message = self._chat(router_messages, temperature=0.1, include_tools=False)
        parsed = self._parse_json_block(message.get("content", ""))
        if not parsed:
            return {"type": "text", "content": message.get("content", "") or "", "function_name": None, "function_args": None}

        if parsed.get("type") == "function_call":
            fn = parsed.get("function_name")
            coerced = self._coerce_function_args(fn, parsed.get("function_args") or {}, user_message)
            return {
                "type": "function_call",
                "content": None,
                "function_name": fn,
                "function_args": coerced,
                "tool_call_id": "ollama-fallback-tool-call-1",
            }
        return {
            "type": "text",
            "content": parsed.get("content", ""),
            "function_name": None,
            "function_args": None,
        }

    def _normalize_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            tool = tool_calls[0].get("function", {})
            return {
                "type": "function_call",
                "content": None,
                "function_name": tool.get("name"),
                "function_args": tool.get("arguments") or {},
                "tool_call_id": "ollama-tool-call-1",
            }

        text = message.get("content", "") or ""
        return {"type": "text", "content": text, "function_name": None, "function_args": None}

    def chat(self, user_message: str) -> Dict[str, Any]:
        self.conversation_history.append({"role": "user", "content": user_message})
        self._trim_history()
        direct = self._direct_intent_from_user_message(user_message)
        if direct:
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": direct["tool_call_id"],
                            "type": "function",
                            "function": {
                                "name": direct["function_name"],
                                "arguments": direct["function_args"],
                            },
                        }
                    ],
                }
            )
            return direct
        try:
            if self.tools_supported is False:
                normalized = self._route_without_native_tools(user_message)
            else:
                message = self._chat(self.conversation_history, include_tools=True)
                self.tools_supported = True
                normalized = self._normalize_response(message)
                if normalized["type"] == "function_call":
                    normalized["function_args"] = self._coerce_function_args(
                        normalized.get("function_name"),
                        normalized.get("function_args") or {},
                        user_message,
                    )
                else:
                    recovered = self._recover_from_text_response(normalized.get("content", ""), user_message)
                    if recovered:
                        normalized = recovered
            if normalized["type"] == "function_call":
                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": normalized["tool_call_id"],
                                "type": "function",
                                "function": {
                                    "name": normalized["function_name"],
                                    "arguments": normalized["function_args"],
                                },
                            }
                        ],
                    }
                )
            else:
                self.conversation_history.append({"role": "assistant", "content": normalized["content"]})
            return normalized
        except requests.HTTPError as e:
            body = str(e)
            if "does not support tools" in body:
                self.tools_supported = False
                normalized = self._route_without_native_tools(user_message)
                if normalized["type"] == "function_call":
                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": normalized["tool_call_id"],
                                    "type": "function",
                                    "function": {
                                        "name": normalized["function_name"],
                                        "arguments": normalized["function_args"],
                                    },
                                }
                            ],
                        }
                    )
                else:
                    self.conversation_history.append({"role": "assistant", "content": normalized["content"]})
                return normalized
            return {"type": "text", "content": f"LLM Error: {body}", "function_name": None, "function_args": None}
        except Exception as e:
            return {"type": "text", "content": f"LLM Error: {e}", "function_name": None, "function_args": None}

    def report_function_result(self, tool_call_id: str, function_name: str, result: str) -> Dict[str, Any]:
        self.conversation_history.append(
            {
                "role": "tool",
                "tool_name": function_name,
                "tool_call_id": tool_call_id,
                "content": result,
            }
        )
        try:
            if self.tools_supported is False:
                summary_messages = [
                    {"role": "system", "content": "You are VISION. Convert tool execution result into a concise, natural user-facing response."},
                    {
                        "role": "user",
                        "content": f"User requested action: {function_name}\nTool result:\n{result}\n\nRespond naturally and briefly.",
                    },
                ]
                message = self._chat(summary_messages, include_tools=False)
                normalized = {
                    "type": "text",
                    "content": message.get("content", "") or result,
                    "function_name": None,
                    "function_args": None,
                }
            else:
                message = self._chat(self.conversation_history, include_tools=True)
                normalized = self._normalize_response(message)
            if normalized["type"] == "function_call":
                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": normalized["tool_call_id"],
                                "type": "function",
                                "function": {
                                    "name": normalized["function_name"],
                                    "arguments": normalized["function_args"],
                                },
                            }
                        ],
                    }
                )
            else:
                self.conversation_history.append({"role": "assistant", "content": normalized["content"]})
            return normalized
        except requests.HTTPError as e:
            body = str(e)
            if "does not support tools" in body:
                self.tools_supported = False
                summary_messages = [
                    {"role": "system", "content": "You are VISION. Convert tool execution result into a concise, natural user-facing response."},
                    {
                        "role": "user",
                        "content": f"User requested action: {function_name}\nTool result:\n{result}\n\nRespond naturally and briefly.",
                    },
                ]
                message = self._chat(summary_messages, include_tools=False)
                normalized = {
                    "type": "text",
                    "content": message.get("content", "") or result,
                    "function_name": None,
                    "function_args": None,
                }
                self.conversation_history.append({"role": "assistant", "content": normalized["content"]})
                return normalized
            return {"type": "text", "content": f"LLM Error: {body}", "function_name": None, "function_args": None}
        except Exception as e:
            return {"type": "text", "content": f"LLM Error: {e}", "function_name": None, "function_args": None}

    def _single_turn_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        message = self._chat(messages, temperature=temperature)
        return message.get("content", "") or ""

    def generate_code(self, description: str, language: str = "python") -> str:
        try:
            return self._single_turn_text(
                system_prompt=f"You are a code generator. Generate clean {language} code. Return ONLY code.",
                user_prompt=description,
                temperature=0.3,
            )
        except Exception as e:
            return f"# Error generating code: {e}"

    def explain_topic(self, topic: str, mode: str = "explain", level: str = "intermediate") -> str:
        mode_prompts = {
            "explain": f"Explain '{topic}' clearly at a {level} level with examples.",
            "summarize": f"Provide a concise summary of '{topic}' at a {level} level.",
            "quiz": f"Create 5 quiz questions about '{topic}' at a {level} level and include answers.",
            "flashcards": f"Create 10 flashcards (Q&A) about '{topic}' at a {level} level.",
        }
        try:
            return self._single_turn_text(
                system_prompt="You are a knowledgeable tutor. Be clear and structured.",
                user_prompt=mode_prompts.get(mode, mode_prompts["explain"]),
                temperature=0.5,
            )
        except Exception as e:
            return f"Error: {e}"

    def clear_history(self):
        self.conversation_history = [{"role": "system", "content": f"{config.SYSTEM_PROMPT}\n\n{_tool_prompt_guardrail()}"}]
