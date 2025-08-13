import asyncio
import json
import tempfile
import threading
import wave
from datetime import datetime
from pathlib import Path
from subprocess import check_output, run

import click
from groq import Groq

try:
    from bleak import BleakScanner
except ImportError:
    BleakScanner = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

from rich import print as rprint
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

console = Console()

# Config
HOSTS_FILE = Path("hosts")
if HOSTS_FILE.exists():
    HOSTS = HOSTS_FILE.read_text().splitlines()
else:
    HOSTS = []

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16 if pyaudio else None
CHANNELS = 1
RATE = 16000


class AudioRecorder:
    def __init__(self):
        if not pyaudio:
            raise ImportError("pyaudio not installed")
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False

    def start(self):
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        self.recording = True
        self.frames = []

        def record():
            while self.recording:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.frames.append(data)

        self.thread = threading.Thread(target=record)
        self.thread.start()

    def stop(self) -> str:
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wf = wave.open(f.name, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            return f.name

    def __del__(self):
        if hasattr(self, "p"):
            self.p.terminate()


@click.group()
@click.option("--json-output", is_flag=True, help="Output in JSON format")
@click.pass_context
def main(ctx, json_output):
    """🚀 Multi-purpose CLI Tool for Network, BLE & Audio Operations"""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    if not json_output:
        console.print(
            Panel.fit("🛠️  [bold cyan]Multi-Tool CLI[/bold cyan]", border_style="cyan")
        )


async def arun_http(host: str, n: int, c: int, json_mode: bool = False):
    """Run HTTP load test"""
    loop = asyncio.get_running_loop()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=json_mode,
    ) as progress:
        task = progress.add_task(f"[cyan]Load testing {host}...", total=None)

        while True:
            try:
                result = await loop.run_in_executor(
                    None,
                    check_output,
                    ["oha", "-n", f"{n}", "-c", f"{c}", "--json", f"http://{host}"],
                )
                data = json.loads(result)

                if json_mode:
                    print(
                        json.dumps(
                            {
                                "host": host,
                                "status": "success",
                                "rps": data.get("rps", {}).get("mean"),
                                "latency_avg": data.get("latency", {}).get("mean"),
                                "success_rate": data.get(
                                    "status_code_distribution", {}
                                ).get("200", 0)
                                / n
                                * 100,
                            }
                        )
                    )
                else:
                    console.print(
                        f"[green]✓[/green] {host} | RPS: {data.get('rps', {}).get('mean', 0):.2f} | Latency: {data.get('latency', {}).get('mean', 0):.2f}ms"
                    )

            except Exception as e:
                if json_mode:
                    print(
                        json.dumps({"host": host, "status": "error", "error": str(e)})
                    )
                else:
                    console.print(f"[red]✗[/red] {host} -> {e}")

            await asyncio.sleep(5)


@main.command()
@click.argument("host")
@click.option("-n", "--requests", default=10000, help="Number of requests")
@click.option("-c", "--concurrency", default=100, help="Concurrent connections")
@click.pass_context
def http(ctx: click.Context, host: str, requests: int, concurrency: int):
    """⚡ HTTP Load Testing with oha"""
    if not ctx.obj.get("json"):
        console.print(f"[bold]Starting load test:[/bold] {host}")
        console.print(f"  • Requests: {requests:,}")
        console.print(f"  • Concurrency: {concurrency}")

    asyncio.run(arun_http(host, requests, concurrency, ctx.obj.get("json", False)))


