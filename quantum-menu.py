import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkfont
import time
import json
import random
import string
import struct

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

gtag = "com.AnotherAxiom.GorillaTag"
folder_path = os.path.join(base_path, "DO NOT DELETE")
adb_path = os.path.join(base_path, "platform-tools", "adb.exe")
quest_file = f"/sdcard/Android/data/{gtag}/files/il2cpp/Metadata/global-metadata.dat"
if not os.path.isdir(folder_path):
    os.makedirs(folder_path, exist_ok=True)
local_file = os.path.join(folder_path, "global-metadata.dat")
    
try:
    subprocess.run([adb_path, "start-server"], capture_output=True, text=True, timeout=5)
    print("[ADB] Starting ADB server...")
    time.sleep(2)
except Exception:
    print("[ADB] Warning: Failed to start ADB server")
    messagebox.showwarning("Warning", "Failed to start ADB! You can ignore this if you are just making a metadata. Otherwise run run_adb.bat.")
    pass

if not os.path.exists(local_file):
    result = subprocess.run([adb_path, "pull", quest_file, local_file], capture_output=True, text=True)
    print("[Metadata] Attempting to pull Quest metadata...")
    if result.returncode != 0:
        print("[Metadata] Error: Failed to pull Quest metadata from device")
        messagebox.showerror("Error", "Please either save a metadata to the 'DO NOT DELETE' folder or connect your headset via USB or wireless! Make sure you have Gorilla Tag installed.")

def check_adb_device():
    if not os.path.exists(adb_path):
        print("[ADB] Critical Error: ADB executable not found")
        return False, f"ADB not found at: {adb_path}"
    
    try:
        start = subprocess.run([adb_path, "start-server"], capture_output=True, text=True, timeout=5)
        time.sleep(0.3)
        result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=5)
        combined = (start.stdout or "") + (start.stderr or "") + "\n" + (result.stdout or "") + (result.stderr or "")
        lines = result.stdout.strip().splitlines()
        devices = [line for line in lines[1:] if line.strip() and "device" in line]
        return (len(devices) > 0), combined
    
    except Exception as e:
        print(f"[ADB] Error checking device: {str(e)}")
        return False, str(e)

def connect_headset(headset_ip=None, retries=3, delay=0.5):
    print("[Connection] Attempting to connect to headset...")
    for attempt in range(retries):
        device_found, output = check_adb_device()
        if device_found:
            print("[Connection] Device connected successfully")
            return True
        elif headset_ip:
            try:
                print(f"[Connection] Trying wireless connection to {headset_ip}...")
                subprocess.run([adb_path, "connect", f"{headset_ip}:5037"], capture_output=True, text=True, timeout=5)
                device_found, output = check_adb_device()
                if device_found:
                    print("[Connection] Wireless connection established")
                    return True
            except Exception:
                pass
        time.sleep(delay)
    print("[Connection] Failed to connect to device")
    return False

def update_json(data):
    print("[Settings] Saving settings to file...")
    with open('settings.json', 'w') as f:
        json.dump(data, f, indent=4)
    
if not os.path.exists('settings.json'):
    print("[Settings] Creating new settings file...")
    data = {
        "tutorial_spawn_for_every_patch_with_infection_mods": False,
        "headset_ip": None,
        "gtag_version": None,
        "custom_methods_enabled": False,
        "punish_mod_checkers": False,
        "methods": {
            "example1original": "example1new",
            "example2original": "example2new"
        }
    }
    update_json(data)

def load_settings():
    """Load settings from JSON file"""
    with open('settings.json', 'r') as f:
        return json.load(f)

# Load initial settings
settings = load_settings()
print("[Settings] Loaded settings from file")

discord = "https://discord.gg/cybz3FDNfX"
headset_ip = settings.get('headset_ip')
custom_methods_enabled = settings.get('custom_methods_enabled')
do_tutorial = settings.get('tutorial_spawn_for_every_patch_with_infection_mods')
punish_mod_checkers = settings.get('punish_mod_checkers', False)
stored_version = settings.get('gtag_version')
if custom_methods_enabled:
    custom_methods = settings.get('methods')

if not connect_headset(headset_ip):
    messagebox.showwarning("Warning", "No VR headset found! Please plug in your headset or setup the wireless feature,"
    " and MAKE SURE YOU HAVE ALLOWED THE POPUP IN YOUR HEADSET! You can ignore this if you are just making a metadata.")

errors = 0

verse = "1 Thessalonians 5:16-17 NKJV".upper()
verse_contents = "Rejoice always, pray without ceasing.".upper()
verse_header = f"{verse_contents} - {verse}"

try:
    print("[Version] Checking Gorilla Tag version...")
    ver_result = subprocess.run(
        [adb_path, "shell", "dumpsys", "package", gtag],
        capture_output=True, text=True, timeout=10
    )

    version = None
    for line in ver_result.stdout.splitlines():
        line = line.strip()
        if line.startswith("versionCode="):
            version = line.split("=")[1]
    
    if version is None:
        print("[Version] Warning: Could not determine Gorilla Tag version")
        messagebox.showwarning("Warning", "Cannot get current Gorilla Tag version! This will cause errors if it has updated. Make sure you have Gorilla Tag installed. If your headset isn't connected, please connect it and restart the script! You can ignore this if you are just making a metadata.")
    else:
        print(f"[Version] Detected Gorilla Tag version: {version}")

    if stored_version != version and stored_version is not None and version is not None:
        print(f"[Version] Update detected: {stored_version} -> {version}")
        messagebox.showinfo("Update", "Gorila Tag Update Detected")
        if os.path.exists(local_file):
            os.remove(local_file)
            print("[Metadata] Removed old metadata file")
        settings['gtag_version'] = version
        update_json(settings)
        print("[Metadata] Pulling updated metadata...")
        res = subprocess.run([adb_path, "pull", quest_file, local_file], capture_output=True, text=True)
        if res.returncode != 0:
            print("[Metadata] Error: Failed to pull updated metadata")
            messagebox.showwarning(
                "Warning",
                "Cannot save updated metadata! Please save it manually. Make sure you have Gorilla Tag installed. If your headset isn't connected, please connect it and restart the script! You can ignore this if you are just making a metadata."
            )
        else:
            print("[Metadata] Successfully pulled updated metadata")
    elif stored_version is None:
        settings['gtag_version'] = version
        update_json(settings)
        

