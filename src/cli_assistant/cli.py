import asyncio
from .config import Config
from .llm import LLMClient
from .ui.formatter import UIFormatter
from .tools.registry import registry
from .tools.calculator import CalculatorTool
from .tools.weather import WeatherTool
from .tools.file_ops import FileOpsTool

class CLIAssistant:
    def __init__(self):
        self.config = Config.from_env()
        self.llm_client = LLMClient(self.config)
        self.ui = UIFormatter()
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        registry.register(CalculatorTool())
        registry.register(WeatherTool())
        registry.register(FileOpsTool())
    
    async def run(self):
        """Main CLI loop"""
        self.ui.format_welcome()
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['/quit', '/exit']:
                    print("Goodbye! 👋")
                    break

                # Format user message
                self.ui.format_user_message(user_input)
                
                if user_input.lower() == '/help':
                    self._show_help()
                    continue

                if user_input.lower() == '/tools':
                    self._show_tools()
                    continue
                               
                # Get and format assistant response
                response = await self.llm_client.chat(user_input)
                self.ui.format_assistant_message(response)
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                self.ui.format_error(str(e))
    
    def _show_help(self):
        """
        Show available tools and commands.
        """
        tools = registry.list_tools()
        help_text = f"""Available tools: {', '.join(tools)}
        Commands:
        - /help - Show this help
        - /quit - Exit the application
        """
        self.ui.format_assistant_message(help_text)

    def _show_tools(self):
        tools = registry.list_tools()
        lines = [f"**{name}**: {registry.get_tool(name).description}" for name in tools]
        self.ui.format_assistant_message("\n\n".join(lines))

def main():
    """Entry point for the CLI application"""
    assistant = CLIAssistant()
    asyncio.run(assistant.run())

if __name__ == "__main__":
    main()