#!/usr/bin/env python3
"""
Limsy - Lightweight HTTP Rate-Limit Analyzer
A single-file Python tool for analyzing HTTP rate-limiting behavior
Author: URDev
"""

import asyncio
import aiohttp
import sys
import time
from collections import Counter
from typing import Dict, List, Tuple, Optional
import signal
import argparse

# Color codes for terminal output (minimal approach)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BLUE = '\033[94m'

# Signal handler for graceful Ctrl+C
class InterruptHandler:
    def __init__(self):
        self.interrupted = False
        signal.signal(signal.SIGINT, self.handle_interrupt)
    
    def handle_interrupt(self, signum, frame):
        if not self.interrupted:
            self.interrupted = True
            print(f"\n{Colors.YELLOW}[!] Interrupt received. Stopping gracefully...{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}[!] Force stopping...{Colors.RESET}")
            sys.exit(1)

async def make_request(session: aiohttp.ClientSession, url: str, delay: float = 0) -> Tuple[str, str]:
    """
    Make a HEAD request and return status and final URL.
    Uses HEAD to minimize impact while still triggering rate limits.
    """
    if delay > 0:
        await asyncio.sleep(delay)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        async with session.head(
            url,
            headers=headers,
            allow_redirects=True
        ) as resp:
            return str(resp.status), str(resp.url)
    except aiohttp.ClientError as e:
        return f"CLIENT_ERROR_{type(e).__name__}", ""
    except asyncio.TimeoutError:
        return "TIMEOUT", ""
    except Exception as e:
        return f"EXCEPTION_{type(e).__name__}", ""

def print_banner():
    """Display the tool banner"""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║               Limsy - Rate-Limit Analyzer            ║
║          Lightweight HTTP Rate-Limit Detection       ║
║                    By URDev                          ║
╚══════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)
    print(f"{Colors.BLUE}[*] Tool for authorized analysis only{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Use only on systems you own or have permission to test{Colors.RESET}\n")

def get_target_from_user() -> str:
    """Interactively get target URL from user"""
    print(f"{Colors.CYAN}[?] Enter target URL (with or without http/https):{Colors.RESET}")
    
    while True:
        try:
            url_input = input("> ").strip()
            
            if not url_input:
                print(f"{Colors.YELLOW}[!] Please enter a URL{Colors.RESET}")
                continue
            
            # Add scheme if missing
            if not url_input.startswith(('http://', 'https://')):
                # Try HTTPS first, fallback to HTTP
                print(f"{Colors.BLUE}[*] No scheme specified. Trying HTTPS...{Colors.RESET}")
                url_input = 'https://' + url_input
            
            # Basic URL validation
            if not (url_input.startswith('http://') or url_input.startswith('https://')):
                print(f"{Colors.RED}[!] Invalid URL format{Colors.RESET}")
                continue
            
            print(f"{Colors.GREEN}[✓] Target set to: {url_input}{Colors.RESET}")
            return url_input
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[!] Input cancelled{Colors.RESET}")
            sys.exit(0)
        except EOFError:
            print(f"\n{Colors.YELLOW}[!] Input ended{Colors.RESET}")
            sys.exit(0)

async def run_stage(
    session: aiohttp.ClientSession, 
    url: str, 
    rps: int, 
    duration: int,
    expected_path: Optional[str] = None
) -> Dict:
    """
    Run a single stage with specific RPS and duration.
    Returns results dictionary.
    """
    print(f"\n{Colors.BOLD}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}[→] Stage:{Colors.RESET} {Colors.BOLD}{rps} RPS{Colors.RESET} for {duration} seconds")
    
    start_time = time.time()
    tasks = []
    status_codes = Counter()
    request_count = 0
    
    # Calculate interval between requests for precise RPS
    interval = 1.0 / rps if rps > 0 else 1.0
    
    # Schedule requests for the duration
    while time.time() - start_time < duration:
        task = asyncio.create_task(make_request(session, url))
        tasks.append(task)
        request_count += 1
        
        # Sleep for calculated interval to maintain precise RPS
        await asyncio.sleep(interval)
    
    # Gather all results
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process responses
    for resp in responses:
        if isinstance(resp, tuple):
            status, final_url = resp
            
            # Categorize response
            if status == "200" and expected_path and expected_path not in final_url:
                # Redirect away from expected path (silent blocking)
                status_codes["REDIRECT_AWAY"] += 1
            elif status in ["429", "403", "503", "502", "504"]:
                # Explicit error codes
                status_codes[status] += 1
            elif status.startswith(("3", "4", "5")):
                # Other HTTP errors
                status_codes[status] += 1
            elif status.startswith("CLIENT_ERROR_") or status.startswith("EXCEPTION_"):
                # Network/connection errors
                status_codes[status] += 1
            else:
                # Success or other statuses
                status_codes[status] += 1
        else:
            # Unexpected exceptions
            status_codes[f"UNHANDLED_{type(resp).__name__}"] += 1
    
    # Display stage results
    print(f"{Colors.BLUE}[*] Requests sent:{Colors.RESET} {request_count}")
    print(f"{Colors.BLUE}[*] Response distribution:{Colors.RESET}")
    
    # Color code based on status
    for code, count in status_codes.most_common():
        if code == "200":
            color = Colors.GREEN
        elif code in ["429", "403", "503", "REDIRECT_AWAY"]:
            color = Colors.RED
        elif code.startswith(("3", "4", "5")) or code.startswith(("CLIENT_ERROR", "EXCEPTION")):
            color = Colors.YELLOW
        else:
            color = Colors.RESET
        
        percentage = (count / request_count) * 100
        print(f"  {color}{code}: {count} ({percentage:.1f}%){Colors.RESET}")
    
    return {
        'rps': rps,
        'duration': duration,
        'total_requests': request_count,
        'status_codes': dict(status_codes),
        'success_rate': (status_codes.get('200', 0) / request_count * 100) if request_count > 0 else 0
    }

