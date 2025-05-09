import re
import itertools

# =====================================================
#   Leet-speak helper functions
# =====================================================

def generate_leet_variants(word):
    """
    Given a word, generate all possible leet-speak variants
    by substituting certain letters with common symbols.
    """
    leet_mapping = {
        'a': ['a', '@'],
        'e': ['e', '3'],
        'i': ['i', '1'],
        'o': ['o', '0'],
        's': ['s', '$', '5'],
        't': ['t', '7']
    }
    char_options = []
    for ch in word:
        options = leet_mapping.get(ch.lower(), [ch])
        if ch.isupper():
            options = [opt.upper() for opt in options]
        char_options.append(options)
    variants = ["".join(candidate) for candidate in itertools.product(*char_options)]
    return variants

def apply_case_pattern(case_pattern, replacement):
    """
    Adjusts the case of replacement to match the provided case pattern.
    Format can be:
    - u:A - all uppercase
    - u:N - all lowercase (no uppercase)
    - u:1,4,L - uppercase at positions 1, 4, and the last character
    """
    if not case_pattern.startswith("u:"):
        return replacement  # Invalid pattern
    
    pattern = case_pattern[2:]  # Remove the "u:" prefix
    
    # All uppercase
    if pattern == "A":
        return replacement.upper()
    
    # All lowercase
    if pattern == "N":
        return replacement.lower()
    
    # Mixed case with specific positions
    result = list(replacement.lower())
    
    # Apply uppercase at specified positions
    positions = pattern.split(",")
    for pos in positions:
        if pos == "L":  # Last character
            if result:  # Ensure there's at least one character
                result[-1] = result[-1].upper()
        else:
            try:
                # Convert to 0-indexed
                idx = int(pos) - 1
                if 0 <= idx < len(result):
                    result[idx] = result[idx].upper()
            except ValueError:
                pass  # Skip invalid positions
    
    return ''.join(result)

# =====================================================
#   Date helper functions
# =====================================================

def parse_date(date_str):
    """
    Parse a date string of the form 'day/month/year' into
    [day, month, full_year, short_year].
    """
    if not date_str or not isinstance(date_str, str):
        return None, None, None, None
    
    parts = date_str.split("/")
    if len(parts) != 3:
        return None, None, None, None
    
    day, month, full_year = parts
    short_year = full_year[-2:]
    return day, month, full_year, short_year

def generate_numbers_from_date(date_str):
    """
    Given a date string in the format "D/M/YYYY" (e.g., "19/7/2003"),
    returns a list of numbers (as strings) derived from the date.
    """
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return []
        day, month, year = parts
        day_str = str(int(day))
        month_str = str(int(month))
        year_str = year.strip()
        last_two_year = year_str[-2:]
        return [
            year_str,
            last_two_year,
            day_str + month_str,
            day_str + month_str + year_str,
            day_str + month_str + last_two_year,
            month_str + day_str,
            month_str + day_str + year_str,
            month_str + day_str + last_two_year,
            year_str + month_str + day_str,
            last_two_year + month_str + day_str,
            year_str + day_str + month_str,
            last_two_year + day_str + month_str,
        ]
    except Exception:
        return []

# =====================================================
#   Rule Parsing Functions
# =====================================================

