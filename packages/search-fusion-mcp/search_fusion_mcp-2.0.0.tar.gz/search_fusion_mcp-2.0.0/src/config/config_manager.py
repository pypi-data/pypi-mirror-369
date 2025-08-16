#!/usr/bin/env python

"""
Configuration Manager
Handles all configuration from MCP environment variables
"""

import os
import json
import subprocess
import platform
import socket
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from loguru import logger


@dataclass 
class SearchEngineConfig:
    """Search engine configuration"""
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    cse_id: Optional[str] = None
    enabled: bool = False


@dataclass
class ServerConfig:
    """Main server configuration"""
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "search_fusion.log"
    log_rotation: str = "100 MB"
    
    # Proxy configuration
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    
    # Rate limiting configuration
    default_cooldown: int = 300
    max_error_count: int = 3
    
    # Search engine configurations
    google: SearchEngineConfig = field(default_factory=SearchEngineConfig)
    serper: SearchEngineConfig = field(default_factory=SearchEngineConfig)  # Same priority as Google
    jina: SearchEngineConfig = field(default_factory=lambda: SearchEngineConfig(enabled=True))  # Always available
    bing: SearchEngineConfig = field(default_factory=SearchEngineConfig)
    baidu: SearchEngineConfig = field(default_factory=SearchEngineConfig)
    exa: SearchEngineConfig = field(default_factory=SearchEngineConfig)
    duckduckgo: SearchEngineConfig = field(default_factory=lambda: SearchEngineConfig(enabled=True))