async def analyze_rate_limits(
    url: str,
    stages: List[Tuple[int, int]] = None,
    interactive_mode: bool = False
):
    """
    Main analysis function with progressive RPS stages.
    """
    if stages is None:
        # Default progressive stages
        stages = [
            (1, 5),    # 1 RPS for 5s - Baseline
            (2, 10),   # 2 RPS for 10s - Light load
            (5, 10),   # 5 RPS for 10s - Moderate
            (10, 10),  # 10 RPS for 10s - Aggressive
            (20, 10),  # 20 RPS for 10s - High
            (50, 5),   # 50 RPS for 5s - Very high
        ]
    
    # Extract expected path for redirect detection
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    expected_path = parsed_url.path if parsed_url.path else "/"
    
    # Configure HTTP client
    connector = aiohttp.TCPConnector(limit=0)  # No client-side concurrency limit
    timeout = aiohttp.ClientTimeout(total=10)
    
    results = []
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print(f"{Colors.BLUE}[*] Starting analysis of: {url}{Colors.RESET}")
        print(f"{Colors.BLUE}[*] Using {len(stages)} progressive stages{Colors.RESET}")
        
        if interactive_mode:
            print(f"\n{Colors.YELLOW}[!] Press Ctrl+C at any time to stop{Colors.RESET}")
        
        try:
            for rps, duration in stages:
                # Run stage
                stage_result = await run_stage(session, url, rps, duration, expected_path)
                results.append(stage_result)
                
                # Check for blocking conditions
                status_codes = Counter(stage_result['status_codes'])
                error_codes = ['429', '403', '503', 'REDIRECT_AWAY', '502', '504']
                
                error_count = sum(status_codes[code] for code in error_codes if code in status_codes)
                
                # Stop if more than 50% errors or complete blocking
                if error_count > stage_result['total_requests'] * 0.5:
                    print(f"\n{Colors.RED}[!] BLOCKING DETECTED at {rps} RPS{Colors.RESET}")
                    print(f"{Colors.RED}[!] Error rate: {error_count/stage_result['total_requests']*100:.1f}%{Colors.RESET}")
                    
                    if interactive_mode:
                        print(f"\n{Colors.YELLOW}[?] Continue testing? (y/n):{Colors.RESET}")
                        try:
                            response = input("> ").strip().lower()
                            if response != 'y':
                                break
                        except (KeyboardInterrupt, EOFError):
                            break
                    else:
                        break
                
                # Brief pause between stages
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            print(f"\n{Colors.YELLOW}[!] Analysis cancelled{Colors.RESET}")
            return results
    
    return results

