#!/usr/bin/env python3
"""
Configuration Management Module
Unified management of all system configuration parameters
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

class Config:
    """Configuration Management Class"""
    
    def __init__(self):
        """Initialize configuration"""
        load_dotenv()
        self._load_config()
    
    def _load_config(self):
        """Load configuration parameters"""
        # Azure OpenAI configuration
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        # Search configuration
        self.model_name = 'all-MPNET-base-v2'
        self.max_products = 5
        self.enable_backup = True
        
        # File path configuration
        self.data_file = '../Intelligent Product Retrieval System/Parts-Keywords.csv'
        self.embeddings_file = 'data/embeddings/product_embeddings.npy'
        self.index_file = 'data/indexes/product_index.faiss'
        
        # Website configuration
        self.richelieu_url = "https://www.richelieu.com/ca/en/"
        self.login_email = "li000436@gmail.com"
        self.login_password = "$101010Mm"
        
        # Environment variable configuration
        self.tokenizers_parallelism = 'false'
        self.omp_num_threads = '1'
        self.mkl_num_threads = '1'
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        required_vars = [
            "azure_openai_api_key",
            "azure_openai_endpoint", 
            "azure_openai_deployment_name",
            "azure_openai_api_version"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search-related configuration"""
        return {
            'model_name': self.model_name,
            'max_products': self.max_products,
            'enable_backup': self.enable_backup
        }
    
    def get_azure_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI configuration"""
        return {
            'api_key': self.azure_openai_api_key,
            'endpoint': self.azure_openai_endpoint,
            'deployment_name': self.azure_openai_deployment_name,
            'api_version': self.azure_openai_api_version
        }
    
    def get_file_paths(self) -> Dict[str, str]:
        """Get file path configuration"""
        return {
            'data_file': self.data_file,
            'embeddings_file': self.embeddings_file,
            'index_file': self.index_file
        }

# Global configuration instance
config = Config() 