class ConfigManager:
    """Configuration manager - handles all configuration sources"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_path: Legacy parameter, now deprecated, using pure MCP environment variable configuration
        """
        if config_path:
            logger.warning("⚠️ config_path parameter is deprecated, now using pure MCP environment variable configuration")
        
        self.config = ServerConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from MCP environment variables only"""
        
        # Load from environment variables and MCP configuration only
        self._load_from_env()
        
        # Auto-detect and setup proxy (inspired by concurrent-browser-mcp implementation)
        self._auto_detect_proxy()
        
        # Setup proxy environment variables
        self._setup_proxy()
        
        logger.info("✅ Configuration loaded successfully (MCP environment variable mode)")
        self._log_config_summary()
    
    def _load_from_env(self):
        """Load configuration from environment variables and MCP configuration"""
        
        # Basic configuration
        self.config.log_level = os.getenv('LOG_LEVEL', self.config.log_level)
        self.config.log_file = os.getenv('LOG_FILE', self.config.log_file)
        self.config.log_rotation = os.getenv('LOG_ROTATION', self.config.log_rotation)
        
        # Proxy configuration - prioritize environment variables
        self.config.http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        self.config.https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        self.config.no_proxy = os.getenv('NO_PROXY') or os.getenv('no_proxy', self.config.no_proxy)
        
        # MCP format API key configuration
        # Supports format: SEARCH_ENGINE_API_KEY, SEARCH_ENGINE_SECRET_KEY etc
        
        # Google configuration
        google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_SEARCH_API_KEY')
        google_cse_id = os.getenv('GOOGLE_CSE_ID') or os.getenv('GOOGLE_SEARCH_CSE_ID')
        if google_api_key:
            self.config.google = SearchEngineConfig(
                api_key=google_api_key,
                cse_id=google_cse_id,
                enabled=True
            )
        
        # Serper configuration
        serper_api_key = os.getenv('SERPER_API_KEY') or os.getenv('SERPER_SEARCH_API_KEY')
        if serper_api_key:
            self.config.serper = SearchEngineConfig(
                api_key=serper_api_key,
                enabled=True
            )
        
        # Bing configuration
        bing_api_key = os.getenv('BING_API_KEY') or os.getenv('BING_SEARCH_API_KEY')
        if bing_api_key:
            self.config.bing = SearchEngineConfig(
                api_key=bing_api_key,
                enabled=True
            )
        
        # Baidu configuration
        baidu_api_key = os.getenv('BAIDU_API_KEY') or os.getenv('BAIDU_SEARCH_API_KEY')
        baidu_secret_key = os.getenv('BAIDU_SECRET_KEY') or os.getenv('BAIDU_SEARCH_SECRET_KEY')
        if baidu_api_key and baidu_secret_key:
            self.config.baidu = SearchEngineConfig(
                api_key=baidu_api_key,
                secret_key=baidu_secret_key,
                enabled=True
            )
        
        # Jina configuration
        jina_api_key = os.getenv('JINA_API_KEY') or os.getenv('JINA_SEARCH_API_KEY')
        self.config.jina = SearchEngineConfig(
            api_key=jina_api_key,  # Can be empty
            enabled=True  # Jina is always enabled
        )
        
        # Exa configuration
        exa_api_key = os.getenv('EXA_API_KEY') or os.getenv('EXA_SEARCH_API_KEY')
        if exa_api_key:
            self.config.exa = SearchEngineConfig(
                api_key=exa_api_key,
                enabled=True
            )
    
    def _auto_detect_proxy(self):
        """Auto-detect system proxy settings - inspired by concurrent-browser-mcp implementation"""
        try:
            # If environment variables already have proxy settings, skip auto-detection
            if self.config.http_proxy or self.config.https_proxy:
                logger.info("🌐 Using proxy from environment variables")
                return
            
            # Follow concurrent-browser-mcp detection order
            detected_proxy = self._detect_local_proxy()
            
            if detected_proxy:
                self.config.http_proxy = detected_proxy
                self.config.https_proxy = detected_proxy
                logger.info(f"🔍 Auto-detected proxy: {detected_proxy}")
            else:
                logger.info("🌐 No system proxy detected, using direct connection")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to auto-detect proxy: {e}")
    
    def _detect_local_proxy(self) -> Optional[str]:
        """Detect local proxy - fully inspired by concurrent-browser-mcp implementation"""
        
        # 1. Check environment variables
        env_proxy = self._get_proxy_from_env()
        if env_proxy:
            logger.info(f"Proxy detected from environment variables: {env_proxy}")
            return env_proxy
        
        # 2. Check common proxy ports - this is the key feature!
        common_ports = [7890, 1087, 8080, 3128, 8888, 10809, 20171]
        for port in common_ports:
            proxy_url = f"http://127.0.0.1:{port}"
            if self._test_proxy_connection(proxy_url):
                logger.info(f"Local proxy port detected: {port}")
                return proxy_url
        
        # 3. Try to detect system proxy settings (macOS)
        if platform.system().lower() == 'darwin':
            system_proxy = self._get_macos_system_proxy()
            if system_proxy:
                logger.info(f"System proxy detected: {system_proxy}")
                return system_proxy
        
        return None
    
    def _get_proxy_from_env(self) -> Optional[str]:
        """Get proxy from environment variables"""
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        all_proxy = os.getenv('ALL_PROXY') or os.getenv('all_proxy')
        
        return http_proxy or https_proxy or all_proxy
    
    def _test_proxy_connection(self, proxy_url: str) -> bool:
        """Test proxy connection - fully inspired by concurrent-browser-mcp implementation"""
        try:
            # Simple port detection to avoid complex network requests
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            
            # Create socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # 3-second timeout, consistent with concurrent-browser-mcp
            
            try:
                result = sock.connect_ex((parsed.hostname, parsed.port))
                return result == 0  # 0 means connection successful
            finally:
                sock.close()
                
        except Exception:
            return False
    
    def _get_macos_system_proxy(self) -> Optional[str]:
        """Get macOS system proxy settings - inspired by concurrent-browser-mcp implementation"""
        try:
            # Use the same command as concurrent-browser-mcp
            result = subprocess.run([
                'networksetup', '-getwebproxy', 'Wi-Fi'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                # Try Ethernet
                result = subprocess.run([
                    'networksetup', '-getwebproxy', 'Ethernet'
                ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                enabled = any('Enabled: Yes' in line for line in lines)
                
                if enabled:
                    server = None
                    port = None
                    
                    for line in lines:
                        if line.startswith('Server:'):
                            server = line.split(':', 1)[1].strip()
                        elif line.startswith('Port:'):
                            port = line.split(':', 1)[1].strip()
                    
                    if server and port:
                        return f"http://{server}:{port}"
                        
        except Exception as e:
            logger.debug(f"macOS proxy detection failed: {e}")
        
        return None
    
    def _setup_proxy(self):
        """Setup proxy environment variables"""
        if self.config.http_proxy:
            os.environ['http_proxy'] = self.config.http_proxy
            os.environ['HTTP_PROXY'] = self.config.http_proxy
        
        if self.config.https_proxy:
            os.environ['https_proxy'] = self.config.https_proxy
            os.environ['HTTPS_PROXY'] = self.config.https_proxy
        
        if self.config.no_proxy:
            os.environ['no_proxy'] = self.config.no_proxy
            os.environ['NO_PROXY'] = self.config.no_proxy
    
    def _log_config_summary(self):
        """Log configuration summary"""
        enabled_engines = []
        for engine_name in ['google', 'serper', 'jina', 'duckduckgo', 'exa', 'bing', 'baidu']:
            if self.is_engine_enabled(engine_name):
                config = self.get_engine_config(engine_name)
                if config.api_key:
                    enabled_engines.append(f"{engine_name.title()} (with API key)")
                else:
                    enabled_engines.append(f"{engine_name.title()} (free)")
        
        logger.info(f"📊 Enabled search engines: {', '.join(enabled_engines) if enabled_engines else 'None'}")
        
        if self.config.http_proxy or self.config.https_proxy:
            logger.info(f"🌐 Proxy configuration: HTTP={self.config.http_proxy}, HTTPS={self.config.https_proxy}")
        
        logger.info(f"📝 Logging: Level={self.config.log_level}, File={self.config.log_file}")
    
    def get_engine_config(self, engine_name: str) -> SearchEngineConfig:
        """Get configuration for specified search engine"""
        return getattr(self.config, engine_name.lower(), SearchEngineConfig(enabled=False))
    
    def is_engine_enabled(self, engine_name: str) -> bool:
        """Check if search engine is enabled and has valid configuration"""
        engine_config = self.get_engine_config(engine_name)
        
        # DuckDuckGo and Jina don't require API keys
        if engine_name.lower() in ['duckduckgo', 'jina']:
            return True
        
        # Other engines require API keys
        return engine_config.enabled and bool(engine_config.api_key)
    
    def get_proxy_config(self) -> Dict[str, Optional[str]]:
        """Get proxy configuration"""
        return {
            "http://": self.config.http_proxy,
            "https://": self.config.https_proxy,
        } if self.config.http_proxy or self.config.https_proxy else None
