#!/usr/bin/env python3

import socket
import subprocess
import sys
from typing import List, Optional

from rich.console import Console
from rich.prompt import IntPrompt
from rich.table import Table

from .kubernetes import KubernetesClient, ServiceInfo


class ServiceSelector:
    """Interactive service selector with colored output."""

    def __init__(self, k8s_client: KubernetesClient):
        self.k8s_client = k8s_client
        self._check_kubectl()
        self.console = Console()

    def _check_kubectl(self):
        """Check if kubectl is available."""
        try:
            subprocess.run(["kubectl", "version"], capture_output=True, check=True)
        except FileNotFoundError:
            raise RuntimeError(
                "kubectl command not found. Please install kubectl and ensure it's in your PATH."
            )
        except subprocess.CalledProcessError as e:
            # Get the actual error output from kubectl
            error_output = e.stderr.decode("utf-8") if e.stderr else "No error output available"
            stdout_output = e.stdout.decode("utf-8") if e.stdout else "No output available"

            raise RuntimeError(
                f"kubectl command failed with exit code {e.returncode}.\n"
                f"Error output: {error_output}\n"
                f"Standard output: {stdout_output}\n"
                f"Please check your kubectl configuration and ensure you have proper access to the cluster."
            )

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available on localhost."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("localhost", port))
                return True
        except OSError:
            return False

    def _find_available_port(self, starting_port: int, max_attempts: int = 10) -> int:
        """Find the next available port starting from the given port."""
        for port in range(starting_port, starting_port + max_attempts):
            if self._is_port_available(port):
                return port
        # If no port found in range, return the original (let it fail naturally)
        return starting_port

    def select_service_in_namespace(
        self,
        namespace: Optional[str] = None,
        include_all_ports: bool = False,
        check_endpoints: bool = False,
    ) -> List[str]:
        """Select a service interactively within a specific namespace."""
        if not namespace:
            namespace = self.k8s_client.get_current_namespace()

        self.console.print(f"\n[bold cyan]Services in namespace: {namespace}[/bold cyan]")

        # Get services
        services = self.k8s_client.get_services_in_namespace(namespace, check_endpoints)

        # Optionally include pods and deployments
        all_resources = services.copy()
        if include_all_ports:
            pods = self.k8s_client.get_pods_with_ports(namespace)
            deployments = self.k8s_client.get_deployments_with_ports(namespace)
            all_resources.extend(pods)
            all_resources.extend(deployments)
            all_resources.sort(key=lambda r: (r.service_type, r.name))

        if not all_resources:
            self.console.print(f"[yellow]No resources found in namespace '{namespace}'[/yellow]")
            return []

        # Display table
        self._display_services_table(
            all_resources,
            check_endpoints=check_endpoints,
            include_all_ports=include_all_ports,
        )

        # Get user selection
        return self._prompt_for_service_selection(
            all_resources,
            namespace,
            show_namespace=False,
            include_all_ports=include_all_ports,
            check_endpoints=check_endpoints,
        )

    def select_service_all_namespaces(
        self, include_all_ports: bool = False, check_endpoints: bool = False
    ) -> List[str]:
        """Select a service interactively across all namespaces."""
        if include_all_ports:
            self.console.print("\n[bold cyan]Getting ports across all namespaces...[/bold cyan]")
        else:
            self.console.print("\n[bold cyan]Getting services across all namespaces...[/bold cyan]")

        # Get all services
        all_services_by_ns = self.k8s_client.get_all_services(check_endpoints)

        if not all_services_by_ns:
            self.console.print("[yellow]No services found in any namespace[/yellow]")
            return []

        # Flatten and add pods/deployments if requested
        all_resources = []
        for namespace, services in all_services_by_ns.items():
            all_resources.extend(services)

            if include_all_ports:
                pods = self.k8s_client.get_pods_with_ports(namespace)
                deployments = self.k8s_client.get_deployments_with_ports(namespace)
                all_resources.extend(pods)
                all_resources.extend(deployments)

        # Sort by namespace, then type, then name
        all_resources.sort(key=lambda r: (r.namespace, r.service_type, r.name))

        # Display table
        self._display_services_table(
            all_resources,
            show_namespace=True,
            check_endpoints=check_endpoints,
            include_all_ports=include_all_ports,
        )

        # Get user selection
        return self._prompt_for_service_selection(
            all_resources,
            show_namespace=True,
            include_all_ports=include_all_ports,
            check_endpoints=check_endpoints,
        )

    def _build_services_table(
        self,
        resources: List[ServiceInfo],
        show_namespace: bool = False,
        check_endpoints: bool = False,
        include_all_ports: bool = False,
        selected_index: Optional[int] = None,
    ) -> Table:
        """Build services table with zebra striping and optional selected row highlight."""
        table = Table()
        table.row_styles = ["", "dim"]

        table.add_column("#", style="dim", width=4)
        if show_namespace:
            table.add_column("Namespace", style="cyan")
        if include_all_ports:
            table.add_column("Type", style="magenta")
        table.add_column("Name", style="bold")
        table.add_column("Ports", style="cyan")

        if check_endpoints:
            table.add_column("Status", justify="center")

        for i, resource in enumerate(resources, 1):
            row = [
                str(i),
                resource.name,
                resource.port_summary,
            ]

            if show_namespace:
                row.insert(1, resource.namespace)

            if include_all_ports:
                type_value = resource.service_type.lower()
                if show_namespace:
                    row.insert(2, type_value)
                else:
                    row.insert(1, type_value)

            if check_endpoints:
                status_color = "green" if resource.has_endpoints else "red"
                status_text = "✓" if resource.has_endpoints else "✗"
                row.append(f"[{status_color}]{status_text}[/{status_color}]")

            style = "bold reverse" if (selected_index is not None and i == selected_index) else None
            table.add_row(*row, style=style)

        return table

    def _display_services_table(
        self,
        resources: List[ServiceInfo],
        show_namespace: bool = False,
        check_endpoints: bool = False,
        include_all_ports: bool = False,
    ):
        """Display services in a colored table."""
        table = self._build_services_table(
            resources,
            show_namespace=show_namespace,
            check_endpoints=check_endpoints,
            include_all_ports=include_all_ports,
        )
        self.console.print(table)

        if check_endpoints:
            self.console.print("\n[green]✓[/green] = Has endpoints  [red]✗[/red] = No endpoints")

    def _prompt_for_service_selection(
        self,
        resources: List[ServiceInfo],
        namespace: Optional[str] = None,
        *,
        show_namespace: Optional[bool] = None,
        include_all_ports: Optional[bool] = None,
        check_endpoints: Optional[bool] = None,
    ) -> List[str]:
        """Prompt user to select a service and return port-forward arguments."""
        # First, try an interactive keyboard navigation if available
        selection: Optional[int] = None
        try:
            # Only attempt interactive navigation in a TTY
            if sys.stdin.isatty() and sys.stdout.isatty():
                try:
                    # Lazy imports (optional dependency)
                    from readchar import key, readkey
                    from rich.live import Live

                    # Resolve layout flags
                    show_namespace_flag = (
                        namespace is None if show_namespace is None else show_namespace
                    )
                    include_all_ports_flag = (
                        include_all_ports if include_all_ports is not None else False
                    )
                    check_endpoints_flag = bool(check_endpoints)

                    current_index = 1
                    max_index = len(resources)

                    def build_view() -> Table:
                        return self._build_services_table(
                            resources,
                            show_namespace=show_namespace_flag,
                            check_endpoints=check_endpoints_flag,
                            include_all_ports=include_all_ports_flag,
                            selected_index=current_index,
                        )

                    help_text = "Use ↑/↓ or j/k to navigate, Enter to select, Esc/q to cancel, digits to type index"

                    with Live(
                        build_view(),
                        console=self.console,
                        refresh_per_second=20,
                        transient=True,
                    ) as live:
                        self.console.print(help_text, style="dim")
                        typed_number = ""
                        while True:
                            ch = readkey()
                            if ch in (key.UP, "k"):
                                current_index = max(1, current_index - 1)
                                typed_number = ""
                                live.update(build_view())
                            elif ch in (key.DOWN, "j"):
                                current_index = min(max_index, current_index + 1)
                                typed_number = ""
                                live.update(build_view())
                            elif ch in (key.ENTER, "\r", "\n"):
                                selection = int(typed_number) if typed_number else current_index
                                break
                            elif ch in (key.ESC, "q"):
                                selection = None
                                break
                            elif ch.isdigit():
                                typed_number += ch
                                try:
                                    preview = int(typed_number)
                                    if 1 <= preview <= max_index:
                                        current_index = preview
                                        live.update(build_view())
                                except ValueError:
                                    pass
                            else:
                                # ignore other keys
                                pass
                except Exception:
                    selection = None

            # Fall back to numeric selection if interactive not used or cancelled
            if selection is None:
                selection = IntPrompt.ask("\nSelect a service", default=1, show_default=True)

            if selection < 1 or selection > len(resources):
                self.console.print("[red]Invalid selection[/red]")
                return []

            selected_resource = resources[selection - 1]

            # If no ports available, can't port-forward
            if not selected_resource.ports:
                self.console.print(
                    f"[red]Service '{selected_resource.name}' has no ports defined[/red]"
                )
                return []

            # Always prompt for port selection (even with single port)
            return self._prompt_for_port_selection(selected_resource)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Service selection cancelled (Ctrl+C)[/yellow]")
            return []

    def _prompt_for_port_selection(self, resource: ServiceInfo) -> List[str]:
        """Prompt user to select a port when multiple are available."""
        self.console.print(f"\n[bold]Available ports for {resource.name}:[/bold]")

        port_table = Table()
        # Zebra striping for port selection table as well
        port_table.row_styles = ["", "dim"]
        port_table.add_column("#", style="dim", width=4)
        port_table.add_column("Port", style="bold")
        port_table.add_column("Protocol", style="cyan")
        port_table.add_column("Name", style="green")

        for i, port in enumerate(resource.ports, 1):
            port_table.add_row(
                str(i),
                str(port["port"]),
                port.get("protocol", "TCP"),
                port.get("name", ""),
            )

        self.console.print(port_table)

        try:
            port_selection = IntPrompt.ask("Select a port", default=1, show_default=True)

            if port_selection < 1 or port_selection > len(resource.ports):
                self.console.print("[red]Invalid port selection[/red]")
                return []

            selected_port = resource.ports[port_selection - 1]["port"]
            local_port = self._prompt_for_local_port(selected_port)

            args = [
                f"{resource.service_type}/{resource.name}",
                f"{local_port}:{selected_port}",
                "-n",
                resource.namespace,
            ]
            return args

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Port selection cancelled (Ctrl+C)[/yellow]")
            return []

    def _prompt_for_local_port(self, remote_port: int) -> int:
        """Prompt user for local port, defaulting to remote port or suggesting alternative if in use."""
        try:
            # If remote port is privileged (< 1024), suggest adding 1000
            if remote_port < 1024:
                suggested_port = remote_port + 1000
                self.console.print(
                    f"[cyan]Service port {remote_port} is privileged (< 1024), suggesting {suggested_port}[/cyan]"
                )

                # Check if suggested port is available
                if self._is_port_available(suggested_port):
                    local_port = IntPrompt.ask(
                        f"Local port (press Enter for {suggested_port})",
                        default=suggested_port,
                        show_default=False,
                    )
                else:
                    # Suggested port is in use, find next available
                    alternative_port = self._find_available_port(suggested_port + 1)
                    self.console.print(f"[yellow]Port {suggested_port} is already in use[/yellow]")
                    local_port = IntPrompt.ask(
                        f"Local port (press Enter for {alternative_port})",
                        default=alternative_port,
                        show_default=False,
                    )
            else:
                # Non-privileged port logic (existing behavior)
                # Check if the remote port is available
                if self._is_port_available(remote_port):
                    # Port is available, use as default
                    local_port = IntPrompt.ask(
                        f"Local port (press Enter for {remote_port})",
                        default=remote_port,
                        show_default=False,
                    )
                else:
                    # Port is in use, find an available alternative
                    suggested_port = self._find_available_port(remote_port + 1)
                    self.console.print(f"[yellow]Port {remote_port} is already in use[/yellow]")
                    local_port = IntPrompt.ask(
                        f"Local port (press Enter for {suggested_port})",
                        default=suggested_port,
                        show_default=False,
                    )

            # Validate the chosen port and warn if it's in use
            if not self._is_port_available(local_port):
                self.console.print(
                    f"[yellow]Warning: Port {local_port} appears to be in use[/yellow]"
                )

            return local_port
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Port input cancelled (Ctrl+C)[/yellow]")
            sys.exit(0)
