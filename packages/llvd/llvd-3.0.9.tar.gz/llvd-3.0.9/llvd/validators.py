"""
Input validation utilities for LLVD.
"""
from typing import Optional, Tuple, List
from llvd.utils import clean_dir

def validate_course_and_path(course: Optional[str], path: Optional[str]) -> Tuple[Tuple[str, str], bool]:
    """
    Validate and process course and path arguments.
    
    Args:
        course: The course slug (optional)
        path: The learning path slug (optional)
        
    Returns:
        Tuple containing (course_slug, is_path) where:
        - course_slug is a tuple of (cleaned_name, type)
        - is_path is a boolean indicating if it's a learning path
        
    Raises:
        ValueError: If validation fails
    """
    if course and path:
        raise ValueError("Please specify either a course OR learning path, not both.")
    
    if path:
        return (clean_dir(path), "path"), True
    if course:
        return (clean_dir(course), "course"), False
        
    raise ValueError("Either --course or --path must be specified")

def parse_throttle(throttle_str: Optional[str]) -> Optional[List[int]]:
    """
    Parse throttle string into min,max values.
    
    Args:
        throttle_str: String in format "min,max" or "value"
        
    Returns:
        List of [min, max] or [value], or None if input is None/empty
        
    Raises:
        ValueError: If input format is invalid
    """
    if not throttle_str:
        return None
        
    try:
        if "," in throttle_str:
            values = [int(x.strip()) for x in throttle_str.split(",", 1)]
            if len(values) != 2:
                raise ValueError("Throttle must be in format 'min,max' or 'value'")
            return values
        return [int(throttle_str)]
    except ValueError as e:
        raise ValueError("Throttle must be a number or two numbers separated by comma") from e