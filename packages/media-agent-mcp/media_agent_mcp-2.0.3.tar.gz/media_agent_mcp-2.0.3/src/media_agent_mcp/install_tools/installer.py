import os
import subprocess
import platform
import shutil
import sys
from typing import Dict, Any, Tuple, Optional, List

try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None


def get_common_ffmpeg_paths() -> List[str]:
    """
    Get common installation paths for ffmpeg based on the operating system.
    
    Returns:
        list: List of common ffmpeg installation paths
    """
    system = platform.system().lower()
    common_paths = []
    
    if system == 'darwin':  # macOS
        common_paths = [
            '/usr/local/bin',
            '/opt/homebrew/bin',
            '/usr/bin',
            '/opt/local/bin',
            '/sw/bin'
        ]
    elif system == 'linux':
        common_paths = [
            '/usr/local/bin',
            '/usr/bin',
            '/bin',
            '/opt/bin',
            '/snap/bin',
            '/usr/local/sbin',
            '/usr/sbin'
        ]
    elif system == 'windows':
        common_paths = [
            'C:\\Program Files\\ffmpeg\\bin',
            'C:\\ffmpeg\\bin',
            'C:\\tools\\ffmpeg\\bin',
            'C:\\ProgramData\\chocolatey\\bin'
        ]
    
    return common_paths


