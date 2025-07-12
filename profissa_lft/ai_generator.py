# Copyright (C) 2024 Alexandre Mitsuru Kaihara
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS for a PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from .exceptions import LFTException

class AITopologyGenerator:
    """
    AI-powered topology generator using DeepSeek-R1-0528.
    This class provides functionality to generate LFT network topologies from natural language descriptions.
    """
    
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-R1-0528", 
                 use_hf_api: bool = True, api_token: Optional[str] = None, 
                 fallback_model: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the AI topology generator.
        
        Args:
            model_name: Hugging Face model identifier
            use_hf_api: Whether to use Hugging Face API (True) or local model (False)
            api_token: Hugging Face API token (required if use_hf_api=True)
        """
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.use_hf_api = use_hf_api
        self.api_token = api_token or os.getenv('HF_TOKEN')
        
        if use_hf_api and not self.api_token:
            raise LFTException("Hugging Face API token required when use_hf_api=True. "
                              "Set HF_TOKEN environment variable or pass api_token parameter.")
        
        self.logger = logging.getLogger(__name__)
        self._setup_model()
        
    def _setup_model(self):
        """Setup the model and tokenizer."""
        try:
            if self.use_hf_api:
                self.logger.info("Using Hugging Face API for model inference")
                self.model = None
                self.tokenizer = None
            else:
                self.logger.info(f"Loading local model: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Check if CUDA is available
                if torch.cuda.is_available():
                    self.logger.info("CUDA available, using GPU")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True
                    )
                else:
                    self.logger.info("CUDA not available, using CPU with float32")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float32,
                        device_map="cpu",
                        trust_remote_code=True,
                        low_cpu_mem_usage=True
                    )
        except Exception as e:
            if not self.use_hf_api and self.model_name != self.fallback_model:
                self.logger.warning(f"Failed to load {self.model_name}, trying fallback model: {self.fallback_model}")
                self.model_name = self.fallback_model
                self._setup_model()
            else:
                raise LFTException(f"Failed to setup model: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for LFT topology generation."""
        return """<|im_start|>system
You are an expert network engineer and Python developer specializing in the Lightweight Fog Testbed (LFT) framework. Your task is to generate Python code that creates network topologies using LFT components.

LFT Components Available:
- Host: Network hosts with IP configuration
- Switch: OpenFlow switches for SDN
- Controller: SDN controllers (e.g., OpenDaylight, ONOS)
- UE: User Equipment for wireless networks
- EPC: Evolved Packet Core for 4G networks
- EnB: eNodeB for 4G base stations

Key LFT Methods:
- instantiate(): Create and start the node
- connect(node, interface1, interface2): Connect two nodes
- setIp(ip, prefix, interface): Configure IP address
- setDefaultGateway(gateway, interface): Set default gateway
- connectToInternet(gateway_ip, prefix, interface1, interface2): Connect to internet

Generate ONLY the Python code without any explanations or markdown formatting. The code should be complete and executable.
<|im_end|>"""
    
    def _get_example_prompts(self) -> List[Dict[str, str]]:
        """Get example prompts for few-shot learning."""
        return [
            {
                "user": "Create a simple SDN topology with 2 hosts connected to a switch",
                "assistant": """from profissa_lft.host import Host
from profissa_lft.switch import Switch

h1 = Host('h1')
h2 = Host('h2')
s1 = Switch('s1')

h1.instantiate()
h2.instantiate()
s1.instantiate()

h1.connect(s1, "h1s1", "s1h1")
h2.connect(s1, "h2s1", "s1h2")

h1.setIp('10.0.0.1', 24, "h1s1")
h2.setIp('10.0.0.2', 24, "h2s1")

s1.connectToInternet('10.0.0.4', 24, "s1host", "hosts1")

h1.setDefaultGateway('10.0.0.4', "h1s1")
h2.setDefaultGateway('10.0.0.4', "h2s1")"""
            },
            {
                "user": "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC",
                "assistant": """from profissa_lft.ue import UE
from profissa_lft.enb import EnB
from profissa_lft.epc import EPC

ue1 = UE('ue1')
ue2 = UE('ue2')
enb = EnB('enb1')
epc = EPC('epc1')

ue1.instantiate()
ue2.instantiate()
enb.instantiate()
epc.instantiate()

ue1.connect(enb, "ue1enb", "enblue1")
ue2.connect(enb, "ue2enb", "enblue2")
enb.connect(epc, "enbs1", "s1enb")

ue1.setIp('192.168.1.10', 24, "ue1enb")
ue2.setIp('192.168.1.11', 24, "ue2enb")
enb.setIp('192.168.1.1', 24, "enblue1")
enb.setIp('192.168.1.2', 24, "enblue2")
enb.setIp('10.0.0.1', 24, "enbs1")
epc.setIp('10.0.0.2', 24, "s1enb")

epc.connectToInternet('10.0.0.4', 24, "epchost", "hostepc")

ue1.setDefaultGateway('192.168.1.1', "ue1enb")
ue2.setDefaultGateway('192.168.1.1', "ue2enb")
enb.setDefaultGateway('10.0.0.2', "enbs1")
epc.setDefaultGateway('10.0.0.4', "epchost")"""
            }
        ]
    
    def _generate_prompt(self, user_description: str) -> str:
        """Generate the complete prompt for the model."""
        system_prompt = self._get_system_prompt()
        
        prompt = f"{system_prompt}<|im_start|>user\n{user_description}<|im_end|>\n<|im_start|>assistant\n"
        
        return prompt
    
    def _call_hf_api(self, prompt: str) -> str:
        """Call Hugging Face API for model inference."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{self.model_name}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                return result.get('generated_text', '')
            else:
                raise LFTException(f"API call failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise LFTException(f"API request failed: {str(e)}")
    
    def _call_local_model(self, prompt: str) -> str:
        """Call local model for inference."""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.1,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.encode("<|im_end|>", add_special_tokens=False)[0]
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated part (after the prompt)
            return generated_text[len(prompt):].strip()
            
        except Exception as e:
            raise LFTException(f"Local model inference failed: {str(e)}")
    
    def generate_topology(self, description: str) -> str:
        """
        Generate LFT topology code from natural language description.
        
        Args:
            description: Natural language description of the desired topology
            
        Returns:
            Generated Python code for the LFT topology
        """
        try:
            self.logger.info(f"Generating topology for description: {description}")
            
            prompt = self._generate_prompt(description)
            
            if self.use_hf_api:
                generated_code = self._call_hf_api(prompt)
            else:
                generated_code = self._call_local_model(prompt)
            
            # Clean up the generated code
            generated_code = self._clean_generated_code(generated_code)
            
            self.logger.info("Topology generation completed successfully")
            return generated_code
            
        except Exception as e:
            self.logger.error(f"Topology generation failed: {str(e)}")
            raise LFTException(f"Failed to generate topology: {str(e)}")
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and validate the generated code."""
        # Remove any markdown formatting
        if code.startswith('```python'):
            code = code[9:]
        if code.endswith('```'):
            code = code[:-3]
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Basic validation - ensure it contains LFT imports
        if 'from profissa_lft' not in code:
            raise LFTException("Generated code does not contain LFT imports")
        
        return code
    
    def generate_and_save(self, description: str, output_file: str) -> str:
        """
        Generate topology code and save it to a file.
        
        Args:
            description: Natural language description of the desired topology
            output_file: Path to save the generated code
            
        Returns:
            Path to the saved file
        """
        try:
            generated_code = self.generate_topology(description)
            
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the generated code
            with open(output_path, 'w') as f:
                f.write(generated_code)
            
            self.logger.info(f"Generated topology saved to: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to save generated topology: {str(e)}")
            raise LFTException(f"Failed to save topology: {str(e)}")
    
    def validate_topology(self, code: str) -> bool:
        """
        Validate the generated topology code.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check for required LFT components
            required_imports = ['from profissa_lft']
            for required in required_imports:
                if required not in code:
                    return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False 