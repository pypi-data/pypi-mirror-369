import click
from typing import Optional
import random

from llvd import config, __version__
from llvd.app import App
from llvd.process_io import parse_cookie_file, parse_header_file
from llvd.validators import validate_course_and_path, parse_throttle
from llvd.utils import load_proxies, get_random_proxy

BOLD = "\033[1m"
RED_COLOR = "\u001b[31m"

@click.command()
@click.option(
    "--version",
    "-v",
    is_flag=True,
    help="Show version and exit",
)
@click.option(
    "--cookies",
    is_flag=True,
    help="Authenticate with cookies by following the guidelines provided in the documentation",
)
@click.option(
    "--headers",
    is_flag=True,
    help="Change request headers",
)
@click.option(
    "--resolution",
    "-r",
    default="720",
    type=click.Choice(["360", "540", "720", "1080"], case_sensitive=False),
    help="Video resolution (default: 720)",
)
@click.option(
    "--caption",
    "-ca",
    is_flag=True,
    help="Download subtitles",
)
@click.option(
    "--exercise",
    "-e",
    is_flag=True,
    help="Download exercises",
)
@click.option(
    "--course",
    "-c",
    help="Course slug (e.g., 'java-8-essential')",
)
@click.option(
    "--path",
    "-p",
    help="Learning path slug (e.g., 'become-a-php-developer')",
)
@click.option(
    "--throttle",
    "-t",
    help="Min,max wait in seconds between downloads (e.g., '10,30' or '5')",
)
@click.option(
    "--proxy-file",
    "proxy_file",
    default=None,
    help="Path to a file containing a list of proxies (one per line)",
)
@click.pass_context
def main(
    ctx: click.Context,
    version: bool,
    cookies: bool,
    headers: bool,
    resolution: str,
    caption: bool,
    exercise: bool,
    course: Optional[str],
    path: Optional[str],
    throttle: Optional[str],
    proxy_file: Optional[str],
) -> None:
    """
    LinkedIn Learning Video Downloader (LLVD)
    
    Download LinkedIn Learning courses for offline viewing.
    
    Examples:
    
    \b
    $ llvd --course "java-8-essential" --cookies
    $ llvd -p "become-a-php-developer" -t 10,30 --cookies
    """
    if version:
        click.echo(f"LLVD version: {__version__}")
        return

    try:
        # Parse proxy file if provided
        proxies = []
        if proxy_file:
            try:
                with open(proxy_file, 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                click.echo(click.style(f"Loaded {len(proxies)} proxies from {proxy_file}", fg="green"))
            except Exception as e:
                click.echo(click.style(f"Failed to load proxies from {proxy_file}: {str(e)}", fg="red"))
                return

        # Validate and process course/path
        course_slug, is_path = validate_course_and_path(course, path)
        
        # Parse throttle values
        throttle_values = parse_throttle(throttle) if throttle else None
        
        # Validate path requires throttle
        if is_path and not throttle_values:
            raise click.UsageError("Throttle option (-t) is required when using --path")
        
        # Initialize and run the application
        app = App(
            email=config.email,
            password=config.password,
            course_slug=course_slug,
            resolution=resolution,
            caption=caption,
            exercise=exercise,
            throttle=throttle_values,
            proxies=proxies
        )

        if cookies:
            cookie_dict = parse_cookie_file()
            if not all(k in cookie_dict for k in ("li_at", "JSESSIONID")):
                raise click.UsageError("cookies.txt must contain both 'li_at' and 'JSESSIONID' cookies")
                
            click.echo(click.style("Using cookie info from cookies.txt", fg="green"))

            if headers:
                header_dict = parse_header_file()
                app.run(cookie_dict, header_dict)
            else:
                app.run(cookie_dict)
        else:
            if not config.email:
                config.email = click.prompt("Please enter your LinkedIn email address")
            if not config.password:
                config.password = click.prompt("Enter your LinkedIn Password", hide_input=True)

            app.run()

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        ctx.exit(1)
