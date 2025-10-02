#!/usr/bin/env python3
"""
LFT AI-Powered Topology Generator - Modern Implementation
Uses robust open-source models with 7B+ parameters for reliable topology generation.
"""

import os
import sys
import logging
import torch
from typing import Optional, List, Dict, Any
from pathlib import Path
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    GenerationConfig
)
from accelerate import infer_auto_device_map

from .exceptions import LFTException

class ModernAITopologyGenerator:
    """
    Modern AI topology generator using robust open-source models.
    Supports both local inference and Hugging Face API.
    """
    
    # Modern, reliable models with 7B+ parameters (fully open source)
    SUPPORTED_MODELS = {
        "deepseek-r1": "deepseek-ai/DeepSeek-R1-0528",
        "phi3-mini": "microsoft/Phi-3-mini-4k-instruct",
        "qwen2-7b": "Qwen/Qwen2-7B-Instruct",
        "gemma2-9b": "google/gemma2-9b-it",
        "stable-code-3b": "stabilityai/stable-code-3b",
        "code-llama-7b": "codellama/CodeLlama-7b-Instruct-hf",
        "deepseek-coder-7b": "deepseek-ai/deepseek-coder-7b-instruct",
        "stable-code-3b-instruct": "stabilityai/stable-code-3b",
        "phi3": "microsoft/Phi-3-mini-4k-instruct"
    }
    
    def __init__(
        self, 
        model_name: str = "deepseek-r1",
        use_hf_api: bool = False,
        api_token: Optional[str] = None,
        device: str = "auto",
        load_in_8bit: bool = True,
        load_in_4bit: bool = False
    ):
        """
        Initialize the modern AI topology generator.
        
        Args:
            model_name: Model identifier from SUPPORTED_MODELS
            use_hf_api: Whether to use Hugging Face API
            api_token: Hugging Face API token
            device: Device to use ('auto', 'cpu', 'cuda')
            load_in_8bit: Use 8-bit quantization for memory efficiency
            load_in_4bit: Use 4-bit quantization (higher memory efficiency)
        """
        self.model_name = model_name
        self.use_hf_api = use_hf_api
        self.api_token = api_token or os.getenv('HF_TOKEN')
        self.device = device
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        if use_hf_api and not self.api_token:
            raise LFTException(
                "Hugging Face API token required when use_hf_api=True. "
                "Set HF_TOKEN environment variable or pass api_token parameter."
            )
        
        # Initialize model components
        self.model = None
        self.tokenizer = None
        self.generation_config = None
        
        if not use_hf_api:
            self._setup_local_model()
    
    def _setup_local_model(self):
        """Setup the local model with proper configuration."""
        try:
            # Get the actual model path
            if self.model_name in self.SUPPORTED_MODELS:
                model_path = self.SUPPORTED_MODELS[self.model_name]
            else:
                model_path = self.model_name
            
            self.logger.info(f"Loading model: {model_path}")
            
            # Configure quantization
            quantization_config = None
            if self.load_in_4bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif self.load_in_8bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True
                )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=quantization_config,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Setup generation config
            self.generation_config = GenerationConfig(
                max_new_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
            
            self.logger.info(f"Model loaded successfully: {model_path}")
            
        except Exception as e:
            raise LFTException(f"Failed to setup local model: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the optimized system prompt for LFT topology generation."""
        return """You are an expert network engineer specializing in the Lightweight Fog Testbed (LFT) framework. 

Generate Python code to create network topologies using LFT components.

Available LFT Components:
- Host: Network hosts with IP configuration
- Switch: OpenFlow switches for SDN
- Controller: SDN controllers (OpenDaylight, ONOS)
- UE: User Equipment for wireless networks
- EPC: Evolved Packet Core for 4G networks
- EnB: eNodeB for 4G base stations

Key LFT Methods:
- instantiate(): Create and start the node
- connect(node, interface1, interface2): Connect two nodes
- setIp(ip, prefix, interface): Configure IP address
- setDefaultGateway(gateway, interface): Set default gateway

IMPORTANT: Generate ONLY executable Python code. Start with 'from profissa_lft import *' and create a complete, runnable topology. No explanations, no markdown, just Python code."""
    
    def _format_prompt(self, user_prompt: str) -> str:
        """Format the prompt for the model."""
        system_prompt = self._get_system_prompt()
        return f"{system_prompt}\n\nUser request: {user_prompt}\n\nPython code:\n"
    
    def _call_local_model(self, prompt: str) -> str:
        """Call local model for inference."""
        try:
            # Format the prompt
            formatted_prompt = self._format_prompt(prompt)
            
            # Tokenize input
            inputs = self.tokenizer(
                formatted_prompt, 
                return_tensors="pt", 
                truncation=True,
                max_length=4096
            )
            
            # Move to device
            if self.device == "auto" and torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Try different generation approaches
            try:
                # Method 1: Standard generation
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=2048,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        repetition_penalty=1.1
                    )
            except Exception as gen_error:
                # Method 2: Fallback with simpler parameters
                self.logger.warning(f"Standard generation failed: {gen_error}, trying fallback...")
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=1024,
                        do_sample=False,
                        num_beams=1
                    )
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (after the prompt)
            response_start = generated_text.find("Python code:")
            if response_start != -1:
                response_start += len("Python code:")
                generated_text = generated_text[response_start:]
            
            # Clean up the response
            generated_text = generated_text.strip()
            
            return generated_text
            
        except Exception as e:
            raise LFTException(f"Local model inference failed: {str(e)}")
    
    def _call_hf_api(self, prompt: str) -> str:
        """Call Hugging Face API for inference."""
        try:
            import requests
            
            # Format the prompt
            formatted_prompt = self._format_prompt(prompt)
            
            # API endpoint
            api_url = f"https://api-inference.huggingface.co/models/{self.SUPPORTED_MODELS[self.model_name]}"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "repetition_penalty": 1.1
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            else:
                return result.get("generated_text", "")
                
        except Exception as e:
            raise LFTException(f"Hugging Face API call failed: {str(e)}")
    
    def _validate_generated_code(self, code: str) -> bool:
        """Validate that the generated code contains LFT components."""
        # Check for basic Python code structure
        if not code or len(code.strip()) < 50:
            return False
        
        # Check for LFT imports or components
        lft_indicators = [
            "from profissa_lft",
            "lft.",
            "Host(",
            "Switch(",
            "Controller(",
            "UE(",
            "EPC(",
            "EnB("
        ]
        
        # At least one LFT indicator should be present
        return any(indicator in code for indicator in lft_indicators)
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format the generated code."""
        # Remove markdown formatting
        code = code.replace("```python", "").replace("```", "")
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Ensure proper imports
        if "from profissa_lft" not in code:
            code = "from profissa_lft import *\n\n" + code
        
        return code
    
    def generate_topology(self, prompt: str, output_file: Optional[str] = None) -> str:
        """
        Generate a network topology based on the prompt.
        
        Args:
            prompt: Description of the desired topology
            output_file: Optional file to save the generated code
            
        Returns:
            Generated Python code for the topology
        """
        try:
            self.logger.info(f"Generating topology for prompt: {prompt}")
            
            # Generate code
            if self.use_hf_api:
                generated_code = self._call_hf_api(prompt)
            else:
                generated_code = self._call_local_model(prompt)
            
            # Validate the generated code
            if not self._validate_generated_code(generated_code):
                raise LFTException("Generated code does not contain valid LFT components")
            
            # Clean the code
            cleaned_code = self._clean_generated_code(generated_code)
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(cleaned_code)
                self.logger.info(f"Topology saved to: {output_file}")
            
            return cleaned_code
            
        except Exception as e:
            raise LFTException(f"Failed to generate topology: {str(e)}")
    
    def list_available_models(self) -> List[str]:
        """List all available models."""
        return list(self.SUPPORTED_MODELS.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.model:
            return {"status": "No model loaded"}
        
        info = {
            "model_name": self.model_name,
            "model_type": type(self.model).__name__,
            "device": str(next(self.model.parameters()).device),
            "dtype": str(next(self.model.parameters()).dtype),
            "parameters": sum(p.numel() for p in self.model.parameters())
        }
        
        return info

# Backward compatibility alias
AITopologyGenerator = ModernAITopologyGenerator
