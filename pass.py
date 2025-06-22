# Password Strength Analyzer and Custom Wordlist Generator

import argparse
import itertools
import re
import datetime
from zxcvbn import zxcvbn
import nltk
from nltk.corpus import words
import getpass

 try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

# Leetspeak substitution dictionary
LEETSPEAK = {
    'a': ['4', '@'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['5', '$'],
    't': ['7']
}

# Text file for storing analyzed passwords
PASSWORD_LOG_FILE = "passwords_analyzed.txt"

# Initialize or append to password log file
def save_to_text_file(password, score):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | Password: {password} | Strength Score: {score}/4\n"
    with open(PASSWORD_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Password Strength Analyzer and Wordlist Generator")
    parser.add_argument('--password', help="Password to analyze")
    parser.add_argument('--name', help="User's name for wordlist")
    parser.add_argument('--date', help="Significant date (e.g., YYYYMMDD)")
    parser.add_argument('--pet', help="Pet's name for wordlist")
    parser.add_argument('--output', default="wordlist.txt", help="Output wordlist file (default: wordlist.txt)")
    return parser.parse_args()

# Analyze password strength using zxcvbn
def analyze_password(password):
    result = zxcvbn(password)
    score = result['score']  # 0 (weak) to 4 (strong)
    crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
    suggestions = result['feedback']['suggestions']
    warnings = result['feedback']['warning']
    
    # Save to text file
    save_to_text_file(password, score)
    
    print("\nPassword Strength Analysis:")
    print(f"Password: {password}")
    print(f"Strength Score: {score}/4")
    print(f"Estimated Crack Time: {crack_time}")
    print(f"Password saved to {PASSWORD_LOG_FILE}")
    if warnings:
        print(f"Warning: {warnings}")
    for suggestion in suggestions:
        print(f"Suggestion: {suggestion}")

# Generate leetspeak variations
def generate_leetspeak(word):
    variations = [word]
    for char, subs in LEETSPEAK.items():
        if char in word.lower():
            new_variations = []
            for var in variations:
                for sub in subs:
                    new_variations.append(var.replace(char, sub).replace(char.upper(), sub))
                new_variations.append(var)
            variations = new_variations
    return list(set(variations))

# Generate wordlist based on user inputs
def generate_wordlist(name, date, pet, output_file):
    wordlist = set()
    base_words = []
    
    # Add user inputs
    if name:
        base_words.extend([name, name.lower(), name.upper(), name.capitalize()])
    if pet:
        base_words.extend([pet, pet.lower(), pet.upper(), pet.capitalize()])
    if date:
        # Extract year, month, day
        date = date.replace('-', '').replace('/', '')
        if len(date) >= 4:
            year = date[-4:]
            base_words.extend([year, date])
    
    # Add common words from NLTK
    common_words = words.words()[:1000]  # Limit to 1000 common words
    base_words.extend(common_words)
    
    # Generate variations
    for word in base_words:
        wordlist.add(word)
        # Case variations
        wordlist.add(word.lower())
        wordlist.add(word.upper())
        wordlist.add(word.capitalize())
        # Leetspeak variations
        wordlist.update(generate_leetspeak(word))
        # Append years (last 50 years)
        current_year = datetime.datetime.now().year
        for year in range(current_year - 50, current_year + 1):
            wordlist.add(word + str(year))
            wordlist.add(word.lower() + str(year))
            wordlist.add(word.upper() + str(year))
            wordlist.add(word.capitalize() + str(year))
        # Common patterns
        wordlist.add(word + "123")
        wordlist.add(word + "!")
    
    # Export wordlist
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(wordlist):
            f.write(word + '\n')
    print(f"\nWordlist generated and saved to {output_file} ({len(wordlist)} entries)")

def main():
    print("Password Strength Analyzer and Wordlist Generator")
    print("FOR EDUCATIONAL PURPOSES ONLY")
    
    args = parse_arguments()
    
    # Analyze password (command-line or interactive)
    password = args.password
    if not password:
        password = getpass.getpass("Enter password to analyze (input is hidden): ")
    if password:
        analyze_password(password)
    
    # Generate wordlist if inputs provided
    if args.name or args.date or args.pet:
        generate_wordlist(args.name, args.date, args.pet, args.output)
    else:
        print("No inputs provided for wordlist generation. Use --name, --date, or --pet to generate a wordlist.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program terminated by user.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
