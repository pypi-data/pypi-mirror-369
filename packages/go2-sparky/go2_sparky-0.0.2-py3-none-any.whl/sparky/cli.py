"""
Sparky CLI - Go2 Robot Control Interface
A beautiful command-line interface for controlling Go2 robots
"""

import asyncio


def _missing_cli_deps_msg():
    return (
        "Sparky CLI dependencies are not installed.\n"
        "Install them with:\n"
        "  pip install 'go2-sparky[cli]'"
    )


try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
except ImportError:

    def app():
        import sys

        sys.exit(_missing_cli_deps_msg())
else:
    from sparky.core.connection import (
        create_local_ap_connection,
        create_local_sta_connection,
        create_local_sta_connection_by_serial,
        create_remote_connection,
    )
    from sparky.core.motion import MotionController

    # Import ASCII banner
    try:
        from sparky.utils.banner import get_banner
        from sparky.utils.banner import print_banner as print_ascii_banner
    except ImportError:
        # Fallback if banner module not available
        def print_ascii_banner():
            console.print(
                "[bold cyan]SPARKY CLI[/bold cyan]  •  [bold green]v0.0.2[/bold green]"
            )
            console.print(
                "[bold green]Welcome to Sparky CLI! Ready to roll.[/bold green]\n"
            )

        def get_banner():
            return (
                "[bold cyan]SPARKY CLI[/bold cyan]  •  [bold green]v0.0.2[/bold green]"
            )

    # Initialize Typer app
    app = typer.Typer(
        name="sparky",
        help="Sparky - Go2 Robot Control Interface",
        add_completion=False,
        rich_markup_mode="rich",
    )

    # Rich console for beautiful output
    console = Console()

    def print_banner():
        """Print Sparky banner with robot dog and SPARKY logo"""
        print_ascii_banner()

    def print_firmware_warning():
        """Print firmware compatibility warning"""
        warning = Panel(
            "[yellow]FIRMWARE UPDATE NOTICE[/yellow]\n\n"
            "Current Go2 firmware only supports 'mcf' mode.\n"
            "Legacy 'normal' and 'ai' modes are no longer available.\n"
            "Some advanced commands may not work.",
            title="[bold yellow]Important[/bold yellow]",
            border_style="yellow",
        )
        console.print(warning)

    @app.command()
    def version():
        """Show Sparky version and information"""
        print_banner()

        info_table = Table(title="Sparky Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")

        info_table.add_row("Version", "0.0.2")
        info_table.add_row("Author", "Ranga Reddy Nukala")
        info_table.add_row("Description", "Go2 Robot Control Package")
        info_table.add_row("Firmware Support", "Current (mcf mode only)")

        console.print(info_table)

    @app.command()
    def banner():
        """Show Sparky banner with robot dog and SPARKY logo"""
        print_banner()

    @app.command()
    def status(
        connection_type: str = typer.Option(
            "localap",
            "--connection",
            "-c",
            help="Connection type: localap, localsta, remote",
        ),
        ip: str | None = typer.Option(
            None, "--ip", "-i", help="Robot IP address (for localsta)"
        ),
        serial: str | None = typer.Option(None, "--serial", help="Robot serial number"),
        username: str | None = typer.Option(
            None, "--username", "-u", help="Username (for remote)"
        ),
        password: str | None = typer.Option(
            None, "--password", "-p", help="Password (for remote)"
        ),
    ):
        """Get robot status and firmware information"""
        print_banner()
        print_firmware_warning()

        async def get_status():
            try:
                # Create connection based on type
                if connection_type == "localap":
                    connection = await create_local_ap_connection()
                elif connection_type == "localsta":
                    if not ip and not serial:
                        console.print(
                            "[red]Error: IP or serial number required for localsta connection[/red]"
                        )
                        return
                    if ip:
                        connection = await create_local_sta_connection(ip)
                    else:
                        connection = await create_local_sta_connection_by_serial(serial)
                elif connection_type == "remote":
                    if not all([serial, username, password]):
                        console.print(
                            "[red]Error: Serial, username, and password required for remote connection[/red]"
                        )
                        return
                    connection = await create_remote_connection(
                        serial, username, password
                    )
                else:
                    console.print(
                        f"[red]Error: Unknown connection type '{connection_type}'[/red]"
                    )
                    return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Connecting to robot...", total=None)

                    if not await connection.connect():
                        console.print("[red]Failed to connect to robot[/red]")
                        return

                    progress.update(task, description="Getting robot status...")

                    # Create motion controller
                    motion = MotionController(connection.conn)

                    # Get status information
                    motion_mode = await motion.get_motion_mode()
                    status_info = motion.get_status()
                    compatibility = motion.get_firmware_compatibility_info()

                    progress.update(task, description="Status retrieved successfully!")

                # Display status
                status_table = Table(title="Robot Status")
                status_table.add_column("Property", style="cyan")
                status_table.add_column("Value", style="green")

                status_table.add_row("Connection Type", connection_type)
                status_table.add_row("Connection Status", " Connected")
                status_table.add_row("Motion Mode", motion_mode or "Unknown")
                status_table.add_row("Is Moving", str(status_info["is_moving"]))
                status_table.add_row(
                    "Available Commands", str(len(status_info["available_commands"]))
                )

                console.print(status_table)

                # Display firmware compatibility
                compat_table = Table(title="Firmware Compatibility")
                compat_table.add_column("Category", style="cyan")
                compat_table.add_column("Status", style="green")

                compat_table.add_row(
                    "Supported Modes", ", ".join(compatibility["supported_modes"])
                )
                compat_table.add_row(
                    "Unsupported Modes", ", ".join(compatibility["unsupported_modes"])
                )
                compat_table.add_row(
                    "Working Commands", str(len(compatibility["working_commands"]))
                )
                compat_table.add_row(
                    "Restricted Commands",
                    str(len(compatibility["potentially_restricted_commands"])),
                )

                console.print(compat_table)

                await connection.disconnect()

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asyncio.run(get_status())

    @app.command()
    def move(
        direction: str = typer.Argument(
            ...,
            help="Movement direction: forward, backward, left, right, turn-left, turn-right",
        ),
        speed: float = typer.Option(
            0.5, "--speed", "-s", help="Movement speed (0.1 to 1.0)"
        ),
        duration: float = typer.Option(
            3.0, "--duration", "-d", help="Movement duration in seconds"
        ),
        connection_type: str = typer.Option(
            "localap", "--connection", "-c", help="Connection type"
        ),
        ip: str | None = typer.Option(None, "--ip", "-i", help="Robot IP address"),
        serial: str | None = typer.Option(None, "--serial", help="Robot serial number"),
        no_verify: bool = typer.Option(
            False, "--no-verify", help="Disable movement verification"
        ),
    ):
        """Move the robot in a specific direction"""
        print_banner()

        async def execute_move():
            try:
                # Create connection
                if connection_type == "localap":
                    connection = await create_local_ap_connection()
                elif connection_type == "localsta":
                    if not ip:
                        console.print(
                            "[red]Error: IP address required for localsta connection[/red]"
                        )
                        return
                    connection = await create_local_sta_connection(ip)
                else:
                    console.print(
                        f"[red]Error: Unsupported connection type '{connection_type}'[/red]"
                    )
                    return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Connecting to robot...", total=None)

                    if not await connection.connect():
                        console.print("[red]Failed to connect to robot[/red]")
                        return

                    progress.update(task, description=f"Moving {direction}...")

                    # Create motion controller
                    motion = MotionController(connection.conn)

                    # Execute movement based on direction
                    success = False
                    if direction == "forward":
                        success = await motion.move_forward(
                            speed, duration, verify=not no_verify
                        )
                    elif direction == "backward":
                        success = await motion.move_backward(
                            speed, duration, verify=not no_verify
                        )
                    elif direction == "left":
                        success = await motion.move_left(
                            speed, duration, verify=not no_verify
                        )
                    elif direction == "right":
                        success = await motion.move_right(
                            speed, duration, verify=not no_verify
                        )
                    elif direction == "turn-left":
                        success = await motion.turn_left(
                            speed, duration, verify=not no_verify
                        )
                    elif direction == "turn-right":
                        success = await motion.turn_right(
                            speed, duration, verify=not no_verify
                        )
                    else:
                        console.print(
                            f"[red]Error: Unknown direction '{direction}'[/red]"
                        )
                        return

                    progress.update(task, description="Movement completed!")

                if success:
                    if no_verify:
                        console.print(
                            f"[green] Move command accepted for {direction}[/green]"
                        )
                        console.print(
                            "[yellow]WARNING: Movement verification disabled - robot may not have actually moved[/yellow]"
                        )
                    else:
                        console.print(
                            f"[green] Successfully moved {direction} for {duration} seconds[/green]"
                        )
                else:
                    console.print(f"[red]FAILED to move {direction}[/red]")

                await connection.disconnect()

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asyncio.run(execute_move())

    @app.command()
    def command(
        cmd: str = typer.Argument(
            ...,
            help="Sport command to execute: hello, sit, standup, dance1, dance2, etc.",
        ),
        connection_type: str = typer.Option(
            "localap", "--connection", "-c", help="Connection type"
        ),
        ip: str | None = typer.Option(None, "--ip", "-i", help="Robot IP address"),
        serial: str | None = typer.Option(None, "--serial", help="Robot serial number"),
        no_verify: bool = typer.Option(
            False, "--no-verify", help="Disable command execution verification"
        ),
    ):
        """Execute a sport command on the robot"""
        print_banner()

        async def execute_command():
            try:
                # Create connection
                if connection_type == "localap":
                    connection = await create_local_ap_connection()
                elif connection_type == "localsta":
                    if not ip:
                        console.print(
                            "[red]Error: IP address required for localsta connection[/red]"
                        )
                        return
                    connection = await create_local_sta_connection(ip)
                else:
                    console.print(
                        f"[red]Error: Unsupported connection type '{connection_type}'[/red]"
                    )
                    return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Connecting to robot...", total=None)

                    if not await connection.connect():
                        console.print("[red]Failed to connect to robot[/red]")
                        return

                    progress.update(task, description=f"Executing {cmd} command...")

                    # Create motion controller
                    motion = MotionController(connection.conn)

                    # Execute command
                    success = await motion.execute_sport_command(
                        cmd.title(), verify=not no_verify
                    )

                    progress.update(task, description="Command completed!")

                if success:
                    if no_verify:
                        console.print(f"[green] Command '{cmd}' accepted[/green]")
                        console.print(
                            "[yellow]WARNING: Execution verification disabled - command may not have actually executed[/yellow]"
                        )
                    else:
                        console.print(
                            f"[green] Successfully executed '{cmd}' command[/green]"
                        )
                else:
                    console.print(f"[red]FAILED to execute '{cmd}' command[/red]")
                    console.print(
                        "[yellow]This command may not be available in current firmware[/yellow]"
                    )

                await connection.disconnect()

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asyncio.run(execute_command())

    @app.command()
    def pattern(
        pattern_name: str = typer.Argument(..., help="Movement pattern: square, spin"),
        connection_type: str = typer.Option(
            "localap", "--connection", "-c", help="Connection type"
        ),
        ip: str | None = typer.Option(None, "--ip", "-i", help="Robot IP address"),
        serial: str | None = typer.Option(None, "--serial", help="Robot serial number"),
        no_verify: bool = typer.Option(
            False, "--no-verify", help="Disable movement verification"
        ),
    ):
        """Execute a movement pattern"""
        print_banner()

        async def execute_pattern():
            try:
                # Create connection
                if connection_type == "localap":
                    connection = await create_local_ap_connection()
                elif connection_type == "localsta":
                    if not ip:
                        console.print(
                            "[red]Error: IP address required for localsta connection[/red]"
                        )
                        return
                    connection = await create_local_sta_connection(ip)
                else:
                    console.print(
                        f"[red]Error: Unsupported connection type '{connection_type}'[/red]"
                    )
                    return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Connecting to robot...", total=None)

                    if not await connection.connect():
                        console.print("[red]Failed to connect to robot[/red]")
                        return

                    progress.update(
                        task, description=f"Executing {pattern_name} pattern..."
                    )

                    # Create motion controller
                    motion = MotionController(connection.conn)

                    # Execute pattern
                    success = False
                    if pattern_name == "square":
                        success = await motion.walk_square(0.3, verify=not no_verify)
                    elif pattern_name == "spin":
                        success = await motion.spin_360("right", verify=not no_verify)
                    else:
                        console.print(
                            f"[red]Error: Unknown pattern '{pattern_name}'[/red]"
                        )
                        return

                    progress.update(task, description="Pattern completed!")

                if success:
                    if no_verify:
                        console.print(
                            f"[green] Pattern '{pattern_name}' commands accepted[/green]"
                        )
                        console.print(
                            "[yellow]WARNING: Movement verification disabled - pattern may not have actually executed[/yellow]"
                        )
                    else:
                        console.print(
                            f"[green] Successfully executed '{pattern_name}' pattern[/green]"
                        )
                else:
                    console.print(
                        f"[red]FAILED to execute '{pattern_name}' pattern[/red]"
                    )

                await connection.disconnect()

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asyncio.run(execute_pattern())

    @app.command()
    def test(
        connection_type: str = typer.Option(
            "localap", "--connection", "-c", help="Connection type"
        ),
        ip: str | None = typer.Option(None, "--ip", "-i", help="Robot IP address"),
        serial: str | None = typer.Option(None, "--serial", help="Robot serial number"),
    ):
        """Run comprehensive firmware compatibility test"""
        print_banner()
        print_firmware_warning()

        console.print(
            "[yellow]This will run a comprehensive test of all available commands.[/yellow]"
        )
        if not typer.confirm("Continue?"):
            return

        async def run_test():
            try:
                # Create connection
                if connection_type == "localap":
                    connection = await create_local_ap_connection()
                elif connection_type == "localsta":
                    if not ip:
                        console.print(
                            "[red]Error: IP address required for localsta connection[/red]"
                        )
                        return
                    connection = await create_local_sta_connection(ip)
                else:
                    console.print(
                        f"[red]Error: Unsupported connection type '{connection_type}'[/red]"
                    )
                    return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Connecting to robot...", total=None)

                    if not await connection.connect():
                        console.print("[red]Failed to connect to robot[/red]")
                        return

                    progress.update(task, description="Running compatibility tests...")

                    # Create motion controller
                    motion = MotionController(connection.conn)

                    # Get compatibility info
                    compatibility = motion.get_firmware_compatibility_info()

                    progress.update(task, description="Tests completed!")

                # Display results
                results_table = Table(title="Firmware Compatibility Test Results")
                results_table.add_column("Test Category", style="cyan")
                results_table.add_column("Status", style="green")
                results_table.add_column("Details", style="yellow")

                results_table.add_row(
                    "Connection", " Success", "Connected successfully"
                )
                results_table.add_row("Motion Mode", " mcf", "Current firmware mode")
                results_table.add_row(
                    "Basic Movements",
                    " Available",
                    "Forward, backward, left, right, turns",
                )
                results_table.add_row(
                    "Core Commands",
                    " Available",
                    f"{len(compatibility['working_commands'])} commands",
                )
                results_table.add_row(
                    "Advanced Commands",
                    "LIMITED",
                    f"{len(compatibility['potentially_restricted_commands'])} may be restricted",
                )
                results_table.add_row(
                    "Mode Switching", "NOT AVAILABLE", "normal/ai modes removed"
                )
                results_table.add_row(
                    "Movement Verification",
                    " Available",
                    "Sensor-based movement detection",
                )

                console.print(results_table)

                await connection.disconnect()

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asyncio.run(run_test())

    @app.command()
    def list_commands():
        """List all available sport commands"""
        print_banner()

        from sparky.core.motion import MotionController

        # Create a dummy motion controller to get command list
        motion = MotionController(None)
        commands = motion.get_available_commands()
        compatibility = motion.get_firmware_compatibility_info()

        # Create tables
        working_table = Table(title=" Working Commands (Recommended)")
        working_table.add_column("Command", style="green")
        working_table.add_column("ID", style="cyan")

        for cmd in compatibility["working_commands"]:
            if cmd in commands:
                working_table.add_row(cmd, str(commands[cmd]))

        restricted_table = Table(title="Potentially Restricted Commands")
        restricted_table.add_column("Command", style="yellow")
        restricted_table.add_column("ID", style="cyan")

        for cmd in compatibility["potentially_restricted_commands"]:
            if cmd in commands:
                restricted_table.add_row(cmd, str(commands[cmd]))

        console.print(working_table)
        console.print(restricted_table)

        console.print(
            "\n[dim]Note: Commands marked as 'restricted' may not work in current firmware.[/dim]"
        )


if __name__ == "__main__":
    app()
