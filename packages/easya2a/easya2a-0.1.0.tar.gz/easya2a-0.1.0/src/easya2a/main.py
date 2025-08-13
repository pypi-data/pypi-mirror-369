"""
Main module for easya2a package
"""

def hello_world(name: str = "World") -> str:
    """
    Return a hello world greeting.
    
    Args:
        name (str): The name to greet. Defaults to "World".
        
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}! Welcome to easya2a!"


def main():
    """
    Main entry point for the command line interface.
    """
    print(hello_world())
    print("This is easya2a package - ready for your awesome features!")


if __name__ == "__main__":
    main()