def print_summary(results: List[Dict], url: str):
    """Print comprehensive analysis summary"""
    if not results:
        print(f"{Colors.YELLOW}[!] No results to display{Colors.RESET}")
        return
    
    print(f"\n{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}ANALYSIS SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Target:{Colors.RESET} {url}")
    print(f"{Colors.BLUE}[*] Stages completed:{Colors.RESET} {len(results)}\n")
    
    # Find thresholds
    blocking_stage = None
    warning_stage = None
    
    for result in results:
        status_codes = Counter(result['status_codes'])
        error_codes = ['429', '403', '503', 'REDIRECT_AWAY', '502', '504']
        error_count = sum(status_codes[code] for code in error_codes if code in status_codes)
        
        if error_count > result['total_requests'] * 0.5 and not blocking_stage:
            blocking_stage = result['rps']
        elif error_count > result['total_requests'] * 0.2 and not warning_stage:
            warning_stage = result['rps']
    
    # Print threshold analysis
    print(f"{Colors.BOLD}Threshold Analysis:{Colors.RESET}")
    if warning_stage:
        print(f"  {Colors.YELLOW}⚠ Warning threshold:{Colors.RESET} {warning_stage} RPS")
    if blocking_stage:
        print(f"  {Colors.RED}✗ Blocking threshold:{Colors.RESET} {blocking_stage} RPS")
    
    if not blocking_stage:
        print(f"  {Colors.GREEN}✓ No hard blocking detected up to {results[-1]['rps']} RPS{Colors.RESET}")
    
    # Detailed stage results
    print(f"\n{Colors.BOLD}Stage-by-Stage Results:{Colors.RESET}")
    print(f"{'RPS':>6} {'Duration':>9} {'Requests':>10} {'Success %':>10} {'Block %':>10}")
    print(f"{'─' * 55}")
    
    for result in results:
        status_codes = Counter(result['status_codes'])
        
        # Calculate success and block percentages
        success_pct = (status_codes.get('200', 0) / result['total_requests']) * 100
        error_codes = ['429', '403', '503', 'REDIRECT_AWAY']
        block_pct = sum(status_codes[code] for code in error_codes if code in status_codes) / result['total_requests'] * 100
        
        # Color coding
        if block_pct > 50:
            rps_color = Colors.RED
        elif block_pct > 20:
            rps_color = Colors.YELLOW
        else:
            rps_color = Colors.GREEN
        
        print(f"{rps_color}{result['rps']:>6}{Colors.RESET} "
              f"{result['duration']:>9}s "
              f"{result['total_requests']:>10} "
              f"{success_pct:>9.1f}% "
              f"{block_pct:>9.1f}%")
    
    # Response code summary
    print(f"\n{Colors.BOLD}Response Code Distribution:{Colors.RESET}")
    all_codes = Counter()
    for result in results:
        all_codes.update(result['status_codes'])
    
    for code, count in all_codes.most_common(10):  # Top 10
        if code == "200":
            color = Colors.GREEN
            symbol = "✓"
        elif code in ["429", "403", "503", "REDIRECT_AWAY"]:
            color = Colors.RED
            symbol = "✗"
        elif code.startswith("3"):
            color = Colors.YELLOW
            symbol = "↪"
        else:
            color = Colors.RESET
            symbol = "•"
        
        print(f"  {color}{symbol} {code}:{Colors.RESET} {count}")

def get_custom_stages() -> List[Tuple[int, int]]:
    """Allow user to define custom stages"""
    stages = []
    print(f"\n{Colors.CYAN}[?] Enter custom stages (RPS Duration), or press Enter for defaults:{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Format: '5 10' for 5 RPS for 10 seconds{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Press Enter twice when done{Colors.RESET}")
    
    try:
        while True:
            line = input("Stage > ").strip()
            if not line:
                if stages:
                    break
                else:
                    print(f"{Colors.BLUE}[*] Using default stages{Colors.RESET}")
                    return None
            
            parts = line.split()
            if len(parts) == 2:
                try:
                    rps = int(parts[0])
                    duration = int(parts[1])
                    if rps > 0 and duration > 0:
                        stages.append((rps, duration))
                        print(f"{Colors.GREEN}[+] Added: {rps} RPS for {duration}s{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}[!] Values must be positive{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.YELLOW}[!] Invalid numbers{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[!] Please enter two numbers{Colors.RESET}")
    except (KeyboardInterrupt, EOFError):
        if stages:
            print(f"{Colors.BLUE}[*] Using {len(stages)} custom stages{Colors.RESET}")
            return stages
        else:
            print(f"{Colors.BLUE}[*] Using default stages{Colors.RESET}")
            return None
    
    return stages if stages else None

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Limsy - Lightweight HTTP Rate-Limit Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-u', '--url', help='Target URL to analyze')
    parser.add_argument('-c', '--custom', action='store_true', 
                       help='Use custom rate stages')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Minimal output, no banner')
    
    args = parser.parse_args()
    
    # Setup interrupt handler
    interrupt_handler = InterruptHandler()
    
    # Show banner unless quiet mode
    if not args.quiet:
        print_banner()
    
    # Get target URL
    target_url = args.url
    if not target_url:
        target_url = get_target_from_user()
    
    # Get custom stages if requested
    custom_stages = None
    if args.custom:
        custom_stages = get_custom_stages()
    
    # Run analysis
    try:
        results = await analyze_rate_limits(
            target_url, 
            stages=custom_stages,
            interactive_mode=not args.url  # Interactive only if URL not provided via CLI
        )
        
        # Print summary
        if not interrupt_handler.interrupted:
            print_summary(results, target_url)
        
        print(f"\n{Colors.GREEN}[✓] Analysis complete{Colors.RESET}")
        
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error during analysis: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Analysis interrupted{Colors.RESET}")
        sys.exit(130)
