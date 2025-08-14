"""Video subtitle processing module.

This module provides video subtitle functionality including adding subtitles to videos.
Uses FFmpeg for subtitle rendering with automatic positioning and styling optimization.
"""
import logging
import os
import time
import subprocess
import re
import platform
from typing import Optional, Dict, Any, List, Tuple
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
        text: Text to analyze
        
    Returns:
        True if text contains Chinese characters
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))


def get_system_font_path() -> str:
    """
    Get system font path that supports Chinese characters.
    
    Returns:
        Path to a font file that supports Chinese characters
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Try common Chinese fonts on macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Arial Unicode MS.ttf"
        ]
    elif system == "Linux":
        # Try common Chinese fonts on Linux
        font_paths = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        ]
    elif system == "Windows":
        # Try common Chinese fonts on Windows
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/arial.ttf"
        ]
    else:
        font_paths = []
    
    # Find first available font
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    # Fallback to system default
    return ""


def calculate_subtitle_style(video_width: int, video_height: int, has_chinese: bool = False) -> Dict[str, Any]:
    """
    Calculate optimal subtitle styling based on video resolution and text content.
    
    Args:
        video_width: Video width in pixels
        video_height: Video height in pixels
        has_chinese: Whether the text contains Chinese characters
        
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
    
    # Choose appropriate font based on content
    if has_chinese:
        font_path = get_system_font_path()
        font_family = font_path if font_path else "Arial"
    else:
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
        'line_spacing': int(base_font_size * 0.2)
    }


def estimate_text_width(text: str, font_size: int, has_chinese: bool = False) -> int:
    """
    Estimate text width in pixels based on font size and content.
    
    Args:
        text: Text content
        font_size: Font size in pixels
        has_chinese: Whether text contains Chinese characters
        
    Returns:
        Estimated width in pixels
    """
    # Rough estimation: Chinese characters are wider than ASCII
    if has_chinese:
        # Chinese characters are roughly square (width ≈ height)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        ascii_chars = len(text) - chinese_chars
        return int(chinese_chars * font_size + ascii_chars * font_size * 0.6)
    else:
        # ASCII characters are roughly 0.6 times the font size in width
        return int(len(text) * font_size * 0.6)


def split_text_into_lines(text: str, max_width: int, font_size: int, has_chinese: bool = False) -> List[str]:
    """
    Split text into multiple lines based on maximum width.
    
    Args:
        text: Text content to split
        max_width: Maximum width in pixels
        font_size: Font size in pixels
        has_chinese: Whether text contains Chinese characters
        
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
        if estimate_text_width(paragraph, font_size, has_chinese) <= max_width:
            lines.append(paragraph)
            continue
        
        # Split paragraph into words for wrapping
        if has_chinese:
            # For Chinese text, we can break at any character
            current_line = ''
            for char in paragraph:
                test_line = current_line + char
                if estimate_text_width(test_line, font_size, has_chinese) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
        else:
            # For English text, break at word boundaries
            words = paragraph.split(' ')
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                if estimate_text_width(test_line, font_size, has_chinese) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
    
    return lines


def create_subtitle_filter(subtitles: List[Dict[str, Any]], style: Dict[str, Any], video_width: int) -> str:
    """
    Create FFmpeg subtitle filter string with multi-line support.
    
    Args:
        subtitles: List of subtitle entries
        style: Styling parameters
        video_width: Video width for text wrapping
        
    Returns:
        FFmpeg filter string for subtitle rendering
    """
    if not subtitles:
        return ""
    
    # Calculate maximum text width (80% of video width minus padding)
    max_text_width = int(video_width * 0.9)
    
    # Build drawtext filters for each subtitle
    filters = []
    
    for i, subtitle in enumerate(subtitles):
        text = subtitle['text']
        
        # Detect if text contains Chinese characters
        has_chinese = detect_chinese_text(text)
        
        # Split text into lines
        lines = split_text_into_lines(text, max_text_width, style['font_size'], has_chinese)
        
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
        
        # Detect if subtitles contain Chinese characters
        all_text = ' '.join([sub['text'] for sub in subtitles])
        has_chinese = detect_chinese_text(all_text)
        logger.info(f"Chinese text detected: {has_chinese}")
        
        # Calculate optimal styling
        style = calculate_subtitle_style(width, height, has_chinese)
        logger.info(f"Calculated subtitle style: font_size={style['font_size']}, font_family={style['font_family']}, y_position={style['y_position']}")
        
        # Create subtitle filter with multi-line support
        subtitle_filter = create_subtitle_filter(subtitles, style, width)
        
        if not output_path:
            output_path = f"subtitled_{int(time.time())}.mp4"
        
        # Build FFmpeg command
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-vf', subtitle_filter,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-c:v', 'libx264',  # Re-encode video to embed subtitles
            '-preset', 'medium',  # Balance between speed and quality
            '-crf', '23',  # Good quality setting
            '-y', output_path
        ]
        
        logger.info("Adding subtitles to video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
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