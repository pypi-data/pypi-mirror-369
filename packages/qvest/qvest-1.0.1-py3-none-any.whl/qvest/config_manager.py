#!/usr/bin/env python3
"""
Configuration manager for securely storing IBM Quantum API keys
"""

import os
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages secure configuration storage for IBM Quantum API credentials"""
    
    def __init__(self):
        """Initialize config manager with default paths"""
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".qvest"
        self.config_file = self.config_dir / "config.json"
        
    def ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)  # Secure permissions
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return {}
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Warning: Could not load config file: {e}")
            return {}
            
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            self.ensure_config_dir()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
            # Set secure file permissions (user read/write only)
            os.chmod(self.config_file, 0o600)
            return True
            
        except IOError as e:
            print(f"❌ Error: Could not save config file: {e}")
            return False
            
    def get_api_key(self) -> Optional[str]:
        """Get IBM Quantum API key from config"""
        config = self.load_config()
        return config.get('ibm_quantum_token')
        
    def get_instance(self) -> Optional[str]:
        """Get IBM Quantum instance from config"""
        config = self.load_config()
        return config.get('ibm_quantum_instance')
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.load_config()
        
    def set_api_key(self, token: str, instance: Optional[str] = None) -> bool:
        """Set IBM Quantum API key and optionally instance"""
        config = self.load_config()
        config['ibm_quantum_token'] = token
        
        if instance:
            config['ibm_quantum_instance'] = instance
            
        return self.save_config(config)
        
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a configuration setting"""
        config = self.load_config()
        config[key] = value
        return self.save_config(config)
        
    def has_api_key(self) -> bool:
        """Check if API key is configured"""
        return bool(self.get_api_key())
        
    def prompt_for_api_key(self) -> Optional[str]:
        """Prompt user for IBM Quantum API key"""
        print("\n🔑 IBM Quantum API Key Setup")
        print("=" * 40)
        print("To use qvest, you need an IBM Quantum API key.")
        print("You can get one for free at: https://quantum-computing.ibm.com/")
        print("")
        
        try:
            token = getpass.getpass("Enter your IBM Quantum API key: ").strip()
            
            if not token:
                print("❌ No API key provided")
                return None
                
            # Optional instance (for IBM Cloud users)
            print("\nOptional: If you're using IBM Cloud (not Platform), enter your instance.")
            print("Format: hub/group/project (e.g., ibm-q/open/main)")
            print("Leave blank if you're using IBM Quantum Platform:")
            
            instance = input("IBM Quantum Instance (optional): ").strip()
            instance = instance if instance else None
            
            # Save credentials
            if self.set_api_key(token, instance):
                print(f"✅ API key saved to {self.config_file}")
                return token
            else:
                print("❌ Failed to save API key")
                return None
                
        except KeyboardInterrupt:
            print("\n🛑 Setup cancelled")
            return None
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            return None
            
    def clear_config(self) -> bool:
        """Clear all configuration"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                print(f"✅ Configuration cleared from {self.config_file}")
            return True
        except IOError as e:
            print(f"❌ Error clearing config: {e}")
            return False
            
    def show_config_status(self) -> None:
        """Display current configuration status"""
        print(f"\n📋 Configuration Status")
        print(f"Config file: {self.config_file}")
        print(f"Exists: {'✅' if self.config_file.exists() else '❌'}")
        
        if self.has_api_key():
            token = self.get_api_key()
            masked_token = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
            print(f"API Key: ✅ {masked_token}")
            
            instance = self.get_instance()
            if instance:
                print(f"Instance: ✅ {instance}")
            else:
                print("Instance: Not set (using Platform)")
        else:
            print("API Key: ❌ Not configured")
            
    def update_config(self) -> bool:
        """Interactive config update"""
        print("\n⚙️ Update Configuration")
        print("=" * 30)
        
        # Show current status
        self.show_config_status()
        
        print("\nWhat would you like to update?")
        print("1. IBM Quantum API Key")
        print("2. IBM Quantum Instance")
        print("3. Clear all configuration")
        print("4. Cancel")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                token = getpass.getpass("New IBM Quantum API key: ").strip()
                if token:
                    instance = self.get_instance()  # Keep existing instance
                    return self.set_api_key(token, instance)
                else:
                    print("❌ No API key provided")
                    return False
                    
            elif choice == "2":
                print("Current instance:", self.get_instance() or "Not set")
                instance = input("New instance (hub/group/project or blank): ").strip()
                instance = instance if instance else None
                
                token = self.get_api_key()
                if token:
                    return self.set_api_key(token, instance)
                else:
                    print("❌ No API key configured. Set API key first.")
                    return False
                    
            elif choice == "3":
                confirm = input("Clear all configuration? (y/N): ").strip().lower()
                if confirm in ('y', 'yes'):
                    return self.clear_config()
                else:
                    print("Cancelled")
                    return False
                    
            elif choice == "4":
                print("Cancelled")
                return False
                
            else:
                print("❌ Invalid choice")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 Update cancelled")
            return False
        except Exception as e:
            print(f"❌ Error during update: {e}")
            return False
