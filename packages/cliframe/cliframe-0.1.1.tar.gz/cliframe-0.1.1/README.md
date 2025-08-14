# CliFrame - Python CLI Development Framework

A simple and powerful framework for building interactive command-line applications with dynamic command discovery and hierarchical command organization.

## 🚀 Features

- **Hierarchical Command Structure** - Organize commands in folders and files
- **Dynamic Command Discovery** - Automatically discovers commands based on file structure
- **Interactive Shell** - Rich interactive CLI with tab completion
- **Built-in Help System** - Use `?` to get help on any command or subcommand
- **Configuration Mode** - Special configuration mode with `_configure` folder support
- **Rich Text Support** - Color formatting and styled output
- **Customizable Prompts** - Set custom prompt text and mode indicators
- **Method Chaining** - Fluent API for easy CLI setup

## 📦 Installation

```bash
pip install cliframe
```

## 🏗️ Quick Start

### 1. Basic Setup

```python
from cliframe import CliService

# Create and run CLI service
cli = CliService()
cli.motd("Welcome to My CLI App!", rich=True)
cli.prompt("myapp")
cli.run()
```

### 2. Command Structure

Organize your commands in a `cli/` directory structure:

```text
cli/
├── show/
│   ├── __init__.py          # 'show' command handler
│   ├── users.py             # 'show users' command
│   └── logs/
│       └── __init__.py      # 'show logs' command
├── start.py                 # 'start' command
├── stop.py                  # 'stop' command  
└── _configure/              # Configuration commands
    ├── network.py
    └── system.py
```

### 3. Command Handlers

Create command handlers as Python classes:

```python
# cli/start.py
class StartCommand:
    """Start the application service."""
    
    def __init__(self, core):
        self.core = core
    
    def run(self, args=None):
        """Start the service with optional arguments."""
        print("Service started successfully!")
        return "Service is now running"

# Alternative: Use Command or StartCommand class names
class Command:  # Will be auto-discovered
    def run(self, args=None):
        print("Command executed!")
```

### 4. Advanced Configuration

```python
from cliframe import CliService

cli = (CliService()
       .folder("/path/to/custom/cli/commands")  # Custom command folder
       .prompt("myapp")                         # Custom prompt
       .prompt_mode_sign("#")                   # Custom prompt sign
       .motd("🎉 Welcome to MyApp CLI!", rich=True))

cli.run()
```

## 🎯 Command Organization

### File-based Commands

- `command.py` → `command` CLI command
- Each file should contain a command handler class

### Directory-based Commands  

- `command/` → `command` CLI command group
- `command/__init__.py` → Handler for base `command`
- `command/subcommand.py` → Handler for `command subcommand`

### Handler Class Discovery

CliFrame looks for handler classes in this order:

1. `StartCommand` class
2. `Command` class  
3. Any class ending with `Command`
4. First class found in the module

## 🛠️ Interactive Features

### Help System

- Type `?` at the end of any command to get help
- `command ?` - Shows help for the command
- `command sub ?` - Shows help for subcommands

### Tab Completion

- Smart tab completion for all available commands
- Context-aware completion based on current command path

### Configuration Mode

- Create `_configure/` folder for configuration commands
- Type `configure` to enter configuration mode
- Prompt changes to `(config)#`
- Type `exit` to leave configuration mode

## 📝 Example Usage

```bash
# Interactive CLI session
myapp> start ?                    # Get help for start command
myapp> show users                 # Execute show users command  
myapp> configure                  # Enter configuration mode
myapp(config)# network setup      # Run configuration command
myapp(config)# exit               # Exit configuration mode
myapp> exit                       # Exit CLI
```

## 🎨 Styling and Output

### Color Markers

Use color markers in your command output:

```python
def run(self, args=None):
    return "[green]Success![/green] Operation completed [yellow]successfully[/yellow]"
```

### Available Styles

- `[red]text[/red]` - Red text
- `[green]text[/green]` - Green text  
- `[yellow]text[/yellow]` - Yellow text
- `[blue]text[/blue]` - Blue text
- `[magenta]text[/magenta]` - Magenta text
- `[cyan]text[/cyan]` - Cyan text

## 🔧 API Reference

### CliService Class

#### Methods

- `__init__(core=None, cli_root=None)` - Initialize CLI service
- `folder(path)` - Set custom CLI commands directory
- `prompt(text)` - Set prompt text (default: "cli")
- `prompt_mode_sign(sign)` - Set prompt mode sign (default: ">")  
- `motd(message, rich=True)` - Set message of the day
- `run()` - Start the interactive CLI

#### Method Chaining

All configuration methods return `self` for easy chaining:

```python
cli = (CliService()
       .folder("./my-commands")
       .prompt("myapp")
       .motd("Welcome!"))
```

## 📁 Project Structure

```text
your-project/
├── cli/                    # Default CLI commands directory
│   ├── show/
│   ├── start.py
│   ├── stop.py
│   └── _configure/        # Configuration commands
├── main.py                # Your CLI application entry point
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