def parse_rule(rule_str):
    """
    Parse a rule string into a list of token rules.
    Handles all rule formats from both generators.
    """
    tokens = rule_str.split(" + ")
    rule = []
    
    for token in tokens:
        # Basic string and leet-speak patterns
        if token.startswith("string:") or token.startswith("string_leet:"):
            token_parts = token.split(":", 1)
            token_type = token_parts[0]
            
            # Extract the case pattern if it exists
            if len(token_parts) > 1 and token_parts[1].startswith("u:"):
                case_pattern = token_parts[1]
            else:
                case_pattern = "u:N"  # Default to all lowercase
                
            rule.append({
                "type": token_type, 
                "case_pattern": case_pattern,
                "index": 1  # Default to first string
            })
            
        # Numbered strings with case patterns
        elif token.startswith("string") and ":u:" in token:
            # Extract the string number if any (string, string2, string3, etc.)
            match = re.match(r'string(\d*):u:', token)
            if match:
                string_idx = int(match.group(1)) if match.group(1) else 1
                case_pattern = "u:" + token.split(":u:")[1]
                rule.append({
                    "type": "string", 
                    "case_pattern": case_pattern, 
                    "index": string_idx
                })
            else:
                # Fallback for basic string
                parts = token.split(":", 2)
                rule.append({
                    "type": "string", 
                    "case_pattern": "u:" + parts[2], 
                    "index": 1
                })
                
        # Character rules
        elif token.startswith("character") and ":u:" in token:
            # Extract the character number if any (character, character2, character3, etc.)
            match = re.match(r'character(\d*):u:', token)
            if match:
                char_idx = int(match.group(1)) if match.group(1) else 1
                case_pattern = "u:" + token.split(":u:")[1]
                rule.append({
                    "type": "character", 
                    "case_pattern": case_pattern, 
                    "index": char_idx
                })
            else:
                # Fallback for basic character
                parts = token.split(":", 2)
                rule.append({
                    "type": "character", 
                    "case_pattern": "u:" + parts[2], 
                    "index": 1
                })
        
        # Date component rules
        elif token == "day":
            rule.append({"type": "day"})
        elif token == "month":
            rule.append({"type": "month"})
        elif token == "year":
            rule.append({"type": "year"})
        elif token == "short_year":
            rule.append({"type": "short_year"})
        elif token == "full_date":
            rule.append({"type": "full_date"})
            
        # Number and symbol rules
        elif token == "symbol":
            rule.append({"type": "symbol"})
        elif token == "common_number":
            rule.append({"type": "common_number"})
        elif token == "number":
            rule.append({"type": "number"})
            
        # Literal values
        elif token.startswith("literal:"):
            value = token.split(":", 1)[1]
            rule.append({"type": "literal", "value": value})
        else:
            # Unknown token type, treat as literal
            rule.append({"type": "literal", "value": token})
    
    return rule

# =====================================================
#   Password Generation Functions
# =====================================================

