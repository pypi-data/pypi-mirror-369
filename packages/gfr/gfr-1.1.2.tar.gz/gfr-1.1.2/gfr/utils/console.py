# gfr/utils/console.py

import sys

def get_multiline_input() -> str:
    """
    Captures multi-line text input from the user.
    
    Input is terminated when the user presses Ctrl+C or Ctrl+D on a blank line
    and then hits Enter.

    Returns:
        str: The multi-line text entered by the user.
    """
    lines = []

    while True:
        try:
            line = sys.stdin.readline()
            if line.strip() == "'''":
                # Stop on '''
                break
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C as termination
            break
            
    # Join the lines, stripping trailing newlines from each line before joining
    return "".join(lines)