def refresh_path_environment() -> bool:
    """
    Refresh the PATH environment variable by adding common ffmpeg installation paths.
    
    Returns:
        bool: True if PATH was updated and ffmpeg is now found, False otherwise
    """
    current_path = os.environ.get('PATH', '')
    common_paths = get_common_ffmpeg_paths()
    
    # Check which paths exist and contain ffmpeg
    valid_paths = []
    for path in common_paths:
        if os.path.exists(path):
            ffmpeg_path = os.path.join(path, 'ffmpeg')
            if platform.system().lower() == 'windows':
                ffmpeg_path += '.exe'
            
            if os.path.exists(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
                if path not in current_path:
                    valid_paths.append(path)
    
    # Add valid paths to PATH
    if valid_paths:
        path_separator = ';' if platform.system().lower() == 'windows' else ':'
        new_paths = path_separator.join(valid_paths)
        if current_path:
            os.environ['PATH'] = new_paths + path_separator + current_path
        else:
            os.environ['PATH'] = new_paths
        
        print(f"Added to PATH: {', '.join(valid_paths)}")
        
        # Clear shutil.which cache to force re-detection
        if hasattr(shutil.which, 'cache_clear'):
            shutil.which.cache_clear()
        
        # Check if ffmpeg is now available
        return shutil.which('ffmpeg') is not None
    
    return False


def which_ffmpeg() -> Optional[str]:
    """
    Args:
        None
    
    Returns:
        result: Path to ffmpeg executable if found, else None
    """
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    # try imageio-ffmpeg provided binary
    if imageio_ffmpeg is not None:
        try:
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return exe
        except Exception:
            pass
    return None


def which_ffprobe() -> Optional[str]:
    """
    Args:
        None
    
    Returns:
        result: Path to ffprobe executable if found, else None
    """
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    # try imageio-ffmpeg provided binary (ffprobe is usually in the same directory)
    if imageio_ffmpeg is not None:
        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_exe and os.path.exists(ffmpeg_exe):
                ffprobe_exe = os.path.join(os.path.dirname(ffmpeg_exe), "ffprobe")
                if os.path.exists(ffprobe_exe):
                    return ffprobe_exe
                # On Windows, try with .exe extension
                ffprobe_exe_win = ffprobe_exe + ".exe"
                if os.path.exists(ffprobe_exe_win):
                    return ffprobe_exe_win
        except Exception:
            pass
    return None


def get_tool_version(tool_path: str) -> str:
    """
    Args:
        tool_path: path to tool executable
    
    Returns:
        result: version string from tool -version
    """
    try:
        result = subprocess.run([tool_path, "-version"], 
                              capture_output=True, text=True, check=True)
        version_line = result.stdout.split('\n')[0]
        # Extract version number from the first line
        parts = version_line.split(' ')
        for i, part in enumerate(parts):
            if 'version' in part.lower() and i + 1 < len(parts):
                return parts[i + 1]
        # Fallback: return the third word if available
        if len(parts) > 2:
            return parts[2]
        return 'unknown'
    except Exception as e:
        return f"unknown ({e})"


def check_tools_installed() -> Dict[str, Any]:
    """
    Check if ffmpeg and ffprobe are installed and available.
    
    Returns:
        dict: Status information for both tools
    """
    ffmpeg_path = which_ffmpeg()
    ffprobe_path = which_ffprobe()
    
    result = {
        'ffmpeg': {
            'installed': ffmpeg_path is not None,
            'path': ffmpeg_path,
            'version': None,
            'source': None
        },
        'ffprobe': {
            'installed': ffprobe_path is not None,
            'path': ffprobe_path,
            'version': None,
            'source': None
        }
    }
    
    # Get version and source information
    if ffmpeg_path:
        result['ffmpeg']['version'] = get_tool_version(ffmpeg_path)
        if 'imageio' in ffmpeg_path:
            result['ffmpeg']['source'] = 'imageio-ffmpeg'
        else:
            result['ffmpeg']['source'] = 'system'
    
    if ffprobe_path:
        result['ffprobe']['version'] = get_tool_version(ffprobe_path)
        if 'imageio' in ffprobe_path:
            result['ffprobe']['source'] = 'imageio-ffmpeg'
        else:
            result['ffprobe']['source'] = 'system'
    
    return result


def install_imageio_ffmpeg() -> Tuple[bool, str]:
    """
    Install imageio-ffmpeg package using pip.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        print("Installing imageio-ffmpeg package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "imageio-ffmpeg"],
            capture_output=True, text=True, check=True
        )
        print("imageio-ffmpeg installed successfully")
        
        # Try to import and verify
        try:
            import importlib
            global imageio_ffmpeg
            imageio_ffmpeg = importlib.import_module('imageio_ffmpeg')
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return True, ""
            else:
                return False, "imageio-ffmpeg installed but ffmpeg binary not found"
        except Exception as e:
            return False, f"imageio-ffmpeg installed but import failed: {e}"
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install imageio-ffmpeg: {e}"
        if e.stderr:
            error_msg += f"\nStderr: {e.stderr}"
        if e.stdout:
            error_msg += f"\nStdout: {e.stdout}"
        return False, error_msg
    except Exception as e:
        return False, f"Unexpected error installing imageio-ffmpeg: {e}"


def install_system_ffmpeg() -> Tuple[bool, str]:
    """
    Install ffmpeg using system package managers.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    system = platform.system().lower()
    
    try:
        if system == 'darwin':  # macOS
            if shutil.which('brew') is None:
                return False, "Homebrew is not installed. Please install Homebrew first: https://brew.sh/"
            
            print("Installing ffmpeg using Homebrew...")
            result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                                  capture_output=True, text=True, check=True)
            print("ffmpeg installed successfully via Homebrew")
            
            # Try to refresh PATH to make tools immediately available
            refresh_path_environment()
            return True, ""
            
        elif system == 'linux':
            # Try different package managers
            managers = [
                ('apt-get', ['sudo', 'apt-get', 'update'], ['sudo', 'apt-get', 'install', '-y', 'ffmpeg']),
                ('yum', None, ['sudo', 'yum', 'install', '-y', 'ffmpeg']),
                ('dnf', None, ['sudo', 'dnf', 'install', '-y', 'ffmpeg']),
                ('pacman', None, ['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg']),
                ('zypper', None, ['sudo', 'zypper', 'install', '-y', 'ffmpeg'])
            ]
            
            for manager, update_cmd, install_cmd in managers:
                if shutil.which(manager) is not None:
                    print(f"Installing ffmpeg using {manager}...")
                    try:
                        if update_cmd:
                            subprocess.run(update_cmd, capture_output=True, text=True, check=True)
                        subprocess.run(install_cmd, capture_output=True, text=True, check=True)
                        print(f"ffmpeg installed successfully via {manager}")
                        
                        # Try to refresh PATH to make tools immediately available
                        refresh_path_environment()
                        return True, ""
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Failed to install via {manager}: {e}"
                        if e.stderr:
                            error_msg += f"\nStderr: {e.stderr}"
                        continue
            
            return False, "No supported package manager found (tried: apt-get, yum, dnf, pacman, zypper)"
                
        elif system == 'windows':
            if shutil.which('choco') is not None:
                print("Installing ffmpeg using Chocolatey...")
                result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                                      capture_output=True, text=True, check=True)
                print("ffmpeg installed successfully via Chocolatey")
                
                # Try to refresh PATH to make tools immediately available
                refresh_path_environment()
                return True, ""
            elif shutil.which('scoop') is not None:
                print("Installing ffmpeg using Scoop...")
                result = subprocess.run(['scoop', 'install', 'ffmpeg'], 
                                      capture_output=True, text=True, check=True)
                print("ffmpeg installed successfully via Scoop")
                
                # Try to refresh PATH to make tools immediately available
                refresh_path_environment()
                return True, ""
            else:
                return False, "No package manager found. Please install Chocolatey (https://chocolatey.org/) or Scoop (https://scoop.sh/)"
        
        else:
            return False, f"Unsupported operating system: {system}"
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Error installing ffmpeg: {e}"
        if e.stderr:
            error_msg += f"\nStderr: {e.stderr}"
        if e.stdout:
            error_msg += f"\nStdout: {e.stdout}"
        return False, error_msg
    except Exception as e:
        return False, f"Unexpected error during installation: {e}"


