"""Video subtitle processing module.

This module provides video subtitle functionality including adding subtitles to videos.
Uses FFmpeg for subtitle rendering with automatic positioning and styling optimization.
"""
import logging
import os

import time
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import requests
from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url, get_video_info
from media_agent_mcp.install_tools.installer import which_ffmpeg

logger = logging.getLogger(__name__)

FFMPEG_PATH = which_ffmpeg()
FFPROBE_PATH = ""
if FFMPEG_PATH:
    FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe")




def parse_srt_content(srt_content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT subtitle content into structured data.
    
    Args:
        srt_content: SRT format subtitle content
        
    Returns:
        List of subtitle entries with start_time, end_time, and text
    """
    subtitles = []
    entries = srt_content.strip().split('\n\n')
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if len(lines) < 3:
            continue
            
        try:
            # Parse time range (format: 00:00:01,000 --> 00:00:04,000)
            time_line = lines[1]
            start_str, end_str = time_line.split(' --> ')
            
            # Convert time to seconds
            start_time = time_str_to_seconds(start_str)
            end_time = time_str_to_seconds(end_str)
            
            # Get subtitle text (may span multiple lines)
            text = '\n'.join(lines[2:])
            
            subtitles.append({
                'start_time': start_time,
                'end_time': end_time,
                'text': text
            })
            
        except Exception as e:
            logger.warning(f"Failed to parse subtitle entry: {entry[:50]}... Error: {e}")
            continue
    
    return subtitles


def time_str_to_seconds(time_str: str) -> float:
    """
    Convert SRT time format to seconds.
    
    Args:
        time_str: Time string in format "HH:MM:SS,mmm"
        
    Returns:
        Time in seconds as float
    """
    # Replace comma with dot for milliseconds
    time_str = time_str.replace(',', '.')
    
    # Split into time parts
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    return hours * 3600 + minutes * 60 + seconds


def detect_chinese_text(text: str) -> bool:
    """
    Detect if text contains Chinese characters.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains Chinese characters, False otherwise
    """
    for char in text:
        # Check for common CJK (Chinese, Japanese, Korean) Unicode ranges
        code = ord(char)
        if (0x4e00 <= code <= 0x9fff or    # CJK Unified Ideographs
            0x3400 <= code <= 0x4dbf or    # CJK Extension A
            0x20000 <= code <= 0x2a6df or  # CJK Extension B
            0x2a700 <= code <= 0x2b73f or  # CJK Extension C
            0x2b740 <= code <= 0x2b81f or  # CJK Extension D
            0x2b820 <= code <= 0x2ceaf or  # CJK Extension E
            0x2ceb0 <= code <= 0x2ebef or  # CJK Extension F
            0x30000 <= code <= 0x3134f or  # CJK Extension G
            0x31350 <= code <= 0x323af):   # CJK Extension H
            return True
    return False


def get_chinese_font_path() -> str:
    """
    Get Chinese font path for subtitle rendering.
    
    Returns:
        Path to a Chinese font file, or empty string if none found
    """
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Try Chinese fonts on macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
    elif system == "Linux":
        # Try Chinese fonts on Linux (including server distributions)
        font_paths = [
            # Noto fonts (Google's comprehensive font family)
            "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/TTF/NotoSansCJK-Regular.ttc",
            
            # WenQuanYi fonts (popular open source Chinese fonts)
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
            "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
            
            # Ubuntu/Debian specific paths
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            
            # CentOS/RHEL specific paths
            "/usr/share/fonts/cjkuni-ukai/ukai.ttc",
            "/usr/share/fonts/cjkuni-uming/uming.ttc",
            
            # Alternative paths
            "/usr/share/fonts/chinese/TrueType/ukai.ttc",
            "/usr/share/fonts/chinese/TrueType/uming.ttc",
            "/usr/share/fonts/TTF/wqy-zenhei.ttc",
            "/usr/share/fonts/TTF/wqy-microhei.ttc",
            
            # Note: Removed DejaVu fallback to ensure proper Chinese font detection/download
        ]
    elif system == "Windows":
        # Try Chinese fonts on Windows
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simkai.ttf",
            "C:/Windows/Fonts/simfang.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/arial.ttf"
        ]
    else:
        font_paths = []
    
    # Find first available Chinese font
    for font_path in font_paths:
        if os.path.exists(font_path):
            logger.info(f"Found Chinese font: {font_path}")
            return font_path
    
    # Try auto-download to cache as fallback
    try:
        cached = download_chinese_font_to_cache()
        if cached and os.path.exists(cached):
            logger.info(f"Downloaded Chinese font to cache: {cached}")
            return cached
    except Exception as e:
        logger.warning(f"Auto-download Chinese font failed: {e}")
    
    # No Chinese font found
    logger.warning("No Chinese font found")
    return ""


def get_system_font_path() -> str:
    """
    Get system font path for subtitle rendering.
    
    Returns:
        Path to a system font file, or empty string if none found
    """
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Try common fonts on macOS
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Times.ttc"
        ]
    elif system == "Linux":
        # Try common fonts on Linux
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        ]
    elif system == "Windows":
        # Try common fonts on Windows
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/times.ttf"
        ]
    else:
        font_paths = []
    
    # Find first available font
    for font_path in font_paths:
        if os.path.exists(font_path):
            logger.info(f"Found system font: {font_path}")
            return font_path
    
    # No system font found
    logger.warning("No system font found")
    return ""


def calculate_subtitle_style(video_width: int, video_height: int, subtitle_text: str = "") -> Dict[str, Any]:
    """
    Calculate optimal subtitle styling based on video resolution.
    
    Args:
        video_width: Video width in pixels
        video_height: Video height in pixels
        subtitle_text: Subtitle text content for font selection
        
    Returns:
        Dictionary containing font size, position, and styling parameters
    """
    # Base font size calculation (proportional to video height)
    base_font_size = max(16, int(video_height * 0.04))  # 4% of video height
    
    # Position subtitle in lower third of video
    y_position = int(video_height * 0.85)  # 85% down from top
    
    # Padding from edges
    x_padding = int(video_width * 0.05)  # 5% padding from sides
    
    # Box padding for background
    box_padding = max(8, int(base_font_size * 0.3))
    
    # Smart font selection based on content
    has_chinese = detect_chinese_text(subtitle_text) if subtitle_text else False
    
    if has_chinese:
        # Prefer Chinese font for Chinese content
        chinese_font = get_chinese_font_path()
        font_family = chinese_font if chinese_font else get_system_font_path()
    else:
        # Use system font for non-Chinese content
        font_family = get_system_font_path()
    
    # Fallback to Arial if no font found
    if not font_family:
        font_family = "Arial"
    
    return {
        'font_size': base_font_size,
        'font_family': font_family,
        'font_color': 'white',
        'outline_color': 'black',
        'outline_width': max(1, int(base_font_size * 0.08)),
        'background_color': 'black@0.6',  # Semi-transparent black background
        'x_position': 'center',  # Center horizontally
        'y_position': y_position,
        'x_padding': x_padding,
        'box_padding': box_padding,
        'line_spacing': int(base_font_size * 0.2),
        'has_chinese': has_chinese
    }


def estimate_text_width(text: str, font_size: int) -> int:
    """
    Estimate text width in pixels based on font size and content.
    
    Args:
        text: Text content
        font_size: Font size in pixels
        
    Returns:
        Estimated width in pixels
    """
    # Simple estimation: characters are roughly 0.6 times the font size in width
    return int(len(text) * font_size * 0.6)


def split_text_into_lines(text: str, max_width: int, font_size: int) -> List[str]:
    """
    Split text into multiple lines based on maximum width.
    
    Args:
        text: Text content to split
        max_width: Maximum width in pixels
        font_size: Font size in pixels
        
    Returns:
        List of text lines
    """
    # If text already contains line breaks, split by them first
    paragraphs = text.split('\n')
    lines = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append('')
            continue
            
        # Check if paragraph fits in one line
        if estimate_text_width(paragraph, font_size) <= max_width:
            lines.append(paragraph)
            continue
        
        # Break at word boundaries
        words = paragraph.split(' ')
        current_line = ''
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            if estimate_text_width(test_line, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    
    return lines


def check_drawtext_filter_available() -> bool:
    """
    Check if FFmpeg supports the drawtext filter.
    
    Returns:
        True if drawtext filter is available, False otherwise
    """
    try:
        import subprocess
        result = subprocess.run([FFMPEG_PATH, '-filters'], capture_output=True, text=True, timeout=10)
        return 'drawtext' in result.stdout
    except Exception:
        return False


def create_srt_file(subtitles: List[Dict[str, Any]], srt_path: str, font_path: str = None) -> None:
    """
    Create an SRT file from subtitle data with optional font specification.
    
    Args:
        subtitles: List of subtitle entries
        srt_path: Path to save the SRT file
        font_path: Optional path to font file for Chinese support
    """
    def seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def seconds_to_ass_time(seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.cc)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    with open(srt_path, 'w', encoding='utf-8') as f:
        # Add ASS-style header for better font control if font_path is provided
        if font_path and os.path.exists(font_path):
            f.write("[Script Info]\n")
            f.write("Title: Generated Subtitles\n")
            f.write("ScriptType: v4.00+\n\n")
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            font_name = os.path.splitext(os.path.basename(font_path))[0]
            f.write(f"Style: Default,{font_name},20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n")
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for i, subtitle in enumerate(subtitles):
                start_time = seconds_to_ass_time(subtitle['start_time'])
                end_time = seconds_to_ass_time(subtitle['end_time'])
                text = subtitle['text'].replace('\n', '\\N')
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
        else:
            # Standard SRT format
            for i, subtitle in enumerate(subtitles, 1):
                start_time = seconds_to_srt_time(subtitle['start_time'])
                end_time = seconds_to_srt_time(subtitle['end_time'])
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle['text']}\n\n")


def create_subtitle_filter(subtitles: List[Dict[str, Any]], style: Dict[str, Any], video_width: int) -> str:
    """
    Create FFmpeg subtitle filter string with multi-line support.
    Uses drawtext if available, otherwise falls back to SRT file method.
    
    Args:
        subtitles: List of subtitle entries
        style: Styling parameters
        video_width: Video width for text wrapping
        
    Returns:
        FFmpeg filter string for subtitle rendering
    """
    if not subtitles:
        return ""
    
    # Check if drawtext filter is available
    if check_drawtext_filter_available():
        return create_drawtext_filter(subtitles, style, video_width)
    else:
        # Fallback to SRT file method
        logger.info("drawtext filter not available, using SRT file method")
        return None  # Will be handled in add_subtitles_to_video


def create_drawtext_filter(subtitles: List[Dict[str, Any]], style: Dict[str, Any], video_width: int) -> str:
    """
    Create FFmpeg drawtext filter string with multi-line support.
    
    Args:
        subtitles: List of subtitle entries
        style: Styling parameters
        video_width: Video width for text wrapping
        
    Returns:
        FFmpeg filter string for subtitle rendering
    """
    # Calculate maximum text width (80% of video width minus padding)
    max_text_width = int(video_width * 0.9)
    
    # Build drawtext filters for each subtitle
    filters = []
    
    for i, subtitle in enumerate(subtitles):
        text = subtitle['text']
        
        # Detect if text contains Chinese characters
        has_chinese = detect_chinese_text(text)
        
        # Split text into lines
        lines = split_text_into_lines(text, max_text_width, style['font_size'])
        
        # Limit maximum lines to prevent overflow
        max_lines = 3
        if len(lines) > max_lines:
            lines = lines[:max_lines-1] + [lines[max_lines-1] + '...']
        
        # Calculate vertical positioning for multi-line text
        line_height = style['font_size'] + style['line_spacing']
        total_height = len(lines) * line_height
        start_y = style['y_position'] - (total_height // 2)
        
        # Create a filter for each line
        for line_idx, line in enumerate(lines):
            if not line.strip():
                continue
                
            # Properly escape text for FFmpeg
            escaped_line = line
            escaped_line = escaped_line.replace('\\', '\\\\')
            escaped_line = escaped_line.replace("'", "\\'")
            escaped_line = escaped_line.replace('"', '\\"')
            escaped_line = escaped_line.replace(':', '\\:')
            escaped_line = escaped_line.replace('[', '\\[')
            escaped_line = escaped_line.replace(']', '\\]')
            
            # Calculate Y position for this line
            line_y = start_y + (line_idx * line_height)
            
            # Create drawtext filter parts
            filter_parts = [
                f"drawtext=text='{escaped_line}'",
                f"fontsize={style['font_size']}",
                f"fontcolor={style['font_color']}",
                f"bordercolor={style['outline_color']}",
                f"borderw={style['outline_width']}",
                f"box=1",
                f"boxcolor={style['background_color']}",
                f"boxborderw={style['box_padding']}",
                f"x=(w-text_w)/2",  # Center horizontally
                f"y={line_y}",
                f"enable='between(t,{subtitle['start_time']},{subtitle['end_time']})'"
            ]
            
            # Add font file if specified
            if style['font_family'] and style['font_family'] != 'Arial' and os.path.exists(style['font_family']):
                filter_parts.insert(1, f"fontfile='{style['font_family']}'")
            
            filters.append(':'.join(filter_parts))
    
    # Combine all filters
    return ','.join(filters)


def add_subtitles_to_video(video_input: str, subtitles_input: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Add subtitles to a video using FFmpeg with automatic styling optimization.
    
    Args:
        video_input: URL or path to the video file
        subtitles_input: SRT format subtitle content or path to SRT file
        output_path: Optional output path for the video with subtitles
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_files = []
    
    try:
        if not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
            return {
                "status": "error",
                "data": None,
                "message": "FFmpeg executable not found"
            }
        
        # Handle video input (URL or local file)
        if video_input.startswith(('http://', 'https://')):
            download_result = download_video_from_url(video_input)
            if download_result["status"] == "error":
                return download_result
            video_path = download_result["data"]["file_path"]
            temp_files.append(video_path)
        elif os.path.exists(video_input):
            video_path = video_input
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Video file {video_input} not found"
            }
        
        # Get video information for styling optimization
        try:
            width, height, fps, frame_count = get_video_info(video_path)
            logger.info(f"Video info: {width}x{height}, {fps} fps, {frame_count} frames")
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Error reading video info: {str(e)}"
            }
        
        # Handle subtitle input (content or file path)
        if os.path.exists(subtitles_input):
            # Read from file
            with open(subtitles_input, 'r', encoding='utf-8') as f:
                srt_content = f.read()
        else:
            # Treat as content
            srt_content = subtitles_input
        
        # Parse SRT content
        subtitles = parse_srt_content(srt_content)
        if not subtitles:
            return {
                "status": "error",
                "data": None,
                "message": "No valid subtitles found in input"
            }
        
        logger.info(f"Parsed {len(subtitles)} subtitle entries")
        
        # Combine all subtitle text for font detection
        all_subtitle_text = "\n".join([sub['text'] for sub in subtitles])
        
        # Calculate optimal styling
        style = calculate_subtitle_style(width, height, all_subtitle_text)
        logger.info(f"Calculated subtitle style: font_size={style['font_size']}, font_family={style['font_family']}, y_position={style['y_position']}, has_chinese={style.get('has_chinese', False)}")
        
        # Check if drawtext filter is available
        use_drawtext = check_drawtext_filter_available()
        
        if not output_path:
            output_path = f"subtitled_{int(time.time())}.mp4"
        
        # Set up environment for FFmpeg font handling
        env = os.environ.copy()
        
        # Add font configuration for better Chinese support
        if style.get('has_chinese', False) and style['font_family'] != 'Arial':
            # Set fontconfig path if Chinese font is available
            font_dir = os.path.dirname(style['font_family'])
            if font_dir:
                env['FONTCONFIG_PATH'] = font_dir
                env['FC_CONFIG_DIR'] = font_dir
                logger.info(f"Set FONTCONFIG_PATH to {font_dir}")
        
        if use_drawtext:
            # Use drawtext filter method
            subtitle_filter = create_subtitle_filter(subtitles, style, width)
            if subtitle_filter:
                cmd = [
                    FFMPEG_PATH,
                    '-i', video_path,
                    '-vf', subtitle_filter,
                    '-c:a', 'copy',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-y', output_path
                ]
            else:
                # Fallback to SRT method if drawtext filter creation fails
                use_drawtext = False
        
        if not use_drawtext:
            # Use SRT file method with font specification
            import tempfile
            srt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
            srt_path = srt_file.name
            srt_file.close()
            temp_files.append(srt_path)
            
            # Get font path for Chinese support
            font_path = style['font_family'] if style['font_family'] != 'Arial' else None
            
            # Create SRT file with font specification
            create_srt_file(subtitles, srt_path, font_path)
            logger.info(f"Created temporary SRT file: {srt_path}")
            
            # Create fontconfig configuration for better font support
            if style.get('has_chinese', False) and font_path and os.path.exists(font_path):
                # Create temporary fontconfig configuration
                fontconfig_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False, encoding='utf-8')
                fontconfig_path = fontconfig_file.name
                temp_files.append(fontconfig_path)
                
                fontconfig_content = f'''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>{os.path.dirname(font_path)}</dir>
  <alias>
    <family>Arial</family>
    <prefer>
      <family>{os.path.splitext(os.path.basename(font_path))[0]}</family>
    </prefer>
  </alias>
  <alias>
    <family>sans-serif</family>
    <prefer>
      <family>{os.path.splitext(os.path.basename(font_path))[0]}</family>
    </prefer>
  </alias>
</fontconfig>'''
                
                fontconfig_file.write(fontconfig_content)
                fontconfig_file.close()
                
                env['FONTCONFIG_FILE'] = fontconfig_path
                logger.info(f"Created fontconfig file: {fontconfig_path}")
            
            # Use subtitles filter with proper font configuration
            subtitle_filter = f"subtitles='{srt_path}'"
            if font_path and os.path.exists(font_path):
                subtitle_filter += f":fontsdir='{os.path.dirname(font_path)}'"
            
            cmd = [
                FFMPEG_PATH,
                '-i', video_path,
                '-vf', subtitle_filter,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-y', output_path
            ]
        
        logger.info("Adding subtitles to video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # If FFmpeg returned non-zero, verify whether output was still produced
        if result.returncode != 0:
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.warning(f"FFmpeg exited with code {result.returncode} but output file exists; proceeding.")
            else:
                error_message = f"Failed to add subtitles. FFmpeg stderr: {result.stderr}"
                logger.error(f"Error adding subtitles: {error_message}")
                return {
                    "status": "error",
                    "data": None,
                    "message": error_message
                }
        
        # Log FFmpeg output for debugging (but don't treat as error)
        if result.stderr:
            logger.debug(f"FFmpeg stderr (informational): {result.stderr}")
        if result.stdout:
            logger.debug(f"FFmpeg stdout: {result.stdout}")
            
        # Verify output file was actually created
        if not os.path.exists(output_path):
            return {
                "status": "error",
                "data": None,
                "message": "FFmpeg completed but output file was not created"
            }
        
        logger.info(f"Subtitles added successfully: {output_path}")
        
        # Upload result to TOS
        try:
            tos_url = upload_to_tos(output_path)
            logger.info(f"Video uploaded to TOS: {tos_url}")
            
            # Clean up local output file
            try:
                os.unlink(output_path)
                logger.info(f"Cleaned up local output file: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up local file {output_path}: {e}")
            
            return {
                "status": "success",
                "data": {"tos_url": tos_url},
                "message": f"Subtitles added successfully ({len(subtitles)} entries)"
            }
        except Exception as e:
            logger.error(f"Error uploading to TOS: {e}")
            return {
                "status": "error",
                "data": None,
                "message": f"Error uploading to TOS: {str(e)}"
            }
        
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to add subtitles. FFmpeg stderr: {e.stderr}"
        logger.error(f"Error adding subtitles: {e}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        return {
            "status": "error",
            "data": None,
            "message": error_message
        }
    except Exception as e:
        logger.error(f"Error adding subtitles: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error adding subtitles: {str(e)}"
        }
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")


def create_srt_from_text_list(text_entries: List[Dict[str, Any]]) -> str:
    """
    Create SRT format content from a list of text entries with timing.
    
    Args:
        text_entries: List of dictionaries with 'start_time', 'end_time', and 'text' keys
        
    Returns:
        SRT format string
    """
    srt_content = []
    
    for i, entry in enumerate(text_entries, 1):
        start_time = seconds_to_time_str(entry['start_time'])
        end_time = seconds_to_time_str(entry['end_time'])
        text = entry['text']
        
        srt_entry = f"{i}\n{start_time} --> {end_time}\n{text}\n"
        srt_content.append(srt_entry)
    
    return "\n".join(srt_content)


def seconds_to_time_str(seconds: float) -> str:
    """
    Convert seconds to SRT time format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Time string in format "HH:MM:SS,mmm"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')


def get_font_cache_dir() -> str:
    """
    Args:
        None
    
    Returns:
        result: Directory path to store cached fonts
    """
    import platform
    system = platform.system().lower()
    home = str(Path.home())
    if system == "darwin":
        base = os.path.join(home, "Library", "Caches", "media-agent-mcp", "fonts")
    elif system == "windows":
        local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        base = os.path.join(local, "media-agent-mcp", "fonts")
    else:
        base = os.path.join(home, ".cache", "media-agent-mcp", "fonts")
    os.makedirs(base, exist_ok=True)
    return base


def download_chinese_font_to_cache() -> str:
    """
    Download a Chinese font to cache directory if not already present.
    Prefers smaller single-style fonts to reduce download size.
    
    Returns:
        result: Absolute path to downloaded font file, or empty string if failed
    """
    cache_dir = get_font_cache_dir()
    candidates: List[Tuple[str, str]] = [
        (
            "SourceHanSansSC-Regular.otf",
            "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf",
        ),
        (
            "NotoSansCJK-Regular.ttc",
            "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTC/NotoSansCJK-Regular.ttc",
        ),
    ]

    # If any candidate already exists and looks valid, return it
    for fname, _ in candidates:
        fpath = os.path.join(cache_dir, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 100_000:
            return fpath

    # Try download in order
    for fname, url in candidates:
        fpath = os.path.join(cache_dir, fname)
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                tmp = fpath + ".part"
                with open(tmp, "wb") as out:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            out.write(chunk)
                # Basic size sanity check (>100KB)
                if os.path.getsize(tmp) > 100_000:
                    os.replace(tmp, fpath)
                    return fpath
                else:
                    os.remove(tmp)
        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            continue
    return ""


if __name__ == '__main__':
    # Example usage
    sample_srt = """1
00:00:00,000 --> 00:00:01,000
这是第一条中文字幕

2
00:00:01,000 --> 00:00:03,000
This is the second English subtitle

3
00:00:04,000 --> 00:00:05,000
这是第三条字幕
支持多行文本"""
    
    video_url = "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4"
    result = add_subtitles_to_video(video_url, sample_srt)
    print(f"Result: {result}")