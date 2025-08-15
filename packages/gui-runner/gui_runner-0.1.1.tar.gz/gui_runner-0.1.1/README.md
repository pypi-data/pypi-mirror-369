# GUI Runner

## Project Overview
A configurable GUI runner based on Tkinter for executing Python and Node.js scripts. Supports parameter configuration, multi-language interfaces, and configuration file management. Ideal for script execution scenarios requiring graphical operations.

## Key Features
- **Visual Parameter Configuration**: Supports multiple parameter types including file paths, directory selection, checkboxes, and dropdown lists
- **JSON-based Configuration**: Uses JSON files instead of command-line arguments for better handling of scripts with numerous parameters
- **Multi-language Support**: Customizable interface text through simple configuration (English by default)
- **Configuration Management**: Load/save configuration files in JSON format
- **Script Execution**: 
  - Automatically detects execution method based on script extension (Python/Node.js)
  - Real-time log display in sub-windows during execution
- **Cross-platform Support**: Implemented using Python's standard library, compatible with Windows, macOS, and Linux systems, but requires Tkinter library to be pre-installed.

## Installation
```bash
pip install gui-runner
```
## Launch Methods
1. Command-line launch after installation:
    ```bash
    gui-runner --config=config.json --dict=dict.txt
    ```
2. Programmatic integration:
    ```python
    import tkinter as tk
    from gui_runner import ConfigurableGUI

    def run_gui():
        root = tk.Tk()
        app = ConfigurableGUI(root, "dict.txt", "config.json")
        root.mainloop()

    if __name__ == "__main__":
        run_gui()
    ```
## Configuration Files
* Main configuration:```config.json```(specify with ```--config``` parameter)
* Language dictionary: ```dict.txt``` (specify with ```--dict``` parameter)
## Extending Functionality
1. Adding new features:
    * Add new categories in the ```categories``` array within ```config.json```
    * Each category can contain multiple function items (see examples)
2. Configuring parameter interfaces:
    * Create JSON-formatted UI configuration files
    * Supported parameter types: ```boolean```, ```choice```, ```array```, ```file```, ```directory```, ```save```, ```string```, ```number```, ```integer```
    * Supports parameter dependencies
## Configuration File Formats
### Main Configuration (```config.json```)
```json
{
  "main_title": "GUI Title",
  "categories": [
    {
      "name": "Category Name",
      "description": "Category Description",
      "functions": [
        {
          "name": "Function Name",
          "description": "Function Description",
          "script": "script_path",
          "config_file": "parameter_config_path",
          "ui_config_file": "ui_config_path"
        }
      ]
    }
  ]
}
```
## UI Configuration (function_config.json)
```json
{
  "notes": "Important notes",
  "groups": [
    {
      "name": "Parameter Group Name",
      "parameters": [
        {
          "name": "parameter_name",
          "label": "Display Label",
          "type": "Parameter Type",
          "tip": "Tooltip Information",
          "default": "Default Value",
          "choices": ["Option1", "Option2"],  // For choice type
          "extensions": [".txt", ".csv"],    // For file type
          "item_type": "file",               // For array type
          "depends_on": "dependency_param"   // Boolean dependencies only
        }
      ]
    }
  ]
}
```
## Language File Format
1. Create a text file (e.g., ```dict.txt```)
2. Format:
    ```
    # Comments (optional)
    key_name: Translated Text
    ```
3. Example (```dict.txt```):
    ```
    # Main window texts
    back_button: Back
    run_script_button: Run Script

    # Error messages
    error_title: Error
    config_format_error: Configuration format error
    ```
    > Full key list reference: See _init_default_values method in src/ui_dict.py

## Directory Structure
```
gui-runner/
├── src/                      # Source code
│   ├── config_manager.py     # Configuration management
│   ├── gui_main.py           # Main window
│   ├── gui_subwindow.py      # Function sub-windows
│   ├── main.py               # Entry point
│   ├── tooltip.py            # Tooltip component
│   ├── ui_dict.py            # Multi-language management
│   └── utils.py              # Utility functions
├── config.json               # Sample configuration
├── setup.py                  # Installation script
└── README.md                 # Documentation
```
## License
[MIT License](LICENSE)