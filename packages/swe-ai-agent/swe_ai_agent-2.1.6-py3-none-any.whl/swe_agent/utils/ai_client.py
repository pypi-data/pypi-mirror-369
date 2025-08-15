"""
Unified AI client supporting both Anthropic and OpenRouter with model selection.
"""

import os
import logging
from typing import Optional, Union, Dict, Any
from anthropic import Anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)

# Default models
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4"

# Supported providers
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENROUTER = "openrouter"

class UnifiedAIClient:
    """
    Unified client for both Anthropic and OpenRouter APIs.
    Provides a consistent interface regardless of the underlying provider.
    """
    
    def __init__(self, provider: str = PROVIDER_ANTHROPIC, model: Optional[str] = None, 
                 openrouter_site_url: Optional[str] = None, openrouter_site_name: Optional[str] = None):
        """
        Initialize the unified AI client.
        
        Args:
            provider: Either "anthropic" or "openrouter" 
            model: Model to use (defaults based on provider)
            openrouter_site_url: Optional site URL for OpenRouter rankings
            openrouter_site_name: Optional site name for OpenRouter rankings
        """
        self.provider = provider.lower()
        self.openrouter_site_url = openrouter_site_url
        self.openrouter_site_name = openrouter_site_name
        
        # Set default models based on provider
        if model is None:
            if self.provider == PROVIDER_ANTHROPIC:
                self.model = DEFAULT_ANTHROPIC_MODEL
            else:
                self.model = DEFAULT_OPENROUTER_MODEL
        else:
            self.model = model
            
        # Initialize the appropriate client
        if self.provider == PROVIDER_ANTHROPIC:
            self._init_anthropic()
        elif self.provider == PROVIDER_OPENROUTER:
            self._init_openrouter()
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'anthropic' or 'openrouter'")
            
        logger.info(f"Initialized {self.provider} client with model: {self.model}")
    
    def _init_anthropic(self):
        """Initialize Anthropic client."""
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        self.client = Anthropic(api_key=api_key)
    
    def _init_openrouter(self):
        """Initialize OpenRouter client."""
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable must be set")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    
    def create_message(self, messages: list, system_prompt: Optional[str] = None, 
                      max_tokens: int = 4000, temperature: float = 0) -> str:
        """
        Create a message using the configured provider and model.
        
        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for randomness
            
        Returns:
            The AI response text
        """
        if self.provider == PROVIDER_ANTHROPIC:
            return self._create_anthropic_message(messages, system_prompt, max_tokens, temperature)
        else:
            return self._create_openrouter_message(messages, system_prompt, max_tokens, temperature)
    
    def _create_anthropic_message(self, messages: list, system_prompt: Optional[str], 
                                 max_tokens: int, temperature: float) -> str:
        """Create message using Anthropic API."""
        try:
            # Convert messages format if needed
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    formatted_messages.append(msg)
                else:
                    formatted_messages.append({"role": "user", "content": str(msg)})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant specializing in software engineering.",
                messages=formatted_messages
            )
            
            # Extract response text
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            elif response.content[0].type == "text":
                return response.content[0].text
            else:
                return str(response.content[0])
                
        except Exception as e:
            logger.error(f"Error calling Anthropic: {e}")
            raise
    
    def _create_openrouter_message(self, messages: list, system_prompt: Optional[str],
                                  max_tokens: int, temperature: float) -> str:
        """Create message using OpenRouter API."""
        try:
            # Convert messages format if needed
            formatted_messages = []
            
            # Add system message if provided
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            
            # Add user messages
            for msg in messages:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    formatted_messages.append(msg)
                else:
                    formatted_messages.append({"role": "user", "content": str(msg)})
            
            # Prepare extra headers for OpenRouter
            extra_headers = {}
            if self.openrouter_site_url:
                extra_headers["HTTP-Referer"] = self.openrouter_site_url
            if self.openrouter_site_name:
                extra_headers["X-Title"] = self.openrouter_site_name
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                extra_headers=extra_headers if extra_headers else None
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            raise

def get_ai_client(provider: Optional[str] = None, model: Optional[str] = None, 
                  openrouter_site_url: Optional[str] = None, openrouter_site_name: Optional[str] = None) -> UnifiedAIClient:
    """
    Get configured AI client with provider and model selection.
    
    Args:
        provider: "anthropic" or "openrouter" (defaults to anthropic)
        model: Model to use (provider-specific defaults if not specified)
        openrouter_site_url: Optional site URL for OpenRouter
        openrouter_site_name: Optional site name for OpenRouter
        
    Returns:
        Configured UnifiedAIClient instance
    """
    if provider is None:
        provider = PROVIDER_ANTHROPIC
    
    return UnifiedAIClient(
        provider=provider,
        model=model,
        openrouter_site_url=openrouter_site_url,
        openrouter_site_name=openrouter_site_name
    )

# Convenience functions for backward compatibility
def get_anthropic_client() -> UnifiedAIClient:
    """Get Anthropic client (backward compatibility)."""
    return get_ai_client(provider=PROVIDER_ANTHROPIC)

def call_claude(client: UnifiedAIClient, message: str, system_prompt: str = None) -> str:
    """Call AI with a message (backward compatibility)."""
    messages = [{"role": "user", "content": message}]
    return client.create_message(messages, system_prompt)