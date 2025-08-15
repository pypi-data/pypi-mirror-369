import os
import sys
import ast
from string import Template
import yaml
import subprocess
import threading
import logging
import platform
import time
import copy
logger = logging.getLogger(__name__)

"""
To do:
- Add support for running scripts in the background.
- Implement a method to run scripts in parallel.
- Timeout handling for script execution.
- Group handling dynamically (inside the script configuration).
"""

class FrameworkAPI:
    """
    FrameworkAPI: A class for managing and executing scripts based on YAML configurations.
    """

    def __init__(self, config_path=None, config=None, log_file=None):
        """
        Initialize the FrameworkAPI with a YAML configuration file or a preloaded configuration.
        Sets up logging if a log file is provided.

        Args:
            config_path (str, optional): Path to the YAML configuration file. Defaults to None.
            config (dict, optional): Preloaded configuration dictionary. Defaults to None.
            log_file (str, optional): Path to the log file for logging errors and debug messages. Defaults to None.

        Raises:
            ValueError: If neither 'config' nor 'config_path' is provided.
        """
        self.config_path = config_path
        self.raw_config = {}
        
        # Determine configuration source
        if config or config_path:
            if isinstance(config_path, str):
                config_path = [config_path]
            if config_path:
                for path in config_path:
                    self.raw_config = FrameworkAPI.merge(
                        self.raw_config, FrameworkAPI._load_config(path, raw=True))

            if isinstance(config, dict):
                config = [config]
            if config:
                for cfg in config:
                    self.raw_config = FrameworkAPI.merge(self.raw_config, cfg)
                    self.raw_config.update(cfg)
        else:
            logger.error("Initialization failed: Both 'config' and 'config_path' are missing. "
                         "Provide at least one configuration source.")
            raise ValueError(
                "Configuration source is required: Pass either 'config' or 'config_path'.")
        
        # Resolve references in the configuration
        self.config = self._resolve_references(self.raw_config)

        # Resolve grouping in the configuration
        self.config = self._resolve_grouping(self.config)

        # Set up logging if a log file is provided
        if log_file:
            self._setup_logging(log_file)
    
    def _setup_logging(self, log_file):
        """
        Set up the logging configuration.

        Args:
            log_file (str): Path to the log file.
        """
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
        )
        logger.debug("Logging initialized.")

    @staticmethod
    def _load_config(path, raw=False, error=None):
        """
        Load and parse the YAML configuration file.

        Args:
            raw (bool): If True, return raw YAML configuration without resolving references.

        Returns:
            dict: Parsed configuration as a dictionary.
        """
        if isinstance(path, FrameworkAPI):
            path = path.config_path
        try:
            with open(path, 'r') as f:
                raw_config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {path}.")
            if raw:
                return raw_config
            else:
                return FrameworkAPI._resolve_references(raw_config)
        except FileNotFoundError as e:
            logger.debug(f"Configuration file not found: {path}")
            if error == 'ignore':
                pass
            elif error == 'raise':
                raise
            else:
                print(e)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            if error == 'ignore':
                pass
            elif error == 'raise':
                raise
            else:
                print(e)
        return {}
    
    def _save_config(self, path, overwrite: bool = False):
        if not os.path.exists(path) or overwrite:
            with open(path, 'w+') as f:
                yaml.safe_dump(self.config, f)
            logger.info(f"Configuration saved to {path}.")

    def _save_class(self, path, overwrite: bool = False):
        if not os.path.exists(path) or overwrite:
            with open(path, 'w+') as f:
                yaml.safe_dump(vars(self), f)
            logger.info(f"FrameworkAPI class saved to {path}.")

    @staticmethod
    def _resolve_grouping(config):
        """
        Resolve grouping in the YAML configuration.

        Args:
            config (dict): The raw YAML configuration.

        Returns:
            dict: Configuration with resolved groups.
        """
        if 'groups' in config:
            logger.info(
                f"Groups already exist in configuration ({config['groups']}).")
            return config
        
        logger.info("Resolving groups in configuration.")
        config['groups'] = []
        try:
            for script in config.get('scripts', {}):
                if 'group' in script:
                    config['groups'] += [script['group']]
            config['groups'] = list(set(config['groups']))  # Remove duplicates
            return config
        except Exception as e:
            logger.error(f"Error resolving groups in configuration: {e}")
            raise

    @staticmethod
    def _resolve_references(config):
        """
        Resolve cross-references in the YAML configuration using string templates.

        Args:
            config (dict): The raw YAML configuration.

        Returns:
            dict: Configuration with resolved references.
        """
        config = FrameworkAPI._resolve_shortkeys(config)

        try:
            def resolve(obj, context=None):
                if context is None:
                    context = obj
                if isinstance(obj, dict):
                    return {k: resolve(v, context) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [resolve(item, context) for item in obj]
                elif isinstance(obj, str):
                    return Template(obj).safe_substitute(context)
                else:
                    return obj

            return resolve(config)
        except Exception as e:
            logger.error(f"Error resolving references in configuration: {e}")
            raise
    
    @staticmethod
    def _resolve_shortkeys(config, shortkeys=None):
        """
        Resolve coded references in the YAML configuration using eval of string.

        Args:
            config (dict): The raw YAML configuration.

        Returns:
            dict: Configuration with resolved coded references.
        """
        try:
            def resolve(obj, key=None):
                if isinstance(obj, str) and obj.strip().startswith('eval:'):
                    expr = obj.strip()[5:].strip()

                    try:
                        # Prepare a restricted environment for evaluation
                        allowed_globals = {
                            "__builtins__": {
                                "True": True,
                                "False": False,
                                "None": None,
                                "len": len,
                                "range": range,
                                "str": str,
                                "int": int,
                                "float": float,
                                "print": print,
                                "__import__": __import__,
                            }}
                        allowed_locals = {}

                        # Dynamically import required libraries
                        if 'import ' in expr:
                            for codeline in expr.split(';'):
                                exec(codeline.strip(),
                                     allowed_globals, allowed_locals)
                                value = allowed_locals.get(key, str(obj))
                        else:
                            # Safely evaluate the expression
                            value = ast.literal_eval(expr)

                        # Store the resolved value in the configuration
                        return value
                    except (ValueError, SyntaxError) as e:
                        print(f"Error evaluating expression: {e}")

                else:
                    return obj

            return {k: resolve(v, k) for k, v in config.items()}

        except Exception as e:
            logger.error(f"Error resolving references in configuration: {e}")
            raise

    @staticmethod
    def merge(one, other, overwrite=True):
        """
        Merge configurations from another FrameworkAPI instance.

        Args:
            other (FrameworkAPI): Another FrameworkAPI instance whose config will be merged.
            overwrite (bool): If True, overwrite existing keys with the values from `other`.

        Returns:
            None
        """
        try:
            def recursive_merge(dict1, dict2):
                for key, value in dict2.items():
                    if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                        recursive_merge(dict1[key], value)
                    elif overwrite or key not in dict1:
                        dict1[key] = value
                return dict1

            if isinstance(other, FrameworkAPI):
                out = copy.deepcopy(one)
                out.__dict__.update(recursive_merge(vars(out), vars(other)))
                logger.info("Configurations merged successfully.")
                return out
            elif isinstance(one, dict) and isinstance(other, dict):
                out = recursive_merge(one, other)
                logger.info("Dictionaries merged successfully.")
                return out
            else:
                raise TypeError("Argument must be an instance of FrameworkAPI")
        except Exception as e:
            logger.error(f"Error merging configurations: {e}")
            raise

    @staticmethod
    def _run_script(configuration=None, script_path=None, function_name=None, args=None,
                    arg_format=None, **kwargs):
        """
        Execute a script based on configuration or direct parameters.

        Args:
            configuration (dict, optional): Configuration of the script to be run. Defaults to None.
            script_path (str, optional): Direct path to the script file. Required if configuration is not provided.
            function_name (str, optional): Function to execute in the script. Defaults to None.
            args (dict, list, tuple, optional): Arguments to pass to the script or function. Defaults to None.
            arg_format (str, optional): Set the format that the arguments will be passed for direct terminal calls.

        Raises:
            ValueError: If required inputs are missing.
        """
        try:
            # Validate inputs
            if not script_path and configuration:
                script_path = script_path or configuration.get("path")
                function_name = function_name or configuration.get("function")
                args = args or configuration.get("args", {})

            if not script_path:
                raise ValueError(
                    "Script path is required if no configuration is provided.")

            args = args or {}

            # Convert args to dict if it's a list or tuple
            if isinstance(args, (list, tuple)):
                args = {f"arg{i+1}": val for i, val in enumerate(args)}
                # Force arg_format to 'v' if args are passed as a list or tuple
                arg_format = 'v'
            elif not isinstance(args, dict):
                raise TypeError("args must be a dict, list, or tuple.")

            # Determine the script command
            command = FrameworkAPI._build_command(
                script_path, function_name, args, arg_format)

            logger.info(f"Executing command: {command}")

            # Execute the command
            return FrameworkAPI._run_command(command=command, **kwargs)
        except Exception as e:
            logger.error(
                f"Error executing script '{script_path}': {e}")
            raise

    def run(self, *args, **kwargs):
        return self.run_script(*args, **kwargs)
    
    def run_script(self, script_name, error='ignore', **kwargs):
        """
        Execute a script defined in the configuration using optional additional parameters.

        Args:
            script_name (str): The name of the script to execute, as defined in the configuration.

        Raises:
            ValueError: If the configuration is missing or improperly defined.
            KeyError: If the specified script is not found in the configuration.
            Exception: Any other exceptions that occur during script execution.

        Returns:
            Any: The result of the script execution.
        """
        if not self.config:
            raise ValueError(
                "Configuration is missing. Please provide a valid configuration.")

        scripts = self.config.get("scripts", {})
        if script_name not in scripts:
            test_group = self._get_scripts_from_group(script_name)
            if test_group:
                return self.run_workflow(workflow=test_group, **kwargs)
            else:
                raise KeyError(
                    f"Script '{script_name}' is not defined in the configuration.")

        try:
            script_info = scripts[script_name]
            runner = FrameworkAPI._run_script(script_info, **kwargs)
            return runner
        except Exception as e:
            logger.error(
                f"Error executing script '{script_name}': {e}")
            if error == 'ignore':
                pass
            else:
                raise e
    
    def _get_scripts_from_group(self, target):
        """
        Retrieves a list of scripts belonging to a specific group.

        Args:
            target (str): The prefix (group) to filter scripts by, e.g. "#GROUP".

        Returns:
            A list of scripts that belong to the given group.        
        """
        groups = self.config.get("groups", {})
        group = groups.get(target, [])
        return group

    def run_workflow(self, workflow=None, background=False, delay=0):
        """
        Execute all scripts defined in the workflow in sequence.
        """
        try:
            if not workflow: workflow = self.config.get('workflow', [])
            for script_name in workflow:
                self.run_script(script_name, background=background)
                time.sleep(delay)
            logger.info("Workflow executed successfully.")
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise

    @staticmethod
    def _get_interpreter(script_path):
        """
        Determine the interpreter for a given script based on its file extension.

        Args:
            script_path (str): Path to the script.

        Returns:
            str: The interpreter command (e.g., 'python', 'Rscript', 'julia').

        Raises:
            ValueError: If the file extension is unsupported.
        """
        ext = os.path.splitext(script_path)[-1].lower() if '.' in script_path else ''
        system = platform.system()

        if ext == '.py':
            if system == 'Linux':
                return 'python3'
            elif system == 'Windows':
                return 'python'
            elif system == 'Darwin':  # macOS
                return 'python3'
            else:
                return 'python'
        elif ext == '.r':
            return 'Rscript'
        elif ext == '.jl':
            return 'julia'
        elif ext == '.exe':
            return 'executable'
        elif ext == '.lnk':
            return 'executable'
        elif ext == '.bat':
            return 'executable'
        elif ext == '.sh':
            return 'bash'
        elif ext == '':
            return 'executable'
        else:
            raise ValueError(
                f"Unsupported script type for file '{script_path}'.")

    @staticmethod
    def _build_command(script_path: str, function_name: str = None, args: dict = {}, arg_format: str = None) -> list:
        """
        Build the command to execute the script.

        Args:
            script_path (str): Path to the script file.
            function_name (str, optional): Function to execute within the script.
            args (dict, optional): Arguments to pass to the function.
            arg_format (str, optional): Set the format that the arguments will be passed for direct terminal calls.

        Returns:
            list: The command to execute the script.

        Raises:
            ValueError: If the script extension is not supported.
        """
        script_path = os.path.abspath(script_path).replace('\\', '/')
        args = args or {}
        interpreter = FrameworkAPI._get_interpreter(script_path)
        ext = os.path.splitext(script_path)[-1].lower()
        system = platform.system()

        if function_name:
            if interpreter in ['executable', 'bash']:
                raise ValueError(
                    f"Cannot handle function name with an executable: {script_path}"
                )
            
            # Build command for a specific function
            module_path = os.path.relpath(
                os.path.abspath(script_path), os.getcwd()).rsplit('.', 1)[0].replace(
                '\\', '.').replace('/', '.')
            formatted_args = ', '.join([f'{k}="{v}"' if isinstance(
                v, str) else f"{k}={v}" for k, v in args.items()])

            if ext == '.py':
                return [interpreter, "-c",
                        f"import {module_path} as f; f.{function_name}({formatted_args})"]
            elif ext == '.r':
                return [
                    interpreter, "-e", f'source("{script_path}"); {function_name}({formatted_args})']
            elif ext == '.jl':
                return [
                    interpreter, "-e", f'include("{script_path}"); {function_name}({formatted_args})']
            else:
                raise ValueError(
                    f"Function execution is not supported for scripts with extension '{ext}'.")
        else:
            # Build command for simple script execution
            if system == 'Linux':
                script_path = script_path.replace('\\', '/')
            elif system == 'Windows':
                script_path = script_path.replace('/', '\\')
            else:
                script_path = script_path.replace('/', '\\')
            command = [interpreter, script_path] if interpreter != 'executable' else [
                script_path]

            if not arg_format:
                if interpreter in ['executable', 'bash']:
                    arg_format = '-k v'
                elif ext in ['.exe', '.lnk']:
                    arg_format = '-k=v'
                else:
                    arg_format = '--k v'

            for key, value in args.items():
                if isinstance(value, str):
                    if ' ' in value:
                        # the string comes with quotes, which have to be removed later
                        value = f'"{value}"'
                elif isinstance(value, (int, float)):
                    value = str(value)
                elif isinstance(value, list):
                    value = " ".join(map(str, value))
                else:
                    value = str(value)

                if arg_format == 'k=v':
                    command.extend([f'{key}={value}'])
                elif arg_format == '-k=v':
                    command.extend([f'-{key}={value}'])
                elif arg_format == '-k v':
                    command.extend([f"-{key}", value])
                elif arg_format == '--k v':
                    command.extend([f"--{key}", value])
                elif arg_format == 'v':
                    command.extend([value])
                else:
                    command.extend([f"--{key}", value])

            if interpreter in ['executable']:
                if system == 'Linux':
                    command = " ".join(
                        [f'"{c}"' if ' ' in c else c for c in command])
                    command = ['bash', '-c', f'echo | {command}']
                elif system == 'Windows':
                    command = ['echo.|'] + command
                else:
                    command = ['echo.|'] + command

            return command

    @staticmethod
    def _run_command(command: list, background: bool = False, ok_code: int = 0, 
                     error: str = 'alert', cwd: str = os.getcwd(), timeout: int = None) -> subprocess.Popen:
        """
        Run a shell command and handle its output and errors.
        
        Args:
            command (list | str): The command to execute.
            background (bool): If True, run the command in the background.
            ok_code (int): Expected exit code (0 by default).
            error (str): 'raise', 'ignore', or 'alert' on error.
            cwd (str): Working directory.
            timeout (int): Timeout in seconds.

        Returns:
            subprocess.CompletedProcess or subprocess.Popen or None

        Raises:
            subprocess.SubprocessError: If the command exits with a non-ok return code.
        """
        logger.info(f"Executing command: {command}")
        system = platform.system()

        # Execute the command
        try:
            process = subprocess.run(
                command,
                stdout=(sys.stdout if system == "Windows" else None),
                stderr=(sys.stderr if system == "Windows" else None),
                text=True,  # Automatically decode byte streams to strings
                bufsize=1,  # Line-buffered output for real-time streaming
                cwd=cwd,    # Set the working directory
                # Execute the command through the shell
                shell=(True if system == "Windows" else False),
                timeout=timeout  # No timeout by default
            )
        except subprocess.TimeoutExpired:
            print(f"Command timed out after {timeout//60} minutes.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error running command: {e}")
            if error == 'raise':
                raise
            return None

        if background:
            logger.info("Running command in the background.")
            return process  # Do not wait for output or process completion in background mode

        # Capture and log output in real-time
        # Check return code only for foreground mode
        if process.returncode != ok_code:
            msg = f"Command '{command}' failed with exit code {process.returncode}."
            logger.error(msg)
            if error == 'raise':
                raise subprocess.SubprocessError(msg)
            elif error == 'ignore':
                pass
            else:
                logger.warning(msg)
        return process
