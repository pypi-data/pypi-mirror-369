import asyncio
import atexit
import signal
import functools
import inspect
import subprocess
import logging
import datetime
from typing import Optional, Dict, List, Any, Union


from swerex.deployment.docker import DockerDeployment
# from swerex.deployment.local import LocalDeployment
from swerex.runtime.abstract import CreateBashSessionRequest, BashAction, Command

from swerex.runtime.abstract import CreateBashSessionRequest, BashAction, Command

# Tools are now detected via ***ISTOOL*** tags in function docstrings
from .tools.core import CodeToolsInstance, CodeToolsConfig
from .utils.tool_stats import ToolCallStats

class CodeInstance:
    
    def __init__(self, type: str, config: Dict, stat: ToolCallStats = None, auto_start: bool = False):
        self.type = type
        self.config = config
        self.deployment = None
        self.tool_instance = None
        self.stats = stat if stat else ToolCallStats()
        self._is_started = False
        self._cleanup_registered = False
        self._swerex_handler = None  # Track our swerex handler for cleanup
        self._tool_call_history = []  # Store detailed history of tool calls
        
        # Setup internal swerex logging without affecting user's logging
        self._setup_swerex_logging()
        
        # Register cleanup handlers
        self._register_cleanup_handlers()
        
        type = "docker" # fix later 
        if type == "local":
            local_config = config.get('local', {})
            # self.deployment = LocalDeployment()

            
        elif type == "docker":
            # Check whether docker service is running
            if not self._check_docker_service():
                raise RuntimeError("Docker service is not running")
            
            deployment_params = config.get('docker', {})
            # Set default image if not provided
            if 'image' not in deployment_params:
                deployment_params['image'] = "python:3.12"
            
            self.deployment = DockerDeployment(**deployment_params)
        else:
            raise ValueError(f"Unsupported deployment type: {type}")
        
        # Get tool configuration
        tool_config = config.get('tool_config', {})
        self.tool_config = tool_config
        
        # Check if Jupyter is enabled in config
        self.jupyter_enabled = self.tool_config.get('jupyter_enabled', False)
        
        # Log Jupyter status
        if self.jupyter_enabled:
            logging.info("Jupyter tools enabled - will install jupyter-remote-runner during startup")
        else:
            logging.info("Jupyter tools not enabled - run_in_jupyter_ipython will not be available")
        
        # Available tools will be populated after tool_instance is created
        self.available_tool_names = []
        
        # Auto-start if requested
        if auto_start:
            self.start_sync()
    
    def _filter_tools_by_config(self) -> List[str]:
        """Filter tool names based on configuration settings."""
        
        # Get all available tool names (will be populated after tool_instance is created)
        if not hasattr(self, 'tool_instance') or not self.tool_instance:
            # Return empty list if tool_instance not yet created
            return []
        
        all_tools = self.get_available_tools()
        
        # Remove Jupyter tools if not enabled
        if not self.jupyter_enabled:
            jupyter_tools = ["run_in_jupyter_ipython"]
            all_tools = [tool for tool in all_tools if tool not in jupyter_tools]
        
        return all_tools
    
    async def _setup_jupyter(self):
        """Setup Jupyter environment by installing jupyter-remote-runner."""
        try:
            logging.info("Setting up Jupyter environment...")
            
            # Use the runtime to install jupyter-remote-runner
            from swerex.runtime.abstract import Command
            
            install_cmd = Command(
                command="pipx install jupyter-remote-runner",
                shell=True,
                timeout=300  # 5 minutes timeout for installation
            )
            
            response = await self.deployment.runtime.execute(install_cmd)
            
            if response.exit_code != 0:
                logging.warning(f"Failed to install jupyter-remote-runner: {response.stderr}")
                logging.info("Attempting alternative installation with pip...")
                
                # Try alternative installation method
                alt_install_cmd = Command(
                    command="pip install jupyter-remote-runner",
                    shell=True,
                    timeout=300
                )
                
                alt_response = await self.deployment.runtime.execute(alt_install_cmd)
                
                if alt_response.exit_code != 0:
                    raise Exception(f"Failed to install jupyter-remote-runner with both pipx and pip: {alt_response.stderr}")
                else:
                    logging.info("Successfully installed jupyter-remote-runner with pip")
            else:
                logging.info("Successfully installed jupyter-remote-runner with pipx")
                
        except Exception as e:
            logging.error(f"Failed to setup Jupyter environment: {e}")
            # Don't raise the exception - just log it and continue
            # This allows the instance to start even if Jupyter setup fails
            logging.warning("Continuing without Jupyter tools due to setup failure")
        
    def _check_docker_service(self) -> bool:
        """Check if Docker service is running"""
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _setup_swerex_logging(self):
        """Setup swerex logging - will temporarily enable during deployment"""
        # Store original root logger level
        root_logger = logging.getLogger()
        self._original_root_level = root_logger.level
        
        # Setup both swerex and rex-deploy loggers
        for logger_name in ['swerex', 'rex-deploy']:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            
            # Add a simple print handler if it doesn't have one
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setLevel(logging.DEBUG)
                
                # Try to use swerex's native formatter for colors
                try:
                    from swerex.utils.logging import get_formatter
                    formatter = get_formatter()
                    handler.setFormatter(formatter)
                except (ImportError, AttributeError):
                    # Simple formatter
                    formatter = logging.Formatter('%(message)s')
                    handler.setFormatter(formatter)
                
                logger.addHandler(handler)
                logger.propagate = False  # Don't interfere with other loggers
                
                # Store the handler for cleanup
                if not hasattr(self, '_swerex_handlers'):
                    self._swerex_handlers = []
                self._swerex_handlers.append((logger_name, handler))
        
    def _enable_deployment_logging(self):
        """Temporarily enable logging during deployment - clean version"""
        # No need to change root logger level since we have direct handlers
        pass
        
    def _restore_logging_level(self):
        """Clean version - no temporary changes needed"""
        pass
    
    def _cleanup_swerex_logging(self):
        """Clean up swerex logging handlers"""
        if hasattr(self, '_swerex_handlers'):
            for logger_name, handler in self._swerex_handlers:
                logger = logging.getLogger(logger_name)
                logger.removeHandler(handler)
                handler.close()
            self._swerex_handlers = []
    
    def _register_cleanup_handlers(self):
        """Register cleanup handlers for unexpected exits"""
        if not self._cleanup_registered:
            atexit.register(self._sync_cleanup)
            
            # Register signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                logging.info(f"Received signal {signum}, cleaning up...")
                self._sync_cleanup()
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            self._cleanup_registered = True
    
    def _format_tool_response(self, result, tool_name: str) -> str:
        """
        Convert tool response objects to human-readable string format.
        
        Args:
            result: The response object from the tool
            tool_name: Name of the tool that was called
            
        Returns:
            Formatted string representation of the response
        """
        import json
        import yaml
        
        # Handle different response types
        if hasattr(result, '__dict__'):
            # This is a response object, convert to string
            if hasattr(result, 'success'):
                if result.success:
                    # Handle successful responses
                    if tool_name == 'read_file' and hasattr(result, 'content'):
                        return f"File read successfully:\n\n{result.content}"
                    elif tool_name == 'write_file':
                        return f"File written successfully. Bytes written: {getattr(result, 'bytes_written', 'N/A')}"
                    elif tool_name == 'run_command' and hasattr(result, 'stdout'):
                        output = f"Command executed successfully.\n"
                        if result.stdout:
                            output += f"STDOUT:\n{result.stdout}\n"
                        if hasattr(result, 'stderr') and result.stderr:
                            output += f"STDERR:\n{result.stderr}\n"
                        if hasattr(result, 'exit_code'):
                            output += f"Exit code: {result.exit_code}"
                        return output
                    elif tool_name == 'list_directory':
                        # For list_directory, result might be a list
                        if isinstance(result, list):
                            output = "Directory listing:\n"
                            for item in result:
                                if isinstance(item, dict):
                                    output += f"  {item.get('type', 'file').upper()}: {item.get('name', 'unknown')} ({item.get('size_formatted', 'N/A')})\n"
                                else:
                                    output += f"  {item}\n"
                            return output
                        else:
                            return f"Directory listed successfully: {result.message}"
                    else:
                        # Generic successful response
                        return f"Operation completed successfully: {result.message}"
                else:
                    # Handle error responses
                    error_msg = f"Error: {result.message}"
                    if hasattr(result, 'details') and result.details:
                        error_msg += f"\nDetails: {result.details}"
                    if hasattr(result, 'suggestions') and result.suggestions:
                        error_msg += f"\nSuggestions:\n"
                        for suggestion in result.suggestions:
                            error_msg += f"  - {suggestion}\n"
                    return error_msg
            else:
                # Response object without success field, convert to JSON
                try:
                    return json.dumps(result.__dict__, indent=2, default=str)
                except:
                    return str(result)
        elif isinstance(result, list):
            # Handle list responses (like from grep_files, glob_files)
            if not result:
                return "No results found."
            
            # Try to format as structured output
            try:
                if all(isinstance(item, dict) for item in result):
                    # List of dictionaries - format nicely
                    output = f"Found {len(result)} results:\n\n"
                    for i, item in enumerate(result, 1):
                        output += f"{i}. "
                        if 'file' in item and 'line' in item:
                            # Grep-style result
                            output += f"{item['file']}:{item['line']} - {item.get('content', '')}\n"
                        elif 'name' in item and 'type' in item:
                            # Directory listing result
                            output += f"{item['type'].upper()}: {item['name']}\n"
                        else:
                            # Generic dict result
                            output += f"{json.dumps(item, indent=2)}\n"
                    return output
                else:
                    # List of strings or other simple types
                    return f"Results ({len(result)} items):\n" + "\n".join(f"  - {item}" for item in result)
            except:
                return f"Results: {result}"
        elif isinstance(result, dict):
            # Handle dictionary responses
            if 'success' in result:
                if result['success']:
                    return f"Operation successful: {result.get('message', 'No message')}"
                else:
                    return f"Operation failed: {result.get('message', 'No message')}"
            else:
                # Generic dictionary - convert to readable format
                try:
                    return yaml.dump(result, default_flow_style=False, indent=2)
                except:
                    return json.dumps(result, indent=2, default=str)
        else:
            # Handle simple types (str, int, bool, etc.)
            return str(result)
    
    def _sync_cleanup(self):
        """Synchronous cleanup for atexit and signal handlers"""
        if self._is_started and self.deployment:
            try:
                # Check if there's already an event loop running
                try:
                    current_loop = asyncio.get_running_loop()
                    # If there's a running loop, we can't use run_until_complete
                    # Instead, schedule the cleanup as a task
                    if current_loop and not current_loop.is_closed():
                        task = current_loop.create_task(self.cleanup())
                        # Wait for the task to complete
                        import time
                        timeout = 5.0  # 5 second timeout
                        start_time = time.time()
                        while not task.done() and (time.time() - start_time) < timeout:
                            time.sleep(0.1)
                        if not task.done():
                            task.cancel()
                        return
                except RuntimeError:
                    # No running loop, create a new one
                    pass
                
                # Run async cleanup in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.cleanup())
                finally:
                    # Ensure the loop is properly closed
                    try:
                        # Cancel any remaining tasks
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        # Wait for cancellation if there are tasks
                        if pending:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass
                    loop.close()
            except Exception as e:
                logging.error(f"Error during cleanup: {e}")
            finally:
                # Always cleanup logging handler even if async cleanup failed
                self._cleanup_swerex_logging()
    
    def __del__(self):
        """Destructor to ensure logging cleanup"""
        try:
            self._cleanup_swerex_logging()
        except:
            pass  # Ignore errors during destruction
    
    async def start(self):
        """Start the deployment and initialize tools"""
        if self._is_started:
            return
        
        try:
            # Enable logging during deployment startup
            self._enable_deployment_logging()
            
            await self.deployment.start()
            self.tool_instance = CodeToolsInstance(self.deployment)

            # Setup Jupyter if enabled
            if self.jupyter_enabled:
                await self._setup_jupyter()

            # Populate available tools after tool_instance is created
            self.available_tool_names = self._filter_tools_by_config()

            self._is_started = True
            
            # Restore original logging level after deployment is started
            self._restore_logging_level()
            
        except Exception as e:
            # Make sure to restore logging level even on error
            self._restore_logging_level()
            logging.error(f"Failed to start CodeInstance: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources and stop deployment"""
        if not self._is_started:
            return
        
        try:
            if self.deployment:
                # Ensure the stop coroutine is properly awaited
                try:
                    await self.deployment.stop()
                except Exception as e:
                    logging.error(f"Error stopping deployment: {e}")
                    # Try to force cleanup if normal stop fails
                    try:
                        if hasattr(self.deployment, 'cleanup'):
                            await self.deployment.cleanup()
                    except Exception:
                        pass
            self._is_started = False
        except Exception as e:
            logging.error(f"Error during deployment cleanup: {e}")
            raise
        finally:
            # Always cleanup our swerex logging handler
            self._cleanup_swerex_logging()
    
    def start_sync(self):
        """Synchronous version of start() - starts the deployment and initializes tools"""
        if self._is_started:
            return
        
        # Create and run event loop for async operations
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start())
        except Exception as e:
            logging.error(f"Failed to start CodeInstance synchronously: {e}")
            raise
        finally:
            try:
                loop.close()
            except:
                pass

        #todo add installations about venv etc, to install additional tools
    
    def stop_sync(self):
        """Synchronous version of cleanup() - cleans up resources and stops deployment"""
        if not self._is_started:
            return
        
        # Use asyncio.run() for clean event loop management like CodeEnv.py
        try:
            asyncio.run(self.cleanup())
        except Exception as e:
            logging.error(f"Failed to stop CodeInstance synchronously: {e}")
            raise
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        return False
    
    def __enter__(self):
        """Sync context manager entry (not recommended for async operations)"""
        # For sync usage, we need to handle this differently
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.cleanup())
        return False

    def get_available_tools(self):
        # Get tool names from tagged methods
        method_tools = self.get_method_tools()
        return [tool["method_name"] for tool in method_tools]
    
    
    def get_tool_call_stats(self):
        """Get the tool call statistics object"""
        return self.stats
        
    def get_usage_summary(self):
        """Get comprehensive usage summary"""
        return self.stats.get_usage_summary()
    
    def export_tool_stats(self):
        """Export tool statistics to JSON format"""
        return self.stats.export_stats_to_json()
    
    def get_history(self):
        """Get detailed history of all tool calls with parameters and outputs"""
        return self._tool_call_history.copy()
    
    def print_history(self):
        """Print the complete history of tool calls in a readable format"""
        if not self._tool_call_history:
            print("No tool calls have been made yet.")
            return
        
        print(f"\n=== Tool Call History ({len(self._tool_call_history)} calls) ===")
        for i, call in enumerate(self._tool_call_history, 1):
            print(f"\n{i}. Tool: {call['tool_name']}")
            print(f"   Timestamp: {call['timestamp']}")
            print(f"   Parameters: {call['parameters']}")
            print(f"   Success: {call['success']}")
            if call['success']:
                print(f"   Output: {call['output'][:500]}{'...' if len(str(call['output'])) > 500 else ''}")
            else:
                print(f"   Error: {call['error_message']}")
            print(f"   Duration: {call['duration']:.3f}s")
            print("-" * 50)
    
    def get_method_tools(self):
        new_method_list = []
        
        # Get methods from the tool instance
        if not self.tool_instance:
            return new_method_list
            
        instance_methods = dict(inspect.getmembers(self.tool_instance, predicate=inspect.ismethod))
        
        # Scan for methods with ***ISTOOL*** tag in their docstrings
        for method_name, method in instance_methods.items():
            if hasattr(method, '__doc__') and method.__doc__:
                doc = method.__doc__.strip()
                if doc.startswith('***ISTOOL***'):
                    # Extract description by removing the tag
                    description = doc.replace('***ISTOOL***', '', 1).strip()
                    tool = {
                        "method_name": method_name,
                        "method_type": "inbuilt",
                        "description": description
                    }
                    new_method_list.append(tool)
        
        return new_method_list
    
    def get_tools(self, include: List[str] = None):
        newkeys = []
        tools_keys = self.get_available_tools()
        
        if include:
            for key in include:
                if key in tools_keys:
                    newkeys.append(key)
                else:
                    raise ValueError(f"Unrecognized tool: {key}")
        else:
            newkeys = tools_keys
        
        return self._wrap_specific_methods(allowed_methods=newkeys)


    def _wrap_specific_methods(self, allowed_methods: list[str]) -> list[Any]:
        """
        Wrap only specific methods based on allowed_methods list.
        """
        tool_list = []
        
        methods_dict_list = self.get_method_tools()
        
        # Get methods from the tool instance
        if not self.tool_instance:
            raise RuntimeError("CodeInstance not started. Call start() first or use as async context manager.")
        
        instance_methods = dict(inspect.getmembers(self.tool_instance, predicate=inspect.ismethod))
        # conversationtools_methods = dict(inspect.getmembers(self, predicate=inspect.ismethod))
        
        for meth in methods_dict_list:
            name = meth['method_name']
            
            if name not in allowed_methods:
                continue
                
            des = meth['description'] if 'description' in meth else None
            method_type = meth.get('method_type', 'inbuilt')
            
            # Choose the right method source based on method_type
            if method_type == 'inbuilt':
                if name not in instance_methods:
                    raise ValueError(f"Inbuilt method '{name}' not found in the instance.")
                method = instance_methods[name]
            else: # TODO Add custom tool like finish and sleep
                if name not in instance_methods:
                    raise ValueError(f"Inbuilt method '{name}' not found in the instance.")
                method = instance_methods[name]

            sig = inspect.signature(method)
            doc = des or "No description available."

            # Capture method in local variable to prevent late binding issue
            def make_tool(func, stats_obj):
                # Check if function is async
                is_async = inspect.iscoroutinefunction(func)
                
                @functools.wraps(func)
                def tool_func(**kwargs):
                    # Record call start and track statistics
                    start_time = stats_obj.record_call_start(func.__name__)
                    call_timestamp = datetime.datetime.now().isoformat()
                    
                    try:
                        if is_async:
                            # For async functions, run them in an event loop
                            import asyncio
                            try:
                                # Try to get the current event loop
                                try:
                                    loop = asyncio.get_running_loop()
                                    # If loop is already running, create a new thread to run the async function
                                    import concurrent.futures
                                    
                                    def run_async():
                                        # Create new event loop for this thread
                                        new_loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(new_loop)
                                        try:
                                            return new_loop.run_until_complete(func(**kwargs))
                                        finally:
                                            # Properly close the loop with all tasks
                                            try:
                                                pending = asyncio.all_tasks(new_loop)
                                                for task in pending:
                                                    task.cancel()
                                                if pending:
                                                    new_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                                            except Exception:
                                                pass
                                            new_loop.close()
                                    
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        future = executor.submit(run_async)
                                        result = future.result()
                                        
                                except RuntimeError:
                                    # No running event loop, try to get event loop or create one
                                    try:
                                        loop = asyncio.get_event_loop()
                                        if loop.is_closed():
                                            raise RuntimeError("Event loop is closed")
                                        result = loop.run_until_complete(func(**kwargs))
                                    except (RuntimeError, AttributeError):
                                        # Create a new event loop
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        try:
                                            result = loop.run_until_complete(func(**kwargs))
                                        finally:
                                            # Properly close the loop
                                            try:
                                                pending = asyncio.all_tasks(loop)
                                                for task in pending:
                                                    task.cancel()
                                                if pending:
                                                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                                            except Exception:
                                                pass
                                            loop.close()
                            except Exception as async_error:
                                # Fallback: try asyncio.run (Python 3.7+)
                                try:
                                    result = asyncio.run(func(**kwargs))
                                except Exception:
                                    # Ultimate fallback - re-raise the original async error
                                    raise async_error
                        else:
                            # Execute sync function normally
                            result = func(**kwargs)
                        
                        # Record successful completion
                        stats_obj.record_call_end(func.__name__, start_time, success=True)
                        
                        # Convert response objects to string format for agent compatibility
                        formatted_result = self._format_tool_response(result, func.__name__)
                        
                        # Calculate duration
                        import time
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        # Add to history
                        history_entry = {
                            'tool_name': func.__name__,
                            'timestamp': call_timestamp,
                            'parameters': kwargs.copy(),
                            'success': True,
                            'output': formatted_result,
                            'error_message': None,
                            'duration': duration
                        }
                        self._tool_call_history.append(history_entry)
                        
                        return formatted_result
                        
                    except Exception as e:
                        # Record failed completion
                        stats_obj.record_call_end(func.__name__, start_time, success=False, error_message=str(e))
                        
                        # Calculate duration
                        import time
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        # Add failed call to history
                        history_entry = {
                            'tool_name': func.__name__,
                            'timestamp': call_timestamp,
                            'parameters': kwargs.copy(),
                            'success': False,
                            'output': None,
                            'error_message': str(e),
                            'duration': duration
                        }
                        self._tool_call_history.append(history_entry)
                        
                        # Re-raise the exception to maintain original behavior
                        raise

                tool_func.__name__ = func.__name__
                tool_func.__doc__ = doc
                tool_func.__signature__ = sig
                return tool_func

            tool_list.append(make_tool(method, self.stats))

        return tool_list
    
    def is_running(self) -> bool:
        """Check if the CodeInstance is currently running"""
        return self._is_started
    
    def get_deployment_type(self) -> str:
        """Get the deployment type (docker or local)"""
        return self.type
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get information about the current deployment"""
        return {
            'type': self.type,
            'is_running': self._is_started,
            'config': self.config,
            'tool_config': self.tool_config
        }
    
    def _format_tool_response(self, result: Any, tool_name: str) -> str:
        """
        Format tool response objects into string format for agent compatibility.
        
        Args:
            result: The result from the tool function
            tool_name: Name of the tool that was called
            
        Returns:
            Formatted string representation of the result
        """
        # Import response classes locally to avoid circular imports
        from .tools.core import (
            FileReadResponse, FileWriteResponse, FileEditResponse, 
            CommandResponse, SearchResponse, ToolResponse
        )
        
        # Handle different response types
        if isinstance(result, FileReadResponse):
            if result.success:
                output = f"✓ File read successfully: {result.message}\n"
                if result.content:
                    output += f"Content:\n{result.content}"
                if result.is_truncated:
                    output += f"\n[Showing {result.lines_shown}/{result.total_lines} lines]"
                return output
            else:
                output = f"✗ Failed to read file: {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                if result.suggestions:
                    output += f"\nSuggestions: {', '.join(result.suggestions)}"
                return output
                
        elif isinstance(result, FileWriteResponse):
            if result.success:
                output = f"✓ File operation successful: {result.message}"
                if result.bytes_written:
                    output += f"\nBytes written: {result.bytes_written}"
                return output
            else:
                output = f"✗ File write failed: {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                if result.suggestions:
                    output += f"\nSuggestions: {', '.join(result.suggestions)}"
                return output
                
        elif isinstance(result, FileEditResponse):
            if result.success:
                output = f"✓ File edited successfully: {result.message}"
                if result.replacements_made:
                    output += f"\nReplacements made: {result.replacements_made}"
                if result.preview:
                    output += f"\nPreview of changes:\n{result.preview}"
                return output
            else:
                output = f"✗ File edit failed: {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                if result.suggestions:
                    output += f"\nSuggestions: {', '.join(result.suggestions)}"
                return output
                
        elif isinstance(result, CommandResponse):
            if result.success:
                output = f"✓ Command executed: {result.command}"
                if result.exit_code is not None:
                    output += f"\nExit code: {result.exit_code}"
                if result.stdout:
                    output += f"\nOutput:\n{result.stdout}"
                if result.stderr:
                    output += f"\nError output:\n{result.stderr}"
                if result.session_name:
                    output += f"\nSession: {result.session_name}"
                return output
            else:
                output = f"✗ Command failed: {result.command}"
                if result.exit_code is not None:
                    output += f"\nExit code: {result.exit_code}"
                if result.stderr:
                    output += f"\nError: {result.stderr}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                return output
                
        elif isinstance(result, SearchResponse):
            if result.success:
                output = f"✓ Search completed: Found {result.total_matches} matches in {result.files_searched} files"
                for match in result.matches[:10]:  # Show first 10 matches
                    output += f"\n{match.file}:{match.line}: {match.content}"
                if len(result.matches) > 10:
                    output += f"\n... and {len(result.matches) - 10} more matches"
                return output
            else:
                output = f"✗ Search failed: {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                return output
                
        elif isinstance(result, ToolResponse):
            if result.success:
                output = f"✓ {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                return output
            else:
                output = f"✗ {result.message}"
                if result.details:
                    output += f"\nDetails: {result.details}"
                if result.suggestions:
                    output += f"\nSuggestions: {', '.join(result.suggestions)}"
                return output
        
        # Handle list results (like from list_directory, glob_files, etc.)
        elif isinstance(result, list):
            if not result:
                return f"✓ {tool_name} completed: No results found"
            
            # Format list results based on content
            if all(isinstance(item, dict) for item in result):
                # Directory listing or similar structured data
                output = f"✓ {tool_name} completed: Found {len(result)} items\n"
                for item in result[:20]:  # Show first 20 items
                    if 'name' in item and 'type' in item:
                        # Directory listing format
                        size_info = f" ({item.get('size_formatted', '')})" if item.get('size_formatted') else ""
                        output += f"{item['type']}: {item['name']}{size_info}\n"
                    elif 'file' in item and 'line' in item:
                        # Search results format
                        output += f"{item['file']}:{item['line']}: {item.get('content', '')}\n"
                    else:
                        # Generic dict format
                        output += f"{item}\n"
                if len(result) > 20:
                    output += f"... and {len(result) - 20} more items"
                return output.rstrip()
            else:
                # Simple list of strings
                output = f"✓ {tool_name} completed: Found {len(result)} items\n"
                for item in result[:20]:
                    output += f"{item}\n"
                if len(result) > 20:
                    output += f"... and {len(result) - 20} more items"
                return output.rstrip()
        
        # Handle dictionary results
        elif isinstance(result, dict):
            if 'success' in result:
                # Legacy dict format
                if result.get('success'):
                    return f"✓ {tool_name} completed successfully\nResult: {result}"
                else:
                    return f"✗ {tool_name} failed: {result.get('error', 'Unknown error')}"
            else:
                # Generic dict result
                import json
                return f"✓ {tool_name} completed\nResult:\n{json.dumps(result, indent=2)}"
        
        # Handle primitive types
        elif isinstance(result, (str, int, float, bool)):
            return f"✓ {tool_name} completed\nResult: {result}"
        
        # Fallback for any other type
        else:
            return f"✓ {tool_name} completed\nResult: {str(result)}"


# Example usage:
# 
# async def main():
#     config = {
#         'docker': {'image': 'python:3.12'},
#         'tool_config': {}
#     }
#     
#     # Using async context manager (recommended)
#     async with CodeInstance('docker', config) as instance:
#         tools = instance.get_tools()
#         # Use tools...
#     
#     # Or manual lifecycle management
#     instance = CodeInstance('docker', config)
#     await instance.start()
#     try:
#         tools = instance.get_tools()
#         # Use tools...
#     finally:
#         await instance.cleanup()
# 
# asyncio.run(main())