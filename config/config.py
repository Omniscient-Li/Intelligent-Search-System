"""
Configuration Management for Intelligent Product System
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI Configuration"""
    api_key: str
    endpoint: str
    deployment_name: str
    api_version: str = "2024-02-15-preview"
    temperature: float = 0.7
    max_tokens: int = 2000

@dataclass
class BrowserConfig:
    """Browser Configuration"""
    headless: bool = True
    timeout: int = 30000
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

@dataclass
class SearchConfig:
    """Search Configuration"""
    max_products: int = 5
    deduplication_threshold: float = 0.8
    search_timeout: int = 60

@dataclass
class LoggingConfig:
    """Logging Configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/system.log"

@dataclass
class SystemConfig:
    """System Configuration"""
    # Azure OpenAI
    azure_openai: AzureOpenAIConfig
    
    # Browser settings
    browser: BrowserConfig
    
    # Search settings
    search: SearchConfig
    
    # Logging
    logging: LoggingConfig
    
    # Performance
    tokenizers_parallelism: str = "false"
    omp_num_threads: str = "4"
    mkl_num_threads: str = "4"

def load_config() -> SystemConfig:
    """Load system configuration from environment variables"""
    
    # Azure OpenAI Configuration
    azure_openai = AzureOpenAIConfig(
        api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", ""),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "2000"))
    )
    
    # Browser Configuration
    browser = BrowserConfig(
        headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
        timeout=int(os.getenv("BROWSER_TIMEOUT", "30000")),
        user_agent=os.getenv("BROWSER_USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    )
    
    # Search Configuration
    search = SearchConfig(
        max_products=int(os.getenv("MAX_PRODUCTS", "5")),
        deduplication_threshold=float(os.getenv("DEDUPLICATION_THRESHOLD", "0.8")),
        search_timeout=int(os.getenv("SEARCH_TIMEOUT", "60"))
    )
    
    # Logging Configuration
    logging = LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        file=os.getenv("LOG_FILE", "logs/system.log")
    )
    
    return SystemConfig(
        azure_openai=azure_openai,
        browser=browser,
        search=search,
        logging=logging,
        tokenizers_parallelism=os.getenv("TOKENIZERS_PARALLELISM", "false"),
        omp_num_threads=os.getenv("OMP_NUM_THREADS", "4"),
        mkl_num_threads=os.getenv("MKL_NUM_THREADS", "4")
    )

# Global configuration instance
config = load_config() 