def install_ffmpeg_tools() -> Tuple[bool, str]:
    """
    Install ffmpeg and ffprobe using multiple fallback strategies.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    errors = []
    
    # Strategy 1: Try imageio-ffmpeg if available
    if imageio_ffmpeg is not None:
        try:
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                print("Found ffmpeg via imageio-ffmpeg")
                return True, ""
        except Exception as e:
            errors.append(f"imageio-ffmpeg check failed: {e}")
    else:
        errors.append("imageio-ffmpeg not available")
    
    # Strategy 2: Try to install imageio-ffmpeg
    print("Attempting to install imageio-ffmpeg...")
    success, error = install_imageio_ffmpeg()
    if success:
        return True, ""
    else:
        errors.append(f"imageio-ffmpeg installation failed: {error}")
    
    # Strategy 3: Try system package managers
    print("Attempting to install via system package manager...")
    success, error = install_system_ffmpeg()
    if success:
        return True, ""
    else:
        errors.append(f"System installation failed: {error}")
    
    # All strategies failed
    combined_error = "All installation strategies failed:\n" + "\n".join(f"- {err}" for err in errors)
    combined_error += "\n\nManual installation options:"
    combined_error += "\n1. Install imageio-ffmpeg: pip install imageio-ffmpeg"
    combined_error += "\n2. Download ffmpeg from https://ffmpeg.org/download.html"
    
    system = platform.system().lower()
    if system == 'darwin':
        combined_error += "\n3. Install Homebrew and run: brew install ffmpeg"
    elif system == 'linux':
        combined_error += "\n3. Use your system package manager: sudo apt install ffmpeg (Ubuntu/Debian)"
    elif system == 'windows':
        combined_error += "\n3. Install Chocolatey and run: choco install ffmpeg"
    
    return False, combined_error


def install_tools_plugin() -> Dict[str, Any]:
    """
    Install development tools (ffmpeg and ffprobe) if not present, or return version and path if already installed.
    
    Returns:
        dict: JSON response with status, data (tools info), and message
    """
    try:
        # Check current installation status
        tools_status = check_tools_installed()
        
        # Check if both tools are already installed
        if tools_status['ffmpeg']['installed'] and tools_status['ffprobe']['installed']:
            return {
                "status": "success",
                "data": {
                    "tools_installed": True,
                    "ffmpeg": tools_status['ffmpeg'],
                    "ffprobe": tools_status['ffprobe']
                },
                "message": f"Tools already installed - ffmpeg: {tools_status['ffmpeg']['version']} ({tools_status['ffmpeg']['source']}), ffprobe: {tools_status['ffprobe']['version']} ({tools_status['ffprobe']['source']})"
            }
        
        # Some tools are missing, attempt installation
        missing_tools = []
        if not tools_status['ffmpeg']['installed']:
            missing_tools.append('ffmpeg')
        if not tools_status['ffprobe']['installed']:
            missing_tools.append('ffprobe')
        
        print(f"Missing tools: {', '.join(missing_tools)}. Attempting to install...")
        
        success, error_message = install_ffmpeg_tools()
        if success:
            # Verify installation and get updated status
            updated_status = check_tools_installed()
            
            if updated_status['ffmpeg']['installed'] and updated_status['ffprobe']['installed']:
                return {
                    "status": "success",
                    "data": {
                        "tools_installed": True,
                        "ffmpeg": updated_status['ffmpeg'],
                        "ffprobe": updated_status['ffprobe']
                    },
                    "message": f"Tools installed successfully - ffmpeg: {updated_status['ffmpeg']['version']} ({updated_status['ffmpeg']['source']}), ffprobe: {updated_status['ffprobe']['version']} ({updated_status['ffprobe']['source']})"
                }
            else:
                # Try to refresh PATH environment and check again
                print("Tools not found in PATH, attempting to refresh environment...")
                path_refreshed = refresh_path_environment()
                
                if path_refreshed:
                    # Check again after PATH refresh
                    final_status = check_tools_installed()
                    if final_status['ffmpeg']['installed'] and final_status['ffprobe']['installed']:
                        return {
                            "status": "success",
                            "data": {
                                "tools_installed": True,
                                "ffmpeg": final_status['ffmpeg'],
                                "ffprobe": final_status['ffprobe']
                            },
                            "message": f"Tools found after PATH refresh - ffmpeg: {final_status['ffmpeg']['version']} ({final_status['ffmpeg']['source']}), ffprobe: {final_status['ffprobe']['version']} ({final_status['ffprobe']['source']})"
                        }
                
                return {
                    "status": "error",
                    "data": None,
                    "message": "Installation completed but tools not found. Tried refreshing PATH environment but tools are still not accessible. Please manually add the installation directory to your PATH or restart your terminal."
                }
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Failed to install tools automatically. Error details:\n{error_message}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error in tools installation plugin: {str(e)}"
        }