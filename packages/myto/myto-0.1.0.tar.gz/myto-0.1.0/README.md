# myto

A flexible Python-based task automation framework for personal use cases.

## 🚀 Quick Start

### Installation
```bash
pip install myto
```

or

```bash
# Clone the repository
git clone <your-repo-url>
cd myto

# Install dependencies
rye sync
```

### Basic Usage
```python
from myto.base.runner import MyToRunner
from myto.tasks.openAppTask import OpenAppTask
from myto.when.timer import WhenTimer

# Create a runner with tasks
runner = MyToRunner(
    tasks=[
        OpenAppTask(appName="notepad.exe"),
        OpenAppTask(
            appName="cmd", 
            when=WhenTimer(seconds=10)  # Run after 10 seconds
        )
    ],
    debug=True
)

# Execute tasks
runner.run()
```

### CLI Usage
```bash
# Run from a Python file
myto run main.py

# Run with custom variable name
myto run main.py --runnervar my_runner

# Merge multiple runners
myto run main.py --path scripts/extra.py --path scripts/more.py
```

## 📋 Core Components

### Tasks
Tasks define what actions to perform. All tasks inherit from `MytoTask`.

#### OpenAppTask
Opens applications or executes commands.

```python
OpenAppTask(
    appName="notepad.exe",           # Application to open
    isPath=True,                     # Whether it's a path or command
    shouldDetach=True,               # Run in background
    name="Open Notepad",             # Optional custom name
    when=WhenTimer(minutes=5)        # Optional timing condition
)
```

### Timing Conditions (When)
Control when tasks execute using `when` conditions.

#### WhenTimer
Execute after a specific duration:
```python
WhenTimer(
    seconds=30,      # Wait 30 seconds
    minutes=5,       # Wait 5 minutes  
    hours=1          # Wait 1 hour
)
```

#### WhenTime
Execute at a specific time of day:
```python
WhenTime(
    hours=14,        # 2 PM
    minutes=30,      # 30 minutes past
    seconds=0,       # 0 seconds
    pm=True          # PM time
)
```

### Before Runners
Wait for specific conditions before executing tasks.

#### WaitForProcess
Wait for a process to start or stop:
```python
from myto import Myto

task = OpenAppTask(
    appName="my_app.exe",
    beforeRunners=[
        Myto.beforeRunners.waitForProcess(
            processMatch="chrome.exe",  # Wait for Chrome
            isClosed=False              # Wait for it to start
        )
    ]
)
```

#### WaitForWindow
Wait for a window to appear or disappear:
```python
task = OpenAppTask(
    appName="my_app.exe", 
    beforeRunners=[
        Myto.beforeRunners.waitForWindow(
            windowMatch="Visual Studio Code",  # Window title contains this
            isClosed=False                     # Wait for window to appear
        )
    ]
)
```

## 🔧 Advanced Features

### Context Management
Tasks have access to a context system for sharing data between execution phases.

### Custom Tasks
Create your own tasks by inheriting from `MytoTask`:

```python
from myto.base.task import MytoTask

class CustomTask(MytoTask):
    def exec(self, ctx):
        # Your custom logic here
        print(f"Executing: {self.name}")
```

## 🔍 Examples

### Simple App Launcher
```python
runner = MyToRunner(
    tasks=[
        OpenAppTask(appName="notepad.exe"),
        OpenAppTask(appName="calc.exe"),
    ]
)
runner.run()
```

### Timed Execution
```python
runner = MyToRunner(
    tasks=[
        OpenAppTask(
            appName="backup_script.bat",
            when=WhenTime(hours=2, am=True)  # Run at 2 AM
        ),
        OpenAppTask(
            appName="chrome.exe",
            when=WhenTimer(minutes=30)       # Run after 30 minutes
        )
    ]
)
runner.run()
```

### Conditional Execution
```python
runner = MyToRunner(
    tasks=[
        OpenAppTask(
            appName="my_app.exe",
            beforeRunners=[
                WaitForProcess(processMatch="required_service.exe"),
                WaitForWindow(windowPattern=r"Ready.*", isClosed=False)
            ]
        )
    ]
)
runner.run()
```

## 🛠️ Development

- Python 3.8+
- Dependencies managed with [Rye](https://rye-up.com/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
