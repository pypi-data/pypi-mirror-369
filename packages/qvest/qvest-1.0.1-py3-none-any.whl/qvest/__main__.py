#!/usr/bin/env python3
"""
Q VEST - IBM Quantum Portfolio Prediction CLI
Main entry point for the command-line interface
"""

import sys
import argparse
from typing import Optional

from .config_manager import ConfigManager
from .prediction import QuantumPortfolioOptimizer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="qvest",
        description="IBM Quantum-powered portfolio optimization CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qvest                    # Run portfolio optimization
  qvest config             # Configure IBM Quantum API key
  qvest config --status    # Show configuration status
  qvest config --update    # Update configuration
  qvest config --clear     # Clear all configuration
  qvest --version          # Show version information

Get your free IBM Quantum API key at:
https://quantum-computing.ibm.com/
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="qvest 1.0.0"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )
    
    # Config subcommand
    config_parser = subparsers.add_parser(
        "config",
        help="Manage IBM Quantum API configuration"
    )
    config_parser.add_argument(
        "--status",
        action="store_true",
        help="Show current configuration status"
    )
    config_parser.add_argument(
        "--update", 
        action="store_true",
        help="Update configuration interactively"
    )
    config_parser.add_argument(
        "--clear",
        action="store_true", 
        help="Clear all configuration"
    )
    
    args = parser.parse_args()
    
    # Initialize config manager
    config = ConfigManager()
    
    try:
        if args.command == "config":
            handle_config_command(config, args)
        else:
            # Main portfolio optimization
            handle_optimization_command(config)
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


def handle_config_command(config: ConfigManager, args) -> None:
    """Handle configuration subcommands"""
    if args.status:
        config.show_config_status()
        
    elif args.update:
        success = config.update_config()
        if success:
            print("✅ Configuration updated successfully")
        else:
            print("❌ Configuration update failed")
            sys.exit(1)
            
    elif args.clear:
        confirm = input("❓ Clear all configuration? (y/N): ").strip().lower()
        if confirm in ('y', 'yes'):
            success = config.clear_config()
            if success:
                print("✅ Configuration cleared successfully")
            else:
                print("❌ Failed to clear configuration")
                sys.exit(1)
        else:
            print("Cancelled")
            
    else:
        # Default config behavior - setup if needed
        if not config.has_api_key():
            print("🔧 No API key configured. Let's set one up:")
            api_key = config.prompt_for_api_key()
            if not api_key:
                print("❌ API key setup failed")
                sys.exit(1)
        else:
            config.show_config_status()
            print("\nTo update your configuration, use: qvest config --update")


def handle_optimization_command(config: ConfigManager) -> None:
    """Handle main portfolio optimization"""
    # Check if API key is configured
    if not config.has_api_key():
        print("🚀 Welcome to Q VEST!")
        print("=" * 50)
        print("It looks like this is your first time using qvest.")
        print("Let's get you set up with your IBM Quantum API key.\n")
        
        api_key = config.prompt_for_api_key()
        if not api_key:
            print("\n❌ Cannot proceed without IBM Quantum API key")
            print("Run 'qvest config' to set up your credentials later.")
            sys.exit(1)
    else:
        api_key = config.get_api_key()
    
    # Get instance if configured
    instance = config.get_instance()
    
    # Initialize and run quantum portfolio optimizer
    try:
        optimizer = QuantumPortfolioOptimizer(api_key, instance)
        result = optimizer.run_optimization()
        
        if result:
            print("\n🎉 Portfolio optimization completed successfully!")
        else:
            print("\n❌ Portfolio optimization failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        print("\nTroubleshooting:")
        print("1. Check your IBM Quantum API key: qvest config --status")
        print("2. Update your credentials: qvest config --update")
        print("3. Clear and reconfigure: qvest config --clear")
        sys.exit(1)


if __name__ == "__main__":
    main()
