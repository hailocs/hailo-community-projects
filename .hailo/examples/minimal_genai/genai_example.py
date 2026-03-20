#!/usr/bin/env python3
"""
Minimal GenAI LLM Chat App

Simplest possible interactive LLM chat on Hailo-10H.
Demonstrates VDevice setup, LLM loading, streaming generation, and cleanup.

Usage:
    source setup_env.sh
    python genai_example.py
    python genai_example.py --hef-path Qwen2.5-1.5B-Instruct
    python genai_example.py --temperature 0.9 --max-tokens 512

Requires: Hailo-10H hardware with GenAI SDK installed.
"""
import argparse
import sys

from hailo_platform import VDevice
from hailo_platform.genai import LLM

from hailo_apps.python.core.common.core import resolve_hef_path
from hailo_apps.python.core.common.defines import SHARED_VDEVICE_GROUP_ID, HAILO10H_ARCH
from hailo_apps.python.core.common.hailo_logger import get_logger

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Minimal Hailo-10H LLM Chat")
    parser.add_argument("--hef-path", type=str, default=None,
                        help="Path to HEF model (name or path)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Sampling temperature (0.0=deterministic, 1.0=creative)")
    parser.add_argument("--max-tokens", type=int, default=256,
                        help="Maximum tokens to generate per response")
    return parser.parse_args()


def main():
    args = parse_args()

    # Resolve model path (auto-downloads if needed)
    hef_path = resolve_hef_path(
        args.hef_path, app_name="simple_llm_chat", arch=HAILO10H_ARCH
    )
    if hef_path is None:
        logger.error("Failed to resolve HEF path. Is Hailo-10H connected?")
        sys.exit(1)

    logger.info(f"Using model: {hef_path}")

    vdevice = None
    llm = None

    try:
        # Initialize Hailo device with shared group ID
        params = VDevice.create_params()
        params.group_id = SHARED_VDEVICE_GROUP_ID
        vdevice = VDevice(params)

        # Load LLM
        llm = LLM(vdevice, str(hef_path))

        # System prompt
        system_prompt = "You are a helpful assistant running on Hailo-10H edge hardware."
        conversation = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]}
        ]

        print("Hailo LLM Chat — Type 'quit' to exit, 'clear' to reset context.\n")

        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                break
            if user_input.lower() == "clear":
                llm.clear_context()
                conversation = [conversation[0]]  # Keep system prompt
                print("Context cleared.\n")
                continue

            # Add user message
            conversation.append(
                {"role": "user", "content": [{"type": "text", "text": user_input}]}
            )

            # Stream response token by token
            print("Assistant: ", end="", flush=True)
            full_response = ""
            with llm.generate(
                prompt=conversation,
                temperature=args.temperature,
                max_generated_tokens=args.max_tokens,
            ) as stream:
                for token in stream:
                    print(token, end="", flush=True)
                    full_response += token

            # Clean up response
            full_response = full_response.split("<|im_end|>")[0]
            print("\n")

            # Add to conversation history
            conversation.append(
                {"role": "assistant", "content": [{"type": "text", "text": full_response}]}
            )

    except KeyboardInterrupt:
        print("\nShutting down...")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Always release resources
        if llm:
            try:
                llm.clear_context()
                llm.release()
            except Exception as e:
                logger.warning(f"Error releasing LLM: {e}")
        if vdevice:
            try:
                vdevice.release()
            except Exception as e:
                logger.warning(f"Error releasing VDevice: {e}")


if __name__ == "__main__":
    main()