async def scan_ble_devices(json_mode: bool = False):
    """Scan BLE devices"""
    if not BleakScanner:
        console.print(
            "[red]BleakScanner not installed. Install with: pip install bleak[/red]"
        )
        return

    while True:
        devices = await BleakScanner.discover()

        if json_mode:
            for d in devices:
                print(
                    json.dumps(
                        {
                            "type": "ble",
                            "address": d.address,
                            "name": d.name,
                            "rssi": getattr(d, "rssi", None),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )
        else:
            table = Table(title="🔵 BLE Devices", border_style="blue")
            table.add_column("Address", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("RSSI", style="yellow")

            for device in devices:
                table.add_row(
                    device.address,
                    device.name or "[unnamed]",
                    f"{getattr(device, 'rssi', 'N/A')} dBm",
                )

            console.clear()
            console.print(table)
            console.print(
                f"\n[dim]Found {len(devices)} devices. Scanning again in 5s...[/dim]"
            )

        await asyncio.sleep(5)


@main.command()
@click.pass_context
def ble(ctx):
    """📡 Scan for Bluetooth LE devices"""
    asyncio.run(scan_ble_devices(ctx.obj.get("json", False)))


@main.command()
@click.argument("target")
@click.option(
    "-p", "--ports", default="1-1000", help="Port range (e.g., 80,443 or 1-1000)"
)
@click.option("-t", "--timeout", default=1, help="Timeout in seconds")
@click.option("--tcp", is_flag=True, default=True, help="TCP scan (default)")
@click.option("--udp", is_flag=True, help="UDP scan")
@click.option("--syn", is_flag=True, help="SYN scan (requires root)")
@click.pass_context
def nmap(
    ctx: click.Context,
    target: str,
    ports: str,
    timeout: int,
    tcp: bool,
    udp: bool,
    syn: bool,
):
    """🔍 Network port scanning"""
    json_mode = ctx.obj.get("json", False)

    cmd = ["nmap", "-oX", "-", f"-p{ports}"]

    if syn:
        cmd.append("-sS")
    elif udp:
        cmd.append("-sU")
    else:
        cmd.append("-sT")

    cmd.extend([f"--host-timeout={timeout}s", target])

    if not json_mode:
        console.print(f"[bold]Scanning:[/bold] {target}")
        console.print(f"  • Ports: {ports}")
        console.print(f"  • Type: {'SYN' if syn else 'UDP' if udp else 'TCP'}")

    with (
        console.status("[cyan]Scanning ports...[/cyan]", spinner="dots")
        if not json_mode
        else nullcontext()
    ):
        try:
            result = run(cmd, capture_output=True, text=True)

            # Parse results
            open_ports = []
            for line in result.stdout.splitlines():
                if "open" in line and "/tcp" in line or "/udp" in line:
                    parts = line.split()
                    if parts:
                        port_info = parts[0].split("/")
                        open_ports.append(
                            {
                                "port": int(port_info[0]),
                                "protocol": port_info[1],
                                "state": "open",
                                "service": parts[2] if len(parts) > 2 else "unknown",
                            }
                        )

            if json_mode:
                print(
                    json.dumps(
                        {
                            "target": target,
                            "scan_type": "syn" if syn else "udp" if udp else "tcp",
                            "open_ports": open_ports,
                            "total_open": len(open_ports),
                        }
                    )
                )
            else:
                if open_ports:
                    table = Table(
                        title=f"🎯 Open Ports on {target}", border_style="green"
                    )
                    table.add_column("Port", style="cyan")
                    table.add_column("Protocol", style="yellow")
                    table.add_column("Service", style="green")

                    for port in open_ports:
                        table.add_row(
                            str(port["port"]), port["protocol"].upper(), port["service"]
                        )

                    console.print(table)
                else:
                    console.print(f"[yellow]No open ports found on {target}[/yellow]")

        except Exception as e:
            if json_mode:
                print(json.dumps({"error": str(e)}))
            else:
                console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.option("--live", is_flag=True, help="Live recording (press Enter to stop)")
@click.pass_context
def transcribe(ctx: click.Context, live: bool):
    """🎤 Record audio and transcribe with Whisper"""
    recorder = AudioRecorder()

    if live:
        console.print("[green]🔴 Recording... Press Enter to stop[/green]")
        recorder.start()
        input()
        audio_file = recorder.stop()
        console.print("[yellow]Recording stopped[/yellow]")
    else:
        with Progress() as progress:
            task = progress.add_task(
                f"[cyan]Recording for {duration}s...", total=duration
            )
            recorder.start()
            for i in range(duration):
                asyncio.run(asyncio.sleep(1))
                progress.update(task, advance=1)
            audio_file = recorder.stop()

    # Transcribe
    with (
        console.status("[cyan]Transcribing...[/cyan]")
        if not json_mode
        else nullcontext()
    ):
        result = Groq().audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            audio=audio_file,
            response_format="verbose_json",
        )
        print(
            json.dumps(
                {
                    "text": result.text,
                    "language": result.language,
                    "segments": result.segments,
                }
            )
        )
        console.print(
            Panel(result.text, title="📝 Transcription", border_style="green")
        )

        if result.segments:
            console.print(f"\n[dim]Detected language: {result.language}[/dim]")
    Path(audio_file).unlink()


@main.command()
@click.pass_context
def batch(ctx: click.Context):
    """🔄 Run batch operations from hosts file"""
    if not HOSTS:
        console.print(
            "[red]No hosts file found. Create a 'hosts' file with one host per line.[/red]"
        )
        return

    async def run_all():
        tasks = []
        for host in HOSTS:
            tasks.append(arun_http(host, 1000, 10, ctx.obj.get("json", False)))
        await asyncio.gather(*tasks)

    if not ctx.obj.get("json"):
        console.print(f"[bold]Running batch tests for {len(HOSTS)} hosts[/bold]")

    asyncio.run(run_all())


# Helper context manager
from contextlib import nullcontext

if __name__ == "__main__":
    main()