except Exception as e: 
    print(f"[Version] Error checking version: {str(e)}")
    messagebox.showwarning(
        "Warning",
        "Cannot get current Gorilla Tag version! This will cause errors if it has updated. Make sure you have Gorilla Tag installed. If your headset isn't connected, please connect it and restart the script! You can ignore this if you are just making a metadata."
    )

def send_vr_notification(title, message):
    subprocess.run(
        [
            adb_path,
            "shell",
            "cmd",
            "notification",
            "post",
            "-S",
            "bigtext",
            "quantum_menu",
            title,
            message
        ],
        capture_output=True,
        text=True
    )

def purple_motd():
    print("[Mod] Applying purple MOTD...")
    motd = f"/sdcard/Android/data/{gtag}/files/TitleDataCache.json"
    with open('TitleDataCache.json', 'w') as f:
        data = {"null": None}
        json.dump(data, f)

    result = subprocess.run([adb_path, "push", 'TitleDataCache.json', motd], capture_output=True, text=True)
    if result.returncode != 0:
        print("[Mod] Error: Failed to apply purple MOTD")
        messagebox.showerror("Error", "Your headset either isn't connected, or this is already enabled!")
    else:
        print("[Mod] Successfully applied purple MOTD")
        messagebox.showinfo("Success", "Successfully applied!")
    
def revert():
    print("[Revert] Reverting to original metadata...")
    result = subprocess.run([adb_path, "push", local_file, quest_file], capture_output=True, text=True)

    if result.returncode != 0:
        print("[Revert] Error: Failed to revert changes")
        messagebox.showerror("Error", "Please connect your headset to do this!")
    else:
        print("[Revert] Successfully reverted changes")
        messagebox.showinfo("Success", "Reverted changes successfully!")
        try:
            send_vr_notification("Success", "Reverted changes successfully!")
        except Exception:
            pass

def close_game(package_name):
    subprocess.run(
        [adb_path, "shell", "am", "force-stop", package_name],
        capture_output=True,
        text=True
    )

