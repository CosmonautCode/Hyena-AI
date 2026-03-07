
from app.core.chat import ChatSystem


def main():
    """Main entry point."""
    app = ChatSystem()
    
    # Load agents and start the original interface
    app.load_agents()
    app.chat_display()


if __name__ == "__main__":
    main()
