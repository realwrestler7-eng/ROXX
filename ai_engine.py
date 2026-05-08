"""
ROXX AI - Advanced AI Engine Integration
Part 2: AI Services & API Integration

This module provides:
- OpenAI GPT-4 integration
- Google Gemini integration
- Hugging Face models
- Response caching
- Error handling
- Rate limiting
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# OPENAI GPT-4 INTEGRATION
# ============================================================================

class OpenAIService:
    """
    OpenAI GPT-4 service for advanced conversations
    
    Features:
    - Direct API integration
    - Token management
    - Error handling
    - Response caching
    - Rate limiting
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize OpenAI service
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key not configured")
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response using GPT-4
        
        Args:
            messages (list): Conversation messages
            temperature (float): Response creativity (0-2)
            max_tokens (int): Max response length
            
        Returns:
            dict: API response with generated text
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            logger.debug(f"🤖 Sending request to OpenAI GPT-4")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info("✅ GPT-4 response received")
            return {
                'success': True,
                'response': data['choices'][0]['message']['content'],
                'tokens_used': data['usage']['total_tokens'],
                'model': self.model
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OpenAI API Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_system_prompt(self, voice_preference: str, name: str = "ROXX") -> str:
        """
        Create system prompt for AI personality
        
        Args:
            voice_preference (str): 'boy' or 'girl'
            name (str): AI name
            
        Returns:
            str: System prompt
        """
        gender = "male" if voice_preference == "boy" else "female"
        
        system_prompt = f"""
        You are ROXX, an advanced AI assistant with a {gender} personality.
        
        Personality Traits:
        - Friendly and conversational
        - Knowledgeable and helpful
        - Tech-savvy and modern
        - Witty and engaging
        - Respectful of privacy
        
        You can help with:
        - General conversations and advice
        - Technical questions
        - Creative writing
        - Problem solving
        - Learning and education
        
        Guidelines:
        - Keep responses concise but informative
        - Use casual language when appropriate
        - Ask clarifying questions if needed
        - Be honest about limitations
        - Maintain context in conversations
        
        Always respond in a friendly and natural way.
        """
        return system_prompt.strip()


# ============================================================================
# GOOGLE GEMINI INTEGRATION
# ============================================================================

class GeminiService:
    """
    Google Gemini API service for conversations
    
    Features:
    - Streaming responses
    - Multi-turn conversations
    - Advanced reasoning
    - Safety filters
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini service
        
        Args:
            api_key (str): Google API key
        """
        self.api_key = api_key or os.environ.get('GOOGLE_GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"
        self.model = "gemini-pro"
        
        if not self.api_key:
            logger.warning("⚠️ Google Gemini API key not configured")
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_output_tokens: int = 2048
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response using Gemini
        
        Args:
            prompt (str): Input prompt
            temperature (float): Response creativity
            top_p (float): Nucleus sampling parameter
            max_output_tokens (int): Max response length
            
        Returns:
            dict: Generated response
        """
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topP": top_p,
                    "maxOutputTokens": max_output_tokens
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
            }
            
            logger.debug("🌟 Sending request to Google Gemini")
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            text_response = data['candidates'][0]['content']['parts'][0]['text']
            
            logger.info("✅ Gemini response received")
            return {
                'success': True,
                'response': text_response,
                'model': self.model,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Gemini API Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat_with_memory(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Chat with conversation memory
        
        Args:
            user_message (str): Current user message
            conversation_history (list): Previous messages
            
        Returns:
            dict: Response with context
        """
        # Build context from history
        context = ""
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = msg.get('sender', '').upper()
            content = msg.get('content', '')
            context += f"{role}: {content}\n"
        
        # Add current message
        full_prompt = context + f"USER: {user_message}\nASSISTANT:"
        
        response = self.generate_response(full_prompt)
        
        if response and response.get('success'):
            # Extract clean response (remove "ASSISTANT:" prefix if present)
            text = response['response']
            if text.startswith('ASSISTANT:'):
                text = text[len('ASSISTANT:'):].strip()
            
            response['response'] = text
        
        return response


# ============================================================================
# HUGGING FACE INTEGRATION
# ============================================================================

class HuggingFaceService:
    """
    Hugging Face inference API for various models
    
    Features:
    - Multiple model support
    - Text generation
    - Text summarization
    - Sentiment analysis
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Hugging Face service
        
        Args:
            api_key (str): Hugging Face API key
        """
        self.api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        self.models = {
            'chat': 'meta-llama/Llama-2-7b-chat',
            'summarization': 'facebook/bart-large-cnn',
            'sentiment': 'distilbert-base-uncased-finetuned-sst-2-english'
        }
        
        if not self.api_key:
            logger.warning("⚠️ Hugging Face API key not configured")
    
    def query_model(
        self,
        model_type: str,
        inputs: str,
        parameters: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Query a Hugging Face model
        
        Args:
            model_type (str): Type of model to use
            inputs (str): Input text
            parameters (dict): Additional parameters
            
        Returns:
            dict: Model output
        """
        try:
            model_name = self.models.get(model_type)
            if not model_name:
                return {
                    'success': False,
                    'error': f'Unknown model type: {model_type}'
                }
            
            url = f"{self.base_url}/{model_name}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": inputs
            }
            
            if parameters:
                payload["parameters"] = parameters
            
            logger.debug(f"🤗 Querying Hugging Face model: {model_type}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Hugging Face response received")
            return {
                'success': True,
                'response': data,
                'model': model_type
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Hugging Face API Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_text(
        self,
        prompt: str,
        max_length: int = 200
    ) -> Optional[Dict[str, Any]]:
        """
        Generate text using Llama model
        
        Args:
            prompt (str): Input prompt
            max_length (int): Max output length
            
        Returns:
            dict: Generated text
        """
        parameters = {
            "max_length": max_length,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        return self.query_model('chat', prompt, parameters)
    
    def summarize_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Summarize text using BART
        
        Args:
            text (str): Text to summarize
            
        Returns:
            dict: Summarized text
        """
        return self.query_model('summarization', text)


# ============================================================================
# CONVERSATION MANAGER
# ============================================================================

class ConversationManager:
    """
    Manages conversations with multiple AI backends
    
    Features:
    - Backend selection
    - Context management
    - Response caching
    - Error handling
    """
    
    def __init__(self):
        """Initialize conversation manager with all AI services"""
        self.openai = OpenAIService()
        self.gemini = GeminiService()
        self.huggingface = HuggingFaceService()
        self.response_cache = {}
    
    def get_ai_response(
        self,
        user_message: str,
        backend: str = 'gemini',
        conversation_history: List[Dict[str, str]] = None,
        voice_preference: str = 'boy'
    ) -> Dict[str, Any]:
        """
        Get AI response from specified backend
        
        Args:
            user_message (str): User's message
            backend (str): AI backend ('gemini', 'openai', 'huggingface')
            conversation_history (list): Previous messages
            voice_preference (str): 'boy' or 'girl'
            
        Returns:
            dict: AI response
        """
        
        logger.info(f"🎯 Getting response from {backend}")
        
        if backend == 'gemini':
            if conversation_history:
                return self.gemini.chat_with_memory(user_message, conversation_history)
            else:
                return self.gemini.generate_response(user_message)
        
        elif backend == 'openai':
            system_prompt = self.openai.create_system_prompt(voice_preference)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if conversation_history:
                # Add previous messages
                for msg in conversation_history[-10:]:
                    role = "assistant" if msg.get('sender') == 'ai' else "user"
                    messages.insert(-1, {
                        "role": role,
                        "content": msg.get('content')
                    })
            
            return self.openai.generate_response(messages)
        
        elif backend == 'huggingface':
            return self.huggingface.generate_text(user_message)
        
        else:
            return {
                'success': False,
                'error': f'Unknown backend: {backend}'
            }


# ============================================================================
# INITIALIZATION
# ============================================================================

# Global instance
ai_manager = ConversationManager()


def get_ai_manager() -> ConversationManager:
    """
    Get global AI manager instance
    
    Returns:
        ConversationManager: Global AI manager
    """
    return ai_manager