class Edit:
    class StringLiteral:
        def __init__(self, length=0, offset=0):
            self.Length = length
            self.Offset = offset

    def __init__(self, full_name):
        self.reader = open(full_name, "rb")
        self.stringLiteralOffset = 0
        self.stringLiteralCount = 0
        self.DataInfoPosition = 0
        self.stringLiteralDataOffset = 0
        self.stringLiteralDataCount = 0
        self.stringLiterals = []
        self.strBytes = []
        self.ReadHeader()
        self.ReadLiteral()
        self.ReadStrByte()

    def ReadHeader(self):
        vansity = struct.unpack("<I", self.reader.read(4))[0]
        if vansity != 0xFAB11BAF:
            print("[Metadata] Error: Invalid metadata file signature")
            messagebox.showerror("Error", "Invalid Metadata!")
            raise Exception("Flag check failed")
        version = struct.unpack("<i", self.reader.read(4))[0]
        self.stringLiteralOffset = struct.unpack("<I", self.reader.read(4))[0]
        self.stringLiteralCount = struct.unpack("<I", self.reader.read(4))[0]
        self.DataInfoPosition = self.reader.tell()
        self.stringLiteralDataOffset = struct.unpack("<I", self.reader.read(4))[0]
        self.stringLiteralDataCount = struct.unpack("<I", self.reader.read(4))[0]

    def ReadLiteral(self):
        self.reader.seek(self.stringLiteralOffset)
        for _ in range(self.stringLiteralCount // 8):
            length = struct.unpack("<I", self.reader.read(4))[0]
            offset = struct.unpack("<I", self.reader.read(4))[0]
            self.stringLiterals.append(self.StringLiteral(length, offset))

    def ReadStrByte(self):
        for lit in self.stringLiterals:
            self.reader.seek(self.stringLiteralDataOffset + lit.Offset)
            self.strBytes.append(self.reader.read(lit.Length))

    def WriteToNewFile(self, file_name):
        self.reader.seek(0)
        data = self.reader.read()
        with open(file_name, "wb") as writer:
            writer.write(data)

            count = 0
            for i, lit in enumerate(self.stringLiterals):
                lit.Offset = count
                lit.Length = len(self.strBytes[i])
                writer.seek(self.stringLiteralOffset + i*8)
                writer.write(struct.pack("<I I", lit.Length, lit.Offset))
                count += lit.Length

            tmp = (self.stringLiteralDataOffset + count) % 4
            if tmp != 0:
                count += 4 - tmp

            if count > self.stringLiteralDataCount:
                if self.stringLiteralDataOffset + self.stringLiteralDataCount < len(data):
                    self.stringLiteralDataOffset = len(data)
            self.stringLiteralDataCount = count

            writer.seek(self.stringLiteralDataOffset)
            for b in self.strBytes:
                writer.write(b)

            writer.seek(self.DataInfoPosition)
            writer.write(struct.pack("<I I", self.stringLiteralDataOffset, self.stringLiteralDataCount))

    def Dispose(self):
        if self.reader:
            self.reader.close()

    def ReplaceStrings(self, replacements: dict):
        global errors
        decoded = []
        for b in self.strBytes:
            try:
                decoded.append(b.decode('utf-8'))
            except UnicodeDecodeError:
                errors += 1
                decoded.append(None)
        for key, new_val in replacements.items():
            found = False
            for i, s in enumerate(decoded):
                if s is None:
                    continue
                if s == key:
                    new = new_val or ""
                    self.strBytes[i] = new.encode('utf-8')
                    decoded[i] = new
                    found = True
                    break
            if not found:
                print(f"[Patch] Error: String not found - '{key}'")
                errors += 1
    
class Metadata:
    def __init__(self):
        self.to_do = {}
        self.active_methods = set()

        self.predictions = 50
        
        self.purple_motd = "real sigma"

        self.crucial = {
            'CHECKING DAILY ROCKS...': verse_header,
            'SUCCESSFULLY GOT DAILY ROCKS!': verse_header,
            'WAITING TO GET DAILY ROCKS...': verse_header,
            'CREDITS': f'<color=red>https://guns.lol/turntojesus <color=#718EFF>\n\n- METADATA CREDITS -\n\nJESUS (our lord and savior)\nTTJ (made the metadata)\nSBEAR AND TTJ (made the API)\nCHIP (made the 32-bit version and then no acid method)\nBOWTIE AND TOXXIN (helped me with the OS in the menu)\nLEO (made this method and the hoverboard method and the ball method)\n\n- GAME CREDITS -\n'
        }
        
        for key, value in self.crucial.items():
            self.to_do[key] = value

        self.touch_ups = {
            'OFFLINE': '<color=red>OFFLINE</color>',
            'Outfit #': '| OUTFIT #'
        }
        self.custom_leaderboard = {
            'Player                     Color         Level        MMR': 'Monkey                     Race          Level        MMR',
            '\n  PLAYER     COLOR  MUTE   REPORT': '\n  MONKEY      RACE   STFU    BAN',
            'MUTE                                REPORT\n': 'STFU                                  BAN\n',
            'MUTE                HATE SPEECH    TOXICITY     CHEATING       CANCEL\n': 'STFU                N WORD SPAM    PRROXZY       HACKER        NVM\n'
        }

        self.anti_acid_kill = {
            'PlayerStateChangeRPC': '_'
        }

        self.custom_camera_text = {
            'RECORD': '-RECORD-',
            'GO LIVE': '-GO LIVE-'
        }

        self.everything_is_buyable = {
            'INSUFFICIENT SHINY ROCKS FOR THIS ITEM!': 'SUCCESS! ENJOY YOUR NEW ITEM!',
            'ERROR IN PURCHASING ITEM! NO MONEY WAS SPENT. SELECT ANOTHER ITEM.': 'SUCCESS! ENJOY YOUR NEW ITEM!'
        }

        self.no_ghosts = {
            'RemoteActivateGhost': '_',
            'WanderingGhost': '_',
            'RPC_RemoteActiveGhost': '_',
            'LurkerGhost': '_'
        }
        
        self.monster_antikill = {
            'ApplyEnemyHitPlayerRPC': '_',
            'ApplyHitRPC': '_'
        }
        
        self.no_handtaps = {
            'OnHandTapRPC': '_',
            'OnHandTapRPCShared': '_',
            'PlayHandTapShared': '_',
            'RPC_PlayHandTap': '_',
            'StealthHandTapFX': '_'
        }
        
        self.clear_water = {
            '_GlobalCameraOverlapWaterSurfacePlane': '_',
            '_GlobalMainWaterSurfacePlane': '_',
            '_GlobalUnderwaterEffectsDistanceToSurfaceFade': '_',
            '_GlobalUnderwaterFogColor': '_',
            '_GlobalUnderwaterFogParams': '_',
            '_GlobalWaterTintColor': '_'
        }
        
        self.no_splash = {
            'RPC_PlaySplashEffect': '_',
            'WaterSplashEffect': '_',
            'WaterRippleEffect': '_'
        }

        self.all_infection_stuff = {
            'didTutorial': ("<size=100><color=red>#####################################################################" if punish_mod_checkers else "<size=65><color=white>No mods detected]<size=0>") + (''.join(random.choice(string.ascii_letters+string.digits+string.punctuation) for _ in range(random.randint(1, 15))) if do_tutorial else "")
        }
        
        self.monkeblocks_cheats = {
            'PieceDestroyedRPC': '_',
            'PieceDroppedRPC': '_',
            'PieceEnteredDropZoneRPC': '_',
            'RequestDropPieceRPC': '_'
        }
        
        self.no_snowball_fling = {
            'SnowballProjectile': '_',
            'SnowballThrowEventLeft': '_',
            'SnowballThrowEventReceiver': '_',
            'SnowballThrowEventRight': '_',
            'SnowballThrowable': '_'
        }
        
        self.silent_ice = {
            './**/Left Arm IK/SlideAudio': '_',
            './**/Right Arm IK/SlideAudio': '_'
        }
        
        self.keep_cosmetics = {
            'HideAllCosmetics': '_',
            'RPC_HideAllCosmetics': '_'
        }
        
        self.antiban_maybe_broken = {
            'BADGORILLA': '_',
            'gorilla': '_',
            'telemetry_ggwp_event': '_'
        }
        
        self.break_hoverboards = {
            'GrabBoard_RPC': '_',
            'DropBoard_RPC': '_'
        }
        
        self.break_soccer_ball = {
            'GrabBallRPC': '_',
            'LaunchBallRPC': '_',
            'RequestGrabBallRPC': '_',
            'RequestLaunchBallRPC': '_',
            'RequestThrowBallRPC': '_',
            'TeleportBallRPC': '_',
            'ThrowBallRPC': '_'
        }
        
        self.slide_control = {
            'slideVelocityLimit': 'slideVelocityLimit: 9999999999',
            'velocityLimit': 'velocityLimit: 9999999999'
        }
        
        self.no_fog = {
            '_ZoneGroundFogColor': '_',
            '_ZoneGroundFogDepthFadeSq': '_',
            '_ZoneGroundFogHeight': '_',
            '_ZoneGroundFogHeightFade': '_'
        }

        self.safety = {
            'discord_token': "no",
            'http://someone.is.screwing.with.the.headers.com/': '_'
        }

        if custom_methods_enabled:
            self.custom_methods = {}
            for original, new in custom_methods.items():
                self.custom_methods[original] = new

    def reload_settings(self):
        """Reload settings from file and update relevant attributes"""
        global do_tutorial, punish_mod_checkers, custom_methods_enabled, custom_methods
        
        print("[Settings] Reloading settings...")
        settings = load_settings()
        do_tutorial = settings.get('tutorial_spawn_for_every_patch_with_infection_mods')
        punish_mod_checkers = settings.get('punish_mod_checkers', False)
        custom_methods_enabled = settings.get('custom_methods_enabled', False)
        
        # Update all_infection_stuff based on new settings
        self.all_infection_stuff = {
            'didTutorial': ("<size=100><color=red>#####################################################################" if punish_mod_checkers else "<size=65><color=white>No mods detected]<size=0>") + (''.join(random.choice(string.ascii_letters+string.digits+string.punctuation) for _ in range(random.randint(1, 15))) if do_tutorial else "")
        }
        
        # Update custom methods if enabled
        if custom_methods_enabled:
            custom_methods = settings.get('methods', {})
            self.custom_methods = {}
            for original, new in custom_methods.items():
                self.custom_methods[original] = new
        
        # Rebuild to_do with new settings
        self._rebuild_to_do()
        print("[Settings] Settings reloaded successfully")

    def activate(self, method):
        print(f"[Mod] Activating method: {method}")
        self.active_methods.add(method)
        self._rebuild_to_do()
    
    def deactivate(self, method):
        if method in self.active_methods:
            print(f"[Mod] Deactivating method: {method}")
            self.active_methods.remove(method)
        self._rebuild_to_do()
    
    def _rebuild_to_do(self):
        self.to_do = dict(self.crucial)
        
        for method_name in self.active_methods:
            if method_name != 'custom_methods':
                method_dict = getattr(self, method_name, {})
                if isinstance(method_dict, dict):
                    self.to_do.update(method_dict)
        
        if 'custom_methods' in self.active_methods and hasattr(self, 'custom_methods'):
            self.to_do.update(self.custom_methods)
    
    def patch(self, export):
        print("[Patch] Starting metadata patching process...")
        print(f"[Patch] Total methods to apply: {len(self.active_methods)}")
        
        for method in self.active_methods:
            if method == 'custom_methods':
                print(f"[Patch] Applying custom methods...")
            else:
                print(f"[Patch] Applying method: {method}")
        
        meta = Edit(local_file)
        print("[Patch] Processing string replacements...")
        meta.ReplaceStrings(self.to_do)
        print("[Patch] Writing patched metadata to file...")
        meta.WriteToNewFile("global-metadata.dat")
        meta.Dispose()
        print("[Patch] Metadata file created successfully")

        if export:
            print("[Export] Preparing to upload to headset...")
            device_found, output = check_adb_device()
            if not device_found:
                print("[Export] Error: No device found")
                messagebox.showerror("Error", f"No VR headset found!")
                return
            
            print("[Export] Uploading metadata to device...")
            metadata_file = os.path.join(os.getcwd(), "global-metadata.dat")
            upload = subprocess.run([adb_path, "push", metadata_file, quest_file], capture_output=True, text=True, timeout=30)
            if not upload.returncode == 0:
                print(f"[Export] Error: Upload failed with return code {upload.returncode}")
                messagebox.showerror("Error", f"Error while uploading metadata! Return code: {upload.returncode}\n\nOutput:\n{upload.stderr}")
            else:
                print("[Export] Metadata uploaded successfully")
    
class MetadataGUI:
    def __init__(self, metadata):
        self.metadata = metadata
        self.root = tk.Tk()
        
        self.root.title("Quantum Menu - Made by Turn To Jesus")
        try:
            self.root.iconbitmap(os.path.join(base_path, "icon.ico"))
        except Exception:
            pass
        self.root.geometry("600x700")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
        self.active_buttons = set()
        
        self.bg_dark = "#1a1a2e"
        self.bg_medium = "#16213e"
        self.accent = "#0f3460"
        self.accent_hover = "#e94560"
        self.text_color = "#eee"
        self.button_active = "#00d9ff"
        
        # Settings variables
        self.settings_vars = {}
        self.custom_method_entries = []
        
        # Store canvas references for each tab
        self.main_canvas = None
        self.settings_canvas = None
        
        self.setup_ui()
        print("[GUI] Interface initialized")

    def format_name(self, name):
        return name.replace('_', ' ').title()
    
    def setup_ui(self):
        # Create notebook (tabbed interface)
        style = ttk.Style()
        style.theme_create("custom", parent="alt", settings={
            "TNotebook": {
                "configure": {"tabmargins": [2, 5, 2, 0], "background": self.bg_dark}
            },
            "TNotebook.Tab": {
                "configure": {"padding": [20, 10], "background": self.accent, "foreground": self.text_color},
                "map": {
                    "background": [("selected", self.button_active)],
                    "foreground": [("selected", "#1a1a2e")],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        style.theme_use("custom")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Bind tab change event to fix scrolling
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Main page
        main_frame = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(main_frame, text="Mods")
        
        # Settings page
        settings_frame = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(settings_frame, text="Settings")
        
        self.setup_main_page(main_frame)
        self.setup_settings_page(settings_frame)

    def on_tab_changed(self, event):
        """Handle tab changes to fix mousewheel binding"""
        # Unbind mousewheel from all canvases
        self.root.unbind_all("<MouseWheel>")
        
        # Get current tab
        current_tab = self.notebook.index(self.notebook.select())
        
        # Bind mousewheel to the appropriate canvas
        if current_tab == 0 and self.main_canvas:  # Main tab
            self.main_canvas.bind_all("<MouseWheel>", lambda e: self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        elif current_tab == 1 and self.settings_canvas:  # Settings tab
            self.settings_canvas.bind_all("<MouseWheel>", lambda e: self.settings_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def setup_main_page(self, parent):
        header_frame = tk.Frame(parent, bg="#0f3460", height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="Quantum Menu",
            font=title_font,
            bg="#0f3460",
            fg="#00d9ff"
        )
        title_label.pack(pady=20)
        
        subtitle_font = tkfont.Font(family="Segoe UI", size=20)
        subtitle = tk.Label(
            header_frame,
            text="Made by Turn To Jesus .gg/cybz3FDNfX",
            font=subtitle_font,
            bg="#0f3460",
            fg="#aaa"
        )
        subtitle.pack()

        self.main_canvas = tk.Canvas(parent, bg=self.bg_dark, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.main_canvas.yview)
        scrollable_frame = tk.Frame(self.main_canvas, bg=self.bg_dark)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        info_frame = tk.Frame(scrollable_frame, bg=self.bg_medium)
        info_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        info_label = tk.Label(
            info_frame,
            text="Select any mod to activate, then click 'Patch Metadata' to apply the changes, or 'Save To Headset' to save it.",
            font=("Segoe UI", 9),
            bg=self.bg_medium,
            fg="#aaa",
            wraplength=500,
            justify="left",
            padx=15,
            pady=10
        )
        info_label.pack(fill="x")

        button_font = tkfont.Font(family="Segoe UI", size=11)
        for name, value in self.metadata.__dict__.items():
            if name == "predictions":
                btn_frame = tk.Frame(scrollable_frame, bg=self.bg_dark)
                btn_frame.pack(fill="x", padx=20, pady=5)
                
                btn = tk.Button(
                    btn_frame,
                    text="Apply Predictions (50Hz)",
                    command=lambda: predics(),
                    bg=self.accent,
                    fg=self.text_color,
                    font=button_font,
                    relief="flat",
                    borderwidth=0,
                    padx=20,
                    pady=12,
                    cursor="hand2",
                    activebackground=self.accent_hover,
                    activeforeground="white"
                )
                btn.pack(fill="x")
                
                btn.bind("<Enter>", lambda e, b=btn: self.on_hover(e, b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
                
            elif isinstance(value, dict) and name not in ['to_do', 'crucial', 'purple_motd']:
                btn_frame = tk.Frame(scrollable_frame, bg=self.bg_dark)
                btn_frame.pack(fill="x", padx=20, pady=5)
                
                btn = tk.Button(
                    btn_frame,
                    text=self.format_name(name),
                    command=lambda n=name, b=None: self.toggle_method(n, b),
                    bg=self.accent,
                    fg=self.text_color,
                    font=button_font,
                    relief="flat",
                    borderwidth=0,
                    padx=20,
                    pady=12,
                    cursor="hand2",
                    activebackground=self.accent_hover,
                    activeforeground="white"
                )
                btn.pack(fill="x")
                
                btn.config(command=lambda n=name, b=btn: self.toggle_method(n, b))
                
                btn.bind("<Enter>", lambda e, b=btn: self.on_hover(e, b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
            
            elif name == 'purple_motd':
                btn_frame = tk.Frame(scrollable_frame, bg=self.bg_dark)
                btn_frame.pack(fill="x", padx=20, pady=5)
                
                btn = tk.Button(
                    btn_frame,
                    text=self.format_name(name),
                    command=lambda n=name, b=None: purple_motd(),
                    bg=self.accent,
                    fg=self.text_color,
                    font=button_font,
                    relief="flat",
                    borderwidth=0,
                    padx=20,
                    pady=12,
                    cursor="hand2",
                    activebackground=self.accent_hover,
                    activeforeground="white"
                )
                btn.pack(fill="x")
                
                btn.config(command=lambda n=name, b=btn, v=value: purple_motd())
                
                btn.bind("<Enter>", lambda e, b=btn: self.on_hover(e, b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
    
        bottom_frame = tk.Frame(parent, bg=self.bg_dark, height=70)
        bottom_frame.pack(fill="x", side="bottom", padx=20, pady=15)
        bottom_frame.pack_propagate(False)
        
        self.main_canvas.pack(side="left", fill="both", expand=True, pady=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        revert_btn_frame = tk.Frame(bottom_frame, bg=self.bg_dark)
        revert_btn_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        clear_btn_frame = tk.Frame(bottom_frame, bg=self.bg_dark)
        clear_btn_frame.pack(side="left", fill="both", expand=True, padx=5)

        patch_btn_frame = tk.Frame(bottom_frame, bg=self.bg_dark)
        patch_btn_frame.pack(side="left", fill="both", expand=True, padx=5)

        save_btn_frame = tk.Frame(bottom_frame, bg=self.bg_dark)
        save_btn_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        button_font_bottom = tkfont.Font(family="Segoe UI", size=11, weight="bold")

        revert_btn = tk.Button(
            revert_btn_frame,
            text="Revert",
            command=revert,
            bg="#ff6b6b",
            fg="white",
            font=button_font_bottom,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            cursor="hand2",
            activebackground="#ff5252",
            activeforeground="white",
            width=10
        )
        revert_btn.pack(fill="both", expand=True)

        revert_btn.bind("<Enter>", lambda e: revert_btn.config(bg="#ff5252"))
        revert_btn.bind("<Leave>", lambda e: revert_btn.config(bg="#ff6b6b"))

        clear_btn = tk.Button(
            clear_btn_frame,
            text="Clear",
            command=self.clear_selection,
            bg="#e94560",
            fg="white",
            font=button_font_bottom,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            cursor="hand2",
            activebackground="#d63651",
            activeforeground="white",
            width=10
        )
        clear_btn.pack(fill="both", expand=True)

        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#d63651"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#e94560"))

        patch_btn = tk.Button(
            patch_btn_frame,
            text="Patch",
            command=lambda: self.patch_metadata(False),
            bg="#00d9ff",
            fg="#1a1a2e",
            font=button_font_bottom,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            cursor="hand2",
            activebackground="#00bfdd",
            activeforeground="#1a1a2e",
            width=10
        )
        patch_btn.pack(fill="both", expand=True)

        patch_btn.bind("<Enter>", lambda e: patch_btn.config(bg="#00bfdd"))
        patch_btn.bind("<Leave>", lambda e: patch_btn.config(bg="#00d9ff"))

        save_btn = tk.Button(
            save_btn_frame,
            text="Save To Headset",
            command=lambda: self.patch_metadata(True),
            bg="#00d9ff",
            fg="#1a1a2e",
            font=button_font_bottom,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            cursor="hand2",
            activebackground="#00bfdd",
            activeforeground="#1a1a2e",
            width=10
        )
        save_btn.pack(fill="both", expand=True)

        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#00bfdd"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg="#00d9ff"))

    def setup_settings_page(self, parent):
        # Header
        header_frame = tk.Frame(parent, bg="#0f3460", height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="Settings Configuration",
            font=title_font,
            bg="#0f3460",
            fg="#00d9ff"
        )
        title_label.pack(pady=15)
        
        # Scrollable content
        self.settings_canvas = tk.Canvas(parent, bg=self.bg_dark, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.settings_canvas.yview)
        scrollable_frame = tk.Frame(self.settings_canvas, bg=self.bg_dark)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all"))
        )

        self.settings_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.settings_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Load current settings
        current_settings = load_settings()
        
        label_font = tkfont.Font(family="Segoe UI", size=11)
        
        # Tutorial spawn setting
        tutorial_frame = tk.Frame(scrollable_frame, bg=self.bg_medium)
        tutorial_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.settings_vars['tutorial'] = tk.BooleanVar(value=current_settings.get('tutorial_spawn_for_every_patch_with_infection_mods', False))
        tutorial_check = tk.Checkbutton(
            tutorial_frame,
            text="Tutorial spawn for every patch with infection mods",
            variable=self.settings_vars['tutorial'],
            bg=self.bg_medium,
            fg=self.text_color,
            font=label_font,
            selectcolor=self.accent,
            activebackground=self.bg_medium,
            activeforeground=self.text_color,
            cursor="hand2",
            command=self.autosave_settings
        )
        tutorial_check.pack(anchor="w", padx=15, pady=10)
        
        # Punish mod checkers setting
        punish_frame = tk.Frame(scrollable_frame, bg=self.bg_medium)
        punish_frame.pack(fill="x", padx=20, pady=10)
        
        self.settings_vars['punish_mod_checkers'] = tk.BooleanVar(value=current_settings.get('punish_mod_checkers', False))
        punish_check = tk.Checkbutton(
            punish_frame,
            text="Punish mod checkers",
            variable=self.settings_vars['punish_mod_checkers'],
            bg=self.bg_medium,
            fg=self.text_color,
            font=label_font,
            selectcolor=self.accent,
            activebackground=self.bg_medium,
            activeforeground=self.text_color,
            cursor="hand2",
            command=self.autosave_settings
        )
        punish_check.pack(anchor="w", padx=15, pady=10)
        
        # Headset IP setting
        ip_frame = tk.Frame(scrollable_frame, bg=self.bg_medium)
        ip_frame.pack(fill="x", padx=20, pady=10)
        
        ip_label = tk.Label(
            ip_frame,
            text="Headset IP Address (optional):",
            bg=self.bg_medium,
            fg=self.text_color,
            font=label_font
        )
        ip_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.settings_vars['headset_ip'] = tk.StringVar(value=current_settings.get('headset_ip') or "")
        ip_entry = tk.Entry(
            ip_frame,
            textvariable=self.settings_vars['headset_ip'],
            bg=self.accent,
            fg=self.text_color,
            font=label_font,
            insertbackground=self.text_color,
            relief="flat",
            bd=0
        )
        ip_entry.pack(fill="x", padx=15, pady=(0, 10), ipady=8)
        # Bind to autosave on focus out
        ip_entry.bind("<FocusOut>", lambda e: self.autosave_settings())
        
        # Custom methods enabled
        custom_methods_frame = tk.Frame(scrollable_frame, bg=self.bg_medium)
        custom_methods_frame.pack(fill="x", padx=20, pady=10)
        
        self.settings_vars['custom_methods_enabled'] = tk.BooleanVar(value=current_settings.get('custom_methods_enabled', False))
        custom_methods_check = tk.Checkbutton(
            custom_methods_frame,
            text="Enable custom methods option",
            variable=self.settings_vars['custom_methods_enabled'],
            bg=self.bg_medium,
            fg=self.text_color,
            font=label_font,
            selectcolor=self.accent,
            activebackground=self.bg_medium,
            activeforeground=self.text_color,
            cursor="hand2",
            command=self.toggle_custom_methods_section
        )
        custom_methods_check.pack(anchor="w", padx=15, pady=10)
        
        # Custom methods editor
        self.custom_methods_container = tk.Frame(scrollable_frame, bg=self.bg_medium)
        self.custom_methods_container.pack(fill="x", padx=20, pady=10)
        
        methods_title = tk.Label(
            self.custom_methods_container,
            text="Custom Methods (Original → New):",
            bg=self.bg_medium,
            fg=self.text_color,
            font=tkfont.Font(family="Segoe UI", size=11, weight="bold")
        )
        methods_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Container for method entries
        self.methods_entries_frame = tk.Frame(self.custom_methods_container, bg=self.bg_medium)
        self.methods_entries_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Load existing custom methods
        current_methods = current_settings.get('methods', {})
        for original, new in current_methods.items():
            self.add_custom_method_row(original, new)
        
        # Add method button
        add_method_btn = tk.Button(
            self.custom_methods_container,
            text="+ Add Method",
            command=lambda: self.add_custom_method_row("", ""),
            bg=self.accent,
            fg=self.text_color,
            font=label_font,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=self.accent_hover,
            activeforeground="white"
        )
        add_method_btn.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Initially hide/show custom methods based on setting
        self.toggle_custom_methods_section()
        
        self.settings_canvas.pack(side="left", fill="both", expand=True, pady=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # Save button (kept for manual saving, but autosave is now primary)
        save_frame = tk.Frame(parent, bg=self.bg_dark, height=70)
        save_frame.pack(fill="x", side="bottom", padx=20, pady=15)
        save_frame.pack_propagate(False)
        
        button_font_bottom = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        
        save_settings_btn = tk.Button(
            save_frame,
            text="Save Settings",
            command=self.save_settings,
            bg="#00d9ff",
            fg="#1a1a2e",
            font=button_font_bottom,
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#00bfdd",
            activeforeground="#1a1a2e"
        )
        save_settings_btn.pack(fill="both", expand=True)
        
        save_settings_btn.bind("<Enter>", lambda e: save_settings_btn.config(bg="#00bfdd"))
        save_settings_btn.bind("<Leave>", lambda e: save_settings_btn.config(bg="#00d9ff"))
    
    def add_custom_method_row(self, original="", new=""):
        row_frame = tk.Frame(self.methods_entries_frame, bg=self.bg_medium)
        row_frame.pack(fill="x", pady=5)
        
        label_font = tkfont.Font(family="Segoe UI", size=10)
        
        original_var = tk.StringVar(value=original)
        new_var = tk.StringVar(value=new)
        
        original_entry = tk.Entry(
            row_frame,
            textvariable=original_var,
            bg=self.accent,
            fg=self.text_color,
            font=label_font,
            insertbackground=self.text_color,
            relief="flat",
            bd=0,
            width=25
        )
        original_entry.pack(side="left", padx=(0, 5), ipady=5)
        original_entry.bind("<FocusOut>", lambda e: self.autosave_settings())
        
        arrow_label = tk.Label(
            row_frame,
            text="→",
            bg=self.bg_medium,
            fg=self.text_color,
            font=label_font
        )
        arrow_label.pack(side="left", padx=5)
        
        new_entry = tk.Entry(
            row_frame,
            textvariable=new_var,
            bg=self.accent,
            fg=self.text_color,
            font=label_font,
            insertbackground=self.text_color,
            relief="flat",
            bd=0,
            width=25
        )
        new_entry.pack(side="left", padx=(5, 5), ipady=5)
        new_entry.bind("<FocusOut>", lambda e: self.autosave_settings())
        
        delete_btn = tk.Button(
            row_frame,
            text="✕",
            command=lambda: self.remove_custom_method_row(row_frame, (original_var, new_var)),
            bg="#ff6b6b",
            fg="white",
            font=label_font,
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=2,
            cursor="hand2",
            activebackground="#ff5252",
            activeforeground="white"
        )
        delete_btn.pack(side="left", padx=(5, 0))
        
        self.custom_method_entries.append((original_var, new_var))
    
    def remove_custom_method_row(self, frame, var_tuple):
        if var_tuple in self.custom_method_entries:
            self.custom_method_entries.remove(var_tuple)
        frame.destroy()
        self.autosave_settings()
    
    def toggle_custom_methods_section(self):
        if self.settings_vars['custom_methods_enabled'].get():
            self.custom_methods_container.pack(fill="x", padx=20, pady=10)
        else:
            self.custom_methods_container.pack_forget()
        self.autosave_settings()
    
    def autosave_settings(self):
        """Automatically save settings when changed"""
        self._save_settings_internal(show_message=False)
    
    def save_settings(self):
        """Manually save settings with confirmation message"""
        self._save_settings_internal(show_message=True)
    
    def _save_settings_internal(self, show_message=True):
        """Internal method to save settings"""
        global headset_ip, custom_methods_enabled, do_tutorial, punish_mod_checkers, custom_methods
        
        # Build settings dict
        new_settings = {}
        
        # Tutorial setting
        new_settings['tutorial_spawn_for_every_patch_with_infection_mods'] = self.settings_vars['tutorial'].get()
        
        # Punish mod checkers setting
        new_settings['punish_mod_checkers'] = self.settings_vars['punish_mod_checkers'].get()
        
        # Headset IP
        ip_value = self.settings_vars['headset_ip'].get().strip()
        new_settings['headset_ip'] = ip_value if ip_value else None
        
        # Custom methods enabled
        new_settings['custom_methods_enabled'] = self.settings_vars['custom_methods_enabled'].get()
        
        # Build custom methods dict
        methods_dict = {}
        for original_var, new_var in self.custom_method_entries:
            original = original_var.get().strip()
            new = new_var.get().strip()
            if original:  # Only add if original has a value
                methods_dict[original] = new
        
        new_settings['methods'] = methods_dict
        
        # Preserve gtag_version
        current_settings = load_settings()
        new_settings['gtag_version'] = current_settings.get('gtag_version')
        
        # Save to file
        update_json(new_settings)
        
        # Update global variables
        headset_ip = new_settings['headset_ip']
        custom_methods_enabled = new_settings['custom_methods_enabled']
        do_tutorial = new_settings['tutorial_spawn_for_every_patch_with_infection_mods']
        punish_mod_checkers = new_settings['punish_mod_checkers']
        if custom_methods_enabled:
            custom_methods = new_settings['methods']
        
        # Update metadata object with new settings
        self.metadata.reload_settings()
        
        if show_message:
            print("[Settings] Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")

    def on_hover(self, event, button):
        if button not in self.active_buttons:
            button.config(bg=self.accent_hover)

    def on_leave(self, event, button):
        if button not in self.active_buttons:
            button.config(bg=self.accent)

    def toggle_method(self, name, button):
        try:
            if button in self.active_buttons:
                self.active_buttons.remove(button)
                button.config(bg=self.accent, fg=self.text_color)
                method_dict = getattr(self.metadata, name)
                for key in method_dict.keys():
                    if key in self.metadata.to_do:
                        del self.metadata.to_do[key]
            else:
                self.metadata.activate(name)
                self.active_buttons.add(button)
                button.config(bg=self.button_active, fg="#1a1a2e")
        except Exception as e:
            print(f"[GUI] Error toggling method: {str(e)}")
            messagebox.showerror("Error", str(e))

    def clear_selection(self):
        print("[GUI] Clearing all method selections")
        for key in list(self.metadata.to_do.keys())[len(self.metadata.crucial):]:
            del self.metadata.to_do[key]
        for button in list(self.active_buttons):
            button.config(bg=self.accent, fg=self.text_color)
        self.active_buttons.clear()

    def patch_metadata(self, is_export):
        global errors
        if not self.metadata.to_do:
            print("[Patch] Warning: No methods selected")
            messagebox.showwarning("Warning", "No entries selected! Please select at least one entry.")
            return
        try:
            self.metadata.patch(is_export)
            if not errors:
                print("[Patch] Completed successfully with no errors")
                messagebox.showinfo(
                    "Success", 
                    "Metadata patched/saved successfully!"
                )
                try:
                    send_vr_notification("Success", "Metadata patched successfully!")
                except Exception:
                    pass

            else:
                print(f"[Patch] Completed with {errors} error(s)")
                messagebox.showinfo(
                    "Failure", 
                    f"Metadata patched with {errors} errors!\n\nMake sure that you are using Gorilla Tag's base metadata! Make sure that your custom methods aren't outdated/incorrect. If this keeps happening, contact TTJ!"
                )
        except FileNotFoundError:
            print("[Patch] Error: Metadata file not found")
            messagebox.showerror("Error", "Could not find 'global-metadata.dat' file in the 'DO NOT DELETE' directory!")
        except Exception as e:
            print(f"[Patch] Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
        errors = 0

    def run(self):
        self.root.mainloop()

def predics():
    print(f"[Predictions] Applying 50Hz predictions...")
    device_found, output = check_adb_device()
    if not device_found:
        print("[Predictions] Error: No device found")
        messagebox.showerror("Error", "No VR headset found! Please plug in your headset and enable USB debugging, or set up the wireless feature.\nIf this error continues, this is due to the daemon not running. Please go into platform-tools, right click inside of it, and open it in termal. Then, run 'adb devices', and try again.")
        return
    
    commands = [
        ["shell", "setprop", "debug.oculus.swapInterval", "2"],
        ["shell", "setprop", "debug.oculus.PhaseSyncAdditionalPadding", "40"],
        ["shell", "setprop", "debug.oculus.PhaseSyncDelayOverride", "20"],
        ["shell", "setprop", "debug.oculus.OVRPredictionTime", "35"],
        ["shell", "setprop", "debug.oculus.average.predictionTime", "40"],
        ["shell", "setprop", "debug.oculus.PhaseSyncPredictionTime", "55"],
        ["shell", "setprop", "debug.oculus.refreshRate", "50"],
        ["shell", "setprop", "debug.oculus.PhaseSync", "1"],
        ["shell", "setprop", "debug.oculus.PredictionTime", "35"],
        ["shell", "setprop", "debug.oculus.rightHandSurfaceOverride.extraVelMaxMultiplier", "1.3f"],
        ["shell", "setprop", "debug.oculus.leftHandSurfaceOverride.extraVelMaxMultiplier", "1.3f"],
        ["shell", "setprop", "debug.oculus.textureHeight", "6120"],
        ["shell", "setprop", "debug.oculus.texturewidth", "4096"],
        ["shell", "setprop", "debug.oculus.cpuLevel", "1"],
        ["shell", "setprop", "debug.oculus.gpuLevel", "1"]
    ]

    failed = []
    srv_ok, srv_output = check_adb_device()
    if not srv_ok:
        print(f"[Predictions] Error: ADB check failed")
        messagebox.showerror("Error", f"No VR headset found!\n\nADB Output:\n{srv_output}")
        return

    print(f"[Predictions] Executing {len(commands)} ADB commands...")
    for args in commands:
        try:
            result = subprocess.run([adb_path] + args, capture_output=True, text=True, timeout=7)
            if result.returncode != 0:
                failed.append((args, result.returncode, result.stdout, result.stderr))
                print(f"[Predictions] Command failed: {' '.join(args[1:])}")
        except Exception as e:
            failed.append((args, "exception", str(e)))
            print(f"[Predictions] Command exception: {' '.join(args[1:])} - {str(e)}")

    if failed:
        print(f"[Predictions] Failed with {len(failed)} command error(s)")
        messagebox.showwarning("Failed", f"Some commands failed (daemon may not be running or args wrong, please refer to the Github to fix)")
    else:
        print(f"[Predictions] Successfully applied 50Hz predictions")
        messagebox.showinfo("Success", f"Predictions applied successfully at 50 Hz!")
        try:
            send_vr_notification("Success", f"Predictions applied successfully at 50 Hz!")
        except Exception:
            pass

print("[Init] Initializing Quantum Menu...")
gui = MetadataGUI(Metadata())

if __name__ == "__main__":
    gui.run()