def generate_passwords_from_rule(rule, strings, numbers, date_info_list, symbols=None, 
                                common_numbers=None, has_spaces=False):
    """
    Generate all possible passwords from a rule using all available inputs.
    
    Parameters:
    - rule: List of token rules
    - strings: List of strings (personal info)
    - numbers: List of numbers
    - date_info_list: List of dictionaries, each with 'components' and 'numbers' lists
    - symbols: List of symbols 
    - common_numbers: List of common number sequences
    - has_spaces: Whether to join tokens with spaces
    """
    # Initialize default values
    if symbols is None:
        symbols = []
    if common_numbers is None:
        common_numbers = []
    
    # Filter out None values from strings
    valid_strings = [s for s in strings if s]
    
    # Identify date components in the rule
    date_components_in_rule = []
    for token_rule in rule:
        if token_rule["type"] in ["day", "month", "year", "short_year", "full_date"]:
            date_components_in_rule.append(token_rule["type"])
    
    # If there are date components in the rule, we need special handling
    has_date_components = len(date_components_in_rule) > 0
    
    # Function to join tokens
    def join_tokens(tokens):
        return " ".join(tokens) if has_spaces else "".join(tokens)
    
    all_passwords = set()
    
    # If the rule has date components, process each date separately
    if has_date_components:
        for date_info in date_info_list:
            date_components = date_info.get('components', (None, None, None, None))
            date_numbers = date_info.get('numbers', [])
            day, month, year, short_year = date_components
            
            # Generate base tokens (without replacements)
            base_tokens = []
            for token_rule in rule:
                if token_rule["type"] == "literal":
                    base_tokens.append(token_rule["value"])
                else:
                    # Placeholder for replacements
                    base_tokens.append(None)
            
            # Process password configurations
            # Initialize with a single starting configuration with no used strings
            configs = [(base_tokens.copy(), set())]  # (token_list, used_strings)
            
            # Process each token rule
            for i, token_rule in enumerate(rule):
                new_configs = []
                token_type = token_rule["type"]
                
                for config, used_strings in configs:
                    # String and string_leet rules
                    if token_type in ["string", "string_leet"]:
                        # Get the string index
                        string_idx = token_rule.get("index", 1) - 1  # Convert to 0-indexed
                        
                        # Get available strings (those not used yet if enforcing uniqueness)
                        available_strings = []
                        for s in valid_strings:
                            if s.lower() not in used_strings:
                                available_strings.append(s)
                        
                        # If no available strings, try to use at least one string
                        if not available_strings and valid_strings:
                            available_strings = [valid_strings[0]]
                        
                        # Handle string replacements
                        for string in available_strings:
                            new_config = config.copy()
                            new_used_strings = used_strings.copy()
                            
                            # Apply case pattern
                            adjusted_string = apply_case_pattern(token_rule["case_pattern"], string)
                            
                            # For leet-speak, generate variants
                            if token_type == "string_leet":
                                variants = generate_leet_variants(adjusted_string)
                                for variant in variants:
                                    variant_config = new_config.copy()
                                    variant_config[i] = variant
                                    # Mark this string as used (case insensitive)
                                    variant_used_strings = new_used_strings.copy()
                                    variant_used_strings.add(string.lower())
                                    new_configs.append((variant_config, variant_used_strings))
                            else:
                                new_config[i] = adjusted_string
                                # Mark this string as used (case insensitive)
                                new_used_strings.add(string.lower())
                                new_configs.append((new_config, new_used_strings))
                    
                    # Character rules (first letter of strings)
                    elif token_type == "character":
                        # Get the character index
                        char_idx = token_rule.get("index", 1) - 1  # Convert to 0-indexed
                        
                        # Get available strings (those not used yet)
                        available_strings = []
                        for s in valid_strings:
                            if s.lower() not in used_strings:
                                available_strings.append(s)
                        
                        # If no available strings, try to use at least one string
                        if not available_strings and valid_strings:
                            available_strings = [valid_strings[0]]
                        
                        # Handle character replacements
                        for string in available_strings:
                            if string and len(string) > 0:
                                new_config = config.copy()
                                new_used_strings = used_strings.copy()
                                
                                # Apply case pattern to first character
                                new_config[i] = apply_case_pattern(token_rule["case_pattern"], string[0])
                                
                                # Mark this string as used (case insensitive)
                                new_used_strings.add(string.lower())
                                
                                new_configs.append((new_config, new_used_strings))
                    
                    # Date component rules - now using only components from the current date
                    elif token_type == "day":
                        if day:
                            new_config = config.copy()
                            new_config[i] = day
                            new_configs.append((new_config, used_strings))
                    
                    elif token_type == "month":
                        if month:
                            new_config = config.copy()
                            new_config[i] = month
                            new_configs.append((new_config, used_strings))
                    
                    elif token_type == "year":
                        if year:
                            new_config = config.copy()
                            new_config[i] = year
                            new_configs.append((new_config, used_strings))
                    
                    elif token_type == "short_year":
                        if short_year:
                            new_config = config.copy()
                            new_config[i] = short_year
                            new_configs.append((new_config, used_strings))
                    
                    elif token_type == "full_date":
                        for date_num in date_numbers:
                            new_config = config.copy()
                            new_config[i] = date_num
                            new_configs.append((new_config, used_strings))
                    
                    # Symbol rule
                    elif token_type == "symbol":
                        for symbol in symbols:
                            new_config = config.copy()
                            new_config[i] = symbol
                            new_configs.append((new_config, used_strings))
                    
                    # Number rules
                    elif token_type == "common_number":
                        for num in common_numbers:
                            new_config = config.copy()
                            new_config[i] = num
                            new_configs.append((new_config, used_strings))
                    
                    elif token_type == "number":
                        for num in numbers:
                            new_config = config.copy()
                            new_config[i] = num
                            new_configs.append((new_config, used_strings))
                    
                    # Literal rule (already handled in base_tokens)
                    elif token_type == "literal":
                        new_configs.append((config, used_strings))
                    
                    # If no rule matched or no replacements were made, keep the original config
                    if not new_configs and token_type != "literal":
                        new_configs.append((config, used_strings))
                
                # Update configurations for next iteration
                configs = new_configs
            
            # Fill in any remaining None values and join tokens
            for config, _ in configs:
                filled_tokens = [t if t is not None else "" for t in config]
                password = join_tokens(filled_tokens)
                if password:  # Only add non-empty passwords
                    all_passwords.add(password)
    
    else:
        # If there are no date components in the rule, we can process normally
        # Generate base tokens (without replacements)
        base_tokens = []
        for token_rule in rule:
            if token_rule["type"] == "literal":
                base_tokens.append(token_rule["value"])
            else:
                # Placeholder for replacements
                base_tokens.append(None)
        
        # Process password configurations
        # Initialize with a single starting configuration with no used strings
        configs = [(base_tokens.copy(), set())]  # (token_list, used_strings)
        
        # Process each token rule
        for i, token_rule in enumerate(rule):
            new_configs = []
            token_type = token_rule["type"]
            
            for config, used_strings in configs:
                # String and string_leet rules
                if token_type in ["string", "string_leet"]:
                    # Get available strings (those not used yet if enforcing uniqueness)
                    available_strings = []
                    for s in valid_strings:
                        if s.lower() not in used_strings:
                            available_strings.append(s)
                    
                    # If no available strings, try to use at least one string
                    if not available_strings and valid_strings:
                        available_strings = [valid_strings[0]]
                    
                    # Handle string replacements
                    for string in available_strings:
                        new_config = config.copy()
                        new_used_strings = used_strings.copy()
                        
                        # Apply case pattern
                        adjusted_string = apply_case_pattern(token_rule["case_pattern"], string)
                        
                        # For leet-speak, generate variants
                        if token_type == "string_leet":
                            variants = generate_leet_variants(adjusted_string)
                            for variant in variants:
                                variant_config = new_config.copy()
                                variant_config[i] = variant
                                # Mark this string as used (case insensitive)
                                variant_used_strings = new_used_strings.copy()
                                variant_used_strings.add(string.lower())
                                new_configs.append((variant_config, variant_used_strings))
                        else:
                            new_config[i] = adjusted_string
                            # Mark this string as used (case insensitive)
                            new_used_strings.add(string.lower())
                            new_configs.append((new_config, new_used_strings))
                
                # Character rules (first letter of strings)
                elif token_type == "character":
                    # Get available strings (those not used yet)
                    available_strings = []
                    for s in valid_strings:
                        if s.lower() not in used_strings:
                            available_strings.append(s)
                    
                    # If no available strings, try to use at least one string
                    if not available_strings and valid_strings:
                        available_strings = [valid_strings[0]]
                    
                    # Handle character replacements
                    for string in available_strings:
                        if string and len(string) > 0:
                            new_config = config.copy()
                            new_used_strings = used_strings.copy()
                            
                            # Apply case pattern to first character
                            new_config[i] = apply_case_pattern(token_rule["case_pattern"], string[0])
                            
                            # Mark this string as used (case insensitive)
                            new_used_strings.add(string.lower())
                            
                            new_configs.append((new_config, new_used_strings))
                
                # Symbol rule
                elif token_type == "symbol":
                    for symbol in symbols:
                        new_config = config.copy()
                        new_config[i] = symbol
                        new_configs.append((new_config, used_strings))
                
                # Number rules
                elif token_type == "common_number":
                    for num in common_numbers:
                        new_config = config.copy()
                        new_config[i] = num
                        new_configs.append((new_config, used_strings))
                
                elif token_type == "number":
                    for num in numbers:
                        new_config = config.copy()
                        new_config[i] = num
                        new_configs.append((new_config, used_strings))
                
                # Literal rule (already handled in base_tokens)
                elif token_type == "literal":
                    new_configs.append((config, used_strings))
                
                # If no rule matched or no replacements were made, keep the original config
                if not new_configs and token_type != "literal":
                    new_configs.append((config, used_strings))
            
            # Update configurations for next iteration
            configs = new_configs
        
        # Fill in any remaining None values and join tokens
        for config, _ in configs:
            filled_tokens = [t if t is not None else "" for t in config]
            password = join_tokens(filled_tokens)
            if password:  # Only add non-empty passwords
                all_passwords.add(password)
    
    return all_passwords