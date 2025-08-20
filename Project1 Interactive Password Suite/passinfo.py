# main_interactive_v4.py
import hashlib
import requests
import yaml
import time
import random
from zxcvbn import zxcvbn
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import track

# --- Setup ---
console = Console()

# --- Banner ---
BANNER = """
██████╗ █████╗ ███████╗███████╗██╗    ██████╗ ██████╗ ██████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██║    ██╔══██╗██╔══██╗██╔══██╗
██████╔╝███████║███████╗███████╗██║    ██║  ██║██████╔╝██████╔╝
██╔═══╝ ██╔══██║╚════██║╚════██║██║    ██║  ██║██╔══██╗██╔══██╗
██║     ██║  ██║███████║███████║███████╗██████╔╝██║  ██║██████╔╝
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═════╝
    [bold]Interactive Password Suite v4.0[/bold]
"""

# --- Core Functions ---

def get_context_interactively():
    """
    Asks the user for personal keywords to use in analysis or generation.
    Returns a list of keywords.
    """
    keywords = []
    console.print("\n[cyan]First, let's gather some memorable words or numbers.[/cyan]")
    console.print("[cyan]Provide any relevant info (press Enter to skip a field):[/cyan]")
    
    name = Prompt.ask("  > A name or nickname?")
    pet = Prompt.ask("  > A pet's name?")
    city = Prompt.ask("  > A city or street?")
    birth_year = Prompt.ask("  > A birth year (e.g., 1998)?")
    company = Prompt.ask("  > A company name?")
    other = Prompt.ask("  > Any other keywords (comma-separated)?")

    for item in [name, pet, city, birth_year, company]:
        if item:
            keywords.append(item.strip())
    if other:
        keywords.extend([k.strip() for k in other.split(',')])
        
    return list(filter(None, keywords))

def check_hibp(password):
    """Checks password against HIBP Pwned Passwords API using k-Anonymity."""
    try:
        sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_password[:5], sha1_password[5:]
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if response.status_code != 200:
            return False, f"API Error (Status: {response.status_code})"
        
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return True, int(count)
        return False, 0
    except requests.RequestException as e:
        return False, f"Network Error: {e}"

def analyze_password():
    """
    Interactive function to guide the user through a technical password analysis.
    """
    console.print("\n[cyan]--- Password Strength Analyzer ---[/cyan]")
    password = Prompt.ask("[yellow]Enter the password to analyze[/yellow]")
    
    results = zxcvbn(password)
    score = results['score']

    with console.status("[bold green]Checking against data breaches...[/bold green]"):
        is_pwned, pwn_count = check_hibp(password)

    if is_pwned:
        score = 0

    table = Table(title=f"Analysis Results", style="bold blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Result", style="white")

    strength_text = {0: "[bold red]Very Weak", 1: "[red]Weak", 2: "[yellow]Fair", 3: "[green]Good", 4: "[bold green]Excellent"}
    table.add_row("Strength Score", f"{score}/4 {strength_text.get(score, 'N/A')}")
    table.add_row("Est. Crack Time", results['crack_times_display']['offline_slow_hashing_1e4_per_second'])
    
    if isinstance(pwn_count, int):
        hibp_result = f"[bold red]FAIL - Found in {pwn_count:,} breaches!" if is_pwned else "[green]PASS - Not found"
    else:
        hibp_result = f"[yellow]WARN - {pwn_count}"
        
    table.add_row("Data Breach Check", hibp_result)
    console.print(table)

def generate_wordlist():
    """
    Interactive function to guide the user through wordlist generation for security testing.
    """
    console.print("\n[cyan]--- Custom Wordlist Generator ---[/cyan]")
    base_words = get_context_interactively()
    
    if not base_words:
        console.print("[red]No keywords provided. Aborting wordlist generation.[/red]")
        return
        
    output_file = Prompt.ask("[yellow]Enter the desired output filename[/yellow]", default="custom_wordlist.txt")

    mutations = set(base_words)
    
    for word in list(mutations):
        mutations.add(word.capitalize())
        mutations.add(word.upper())

    leet_map = {'a': '@', 'o': '0', 'e': '3', 'i': '1', 's': '$', 't': '7'}
    for word in list(mutations):
        leet_word = "".join(leet_map.get(char.lower(), char) for char in word)
        mutations.add(leet_word)

    current_mutations = list(mutations)
    for word in track(current_mutations, description="[green]Generating mutations...[/green]"):
        for year in range(2015, 2026):
            mutations.add(f"{word}{year}")
        for symbol in ['!', '@', '#', '$', '%']:
            mutations.add(f"{word}{symbol}")
            mutations.add(f"{word}{symbol}{symbol}")

    final_list = sorted(list(mutations))
    with open(output_file, 'w') as f:
        for item in final_list:
            f.write(f"{item}\n")
            
    console.print(f"\n[bold green]Success![/bold green] Generated [cyan]{len(final_list)}[/cyan] unique passwords and saved to [magenta]'{output_file}'[/magenta].")

