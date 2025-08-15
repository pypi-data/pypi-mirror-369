#########
# STUDR #
#########

__version__ = "0.2.0"
__author__ = "fr33 // Emirhan"
__email__ = "Emirhan.07274@gmail.com" #i love titanfall 2

from .__Main__ import asciiTextGenerator, draw, stopwatch

def main():
    from .__Main__ import main as main_func
    
    try:
        main_func()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error running studr: {e}")
        return 1
    
    return 0

__all__ = ["main", "asciiTextGenerator", "draw", "stopwatch"]