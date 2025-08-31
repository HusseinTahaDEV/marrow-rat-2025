#!/usr/bin/env python3
"""
Marrow RAT 2025 - Uninstaller
Removes RAT persistence and files
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path

def log(msg):
    print(f"[INFO] {msg}")

def success(msg):
    print(f"[SUCCESS] {msg}")

def error(msg):
    print(f"[ERROR] {msg}")

def remove_startup_registry():
    """Remove RAT from Windows startup registry"""
    try:
        # Common startup locations
        startup_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        
        # Common RAT names to look for
        rat_names = [
            "MarrowRAT", "MarrowAgent", "SystemService", "WindowsUpdate",
            "SecurityUpdate", "SystemCheck", "WinDefender", "ChromeUpdate"
        ]
        
        removed_count = 0
        
        for hkey, subkey in startup_keys:
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            
                            # Check if this looks like our RAT
                            is_rat = False
                            for rat_name in rat_names:
                                if rat_name.lower() in name.lower() or rat_name.lower() in value.lower():
                                    is_rat = True
                                    break
                            
                            if is_rat or "marrow" in name.lower() or "marrow" in value.lower():
                                log(f"Found RAT entry: {name} -> {value}")
                                winreg.DeleteValue(key, name)
                                success(f"Removed startup entry: {name}")
                                removed_count += 1
                                continue
                            
                            i += 1
                        except OSError:
                            break
                            
            except FileNotFoundError:
                continue
            except Exception as e:
                error(f"Registry access error: {e}")
        
        if removed_count == 0:
            log("No RAT startup entries found in registry")
        else:
            success(f"Removed {removed_count} startup entries")
            
    except Exception as e:
        error(f"Registry cleanup failed: {e}")

def kill_rat_processes():
    """Kill any running RAT processes"""
    try:
        # Get list of running processes
        result = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True)
        
        rat_processes = []
        for line in result.stdout.split('\n'):
            if any(name in line.lower() for name in ['marrow', 'rat', 'systemservice']):
                parts = line.split(',')
                if len(parts) > 1:
                    process_name = parts[0].strip('"')
                    if process_name.endswith('.exe'):
                        rat_processes.append(process_name)
        
        killed_count = 0
        for process in rat_processes:
            try:
                subprocess.run(['taskkill', '/f', '/im', process], check=True, capture_output=True)
                success(f"Killed process: {process}")
                killed_count += 1
            except subprocess.CalledProcessError:
                error(f"Could not kill process: {process}")
        
        if killed_count == 0:
            log("No RAT processes found running")
        else:
            success(f"Killed {killed_count} RAT processes")
            
    except Exception as e:
        error(f"Process cleanup failed: {e}")

def remove_rat_files():
    """Remove RAT files from common locations"""
    try:
        # Common RAT installation paths
        search_paths = [
            Path.home() / "AppData" / "Local",
            Path.home() / "AppData" / "Roaming", 
            Path("C:/Windows/System32"),
            Path("C:/Windows/SysWOW64"),
            Path("C:/ProgramData"),
            Path.home() / "Documents",
            Path.home() / "Downloads",
        ]
        
        rat_files = []
        
        for search_path in search_paths:
            if search_path.exists():
                try:
                    for file_path in search_path.rglob("*"):
                        if file_path.is_file() and any(name in file_path.name.lower() 
                                                     for name in ['marrow', 'rat', 'systemservice']):
                            rat_files.append(file_path)
                except PermissionError:
                    continue
        
        removed_count = 0
        for file_path in rat_files:
            try:
                file_path.unlink()
                success(f"Removed file: {file_path}")
                removed_count += 1
            except Exception as e:
                error(f"Could not remove {file_path}: {e}")
        
        if removed_count == 0:
            log("No RAT files found")
        else:
            success(f"Removed {removed_count} RAT files")
            
    except Exception as e:
        error(f"File cleanup failed: {e}")

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    MARROW RAT UNINSTALLER                   ║")
    print("║                      Complete Removal                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    print("WARNING: This will completely remove all Marrow RAT traces from this system.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("Uninstallation cancelled.")
        return
    
    log("Starting RAT removal process...")
    print()
    
    # Step 1: Kill running processes
    log("Step 1: Terminating RAT processes...")
    kill_rat_processes()
    print()
    
    # Step 2: Remove startup entries
    log("Step 2: Removing startup persistence...")
    remove_startup_registry()
    print()
    
    # Step 3: Remove files
    log("Step 3: Removing RAT files...")
    remove_rat_files()
    print()
    
    success("RAT uninstallation completed!")
    print("\nRecommendations:")
    print("- Restart your computer to ensure all changes take effect")
    print("- Run a full antivirus scan")
    print("- Check startup programs manually in Task Manager")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        # Check if running as admin
        if not os.access("C:\\Windows\\System32", os.W_OK):
            print("WARNING: Running without administrator privileges.")
            print("Some registry entries may not be removable.")
            print("For complete removal, run as administrator.")
            print()
        
        main()
        
    except KeyboardInterrupt:
        print("\nUninstallation cancelled by user.")
    except Exception as e:
        error(f"Uninstaller error: {e}")
        input("Press Enter to exit...")