def generate_strong_password():
    """
    Generates strong, memorable, and breach-checked password suggestions.
    """
    console.print("\n[cyan]--- Strong Password Generator ---[/cyan]")
    user_words = get_context_interactively()
    if not user_words:
        console.print("[red]No keywords provided. Cannot generate passwords.[/red]")
        return

    safe_passwords = []
    connector_words = ["Blue", "Cosmic", "Quiet", "Jumping", "Silent", "River", "Stone", "Moon", "Sun", "Star"]
    
    with console.status("[bold green]Generating and checking password candidates...[/bold green]"):
        attempts = 0
        while len(safe_passwords) < 3 and attempts < 50:
            random.shuffle(user_words)
            random.shuffle(connector_words)
            
            base1 = user_words[0].capitalize()
            base2 = connector_words[0]
            num = str(random.randint(10, 999))
            sym = random.choice(['!', '#', '$', '%', '&'])
            
            patterns = [f"{base1}{base2}{num}{sym}", f"{base2}{base1}{sym}{num}", f"{base1}{sym}{base2}{num}"]
            candidate = random.choice(patterns)

            is_pwned, _ = check_hibp(candidate)
            if not is_pwned and candidate not in safe_passwords:
                safe_passwords.append(candidate)
            
            attempts += 1

    if not safe_passwords:
        console.print("[bold red]Could not generate safe passwords with the given keywords. Please try different ones.[/bold red]")
        return

    table = Table(title="Safe & Strong Password Suggestions", style="bold green")
    table.add_column("Suggestion", style="white", no_wrap=True)
    table.add_column("Strength Score", style="cyan")

    for pwd in safe_passwords:
        score = zxcvbn(pwd)['score']
        strength_text = {3: "[green]Good", 4: "[bold green]Excellent"}.get(score, "[yellow]Fair")
        table.add_row(pwd, f"{score}/4 {strength_text}")
        
    console.print(table)
    console.print("[italic]These passwords were not found in any known data breaches.[/italic]")

def show_password_guide():
    """
    Displays a concise guide to password security.
    """
    console.print("\n")
    guide_text = """
[bold]1. Length is King [/bold]
Longer passwords are exponentially harder to crack. Aim for at least [cyan]16 characters[/cyan]. A short, complex password is weaker than a long, simple one.

[bold]2. Use a Mix [/bold]
Include [cyan]UPPERCASE[/cyan], [cyan]lowercase[/cyan], [cyan]numbers (0-9)[/cyan], and [cyan]symbols (!@#$)[/cyan]. This makes brute-force attacks much harder.

[bold]3. Avoid the Obvious  বযকতগত[/bold]
Never use personal info like your name, birthday, pet's name, or family names. This is the first thing attackers will try.

[bold]4. Create a Passphrase [/bold]
Combine 4-5 random, unrelated words. It's long, easy to remember, and very secure.
[green]Example:[/green] [italic]CorrectHorseBatteryStaple[/italic]

[bold]5. Uniqueness is Key [/bold]
Use a [bold red]DIFFERENT[/bold red] password for every important account (email, banking, social media). If one site is breached, your other accounts remain safe.

[bold]6. Check for Breaches [/bold]
Use a tool (like this one!) to see if your password has been exposed in a known data breach. If it has, [bold]stop using it immediately.[/bold]
    """
    console.print(Panel(guide_text, title="[bold yellow]Password Security Guide[/bold yellow]", border_style="blue"))


def main_menu():
    """
    Displays the main menu and handles user choices.
    """
    while True:
        console.clear()
        console.print(f"[cyan]{BANNER}[/cyan]")
        console.print("\n[bold]Choose an option:[/bold]")
        console.print("  [cyan]1[/cyan] - Analyze a Password")
        console.print("  [cyan]2[/cyan] - Generate a Custom Wordlist (for testing)")
        console.print("  [cyan]3[/cyan] - Generate a Strong, Memorable Password")
        console.print("  [cyan]4[/cyan] - View Password Security Guide")
        console.print("  [cyan]5[/cyan] - Exit")

        choice = Prompt.ask("\n[yellow]Enter your choice[/yellow]", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == '1':
            analyze_password()
        elif choice == '2':
            generate_wordlist()
        elif choice == '3':
            generate_strong_password()
        elif choice == '4':
            show_password_guide()
        elif choice == '5':
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break
        
        if Confirm.ask("\n[yellow]Return to the main menu?[/yellow]"):
            continue
        else:
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break

# --- Main execution block ---
if __name__ == "__main__":
    main_menu()
                   
