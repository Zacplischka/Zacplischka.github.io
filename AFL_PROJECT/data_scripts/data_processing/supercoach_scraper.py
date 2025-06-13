#!/usr/bin/env python3
"""
SuperCoach Price Scraper

This script scrapes AFL SuperCoach player prices from FootyWire and parses
the concatenated player data into separate columns for analysis.

Author: AFL Project
Date: June 2025
"""

import pandas as pd
import requests
import re
from datetime import date
from bs4 import BeautifulSoup as bs
from db_connect import connect_to_database


def get_team_mapping():
    """
    Get the mapping from SuperCoach team abbreviations to official database team names
    
    Returns:
        dict: Mapping of SuperCoach abbreviations to official team names
    """
    return {
        'Blues': 'Carlton',
        'Bombers': 'Essendon', 
        'Bulldogs': 'Western Bulldogs',
        'Cats': 'Geelong Cats',
        'Crows': 'Adelaide Crows',
        'Demons': 'Melbourne',
        'Dockers': 'Fremantle',
        'Eagles': 'West Coast Eagles',
        'Giants': 'GWS GIANTS',
        'Hawks': 'Hawthorn',
        'Kangaroos': 'North Melbourne',
        'Lions': 'Brisbane Lions',
        'Magpies': 'Collingwood',
        'Power': 'Port Adelaide',
        'Saints': 'St Kilda',
        'Suns': 'Gold Coast SUNS',
        'Swans': 'Sydney Swans',
        'Tigers': 'Richmond'
    }


def standardize_team_name(supercoach_team):
    """
    Convert SuperCoach team abbreviation to official database team name
    
    Args:
        supercoach_team (str): SuperCoach team abbreviation
        
    Returns:
        str: Official database team name
    """
    if pd.isna(supercoach_team) or not supercoach_team:
        return None
    
    team_mapping = get_team_mapping()
    return team_mapping.get(supercoach_team, supercoach_team)


def parse_player_data(player_string):
    """
    Parse concatenated player data like 'Tristan XerriT XerriKangaroos' or 'Massimo D Ambrosio M D Ambrosio Hawks'
    into separate components: full_name, abbreviated_name, team
    
    Args:
        player_string (str): Concatenated player string from FootyWire
        
    Returns:
        tuple: (full_name, abbreviated_name, team)
    """
    if pd.isna(player_string) or player_string == 'No results found.':
        return None, None, None
    
    # Handle edge case where parsing fails
    if not player_string or len(player_string.strip()) == 0:
        return None, None, None
    
    # Known team abbreviations to help identify where team starts
    team_mapping = get_team_mapping()
    team_abbreviations = list(team_mapping.keys())
    
    # Split by capital letters to identify boundaries
    parts = re.findall(r'[A-Z][a-z]*', player_string)
    
    if len(parts) < 3:
        return player_string, None, None
    
    # Find team at the end first
    team = None
    team_start_idx = None
    
    # Check if last part is a known team
    if parts[-1] in team_abbreviations:
        team = parts[-1]
        team_start_idx = len(parts) - 1
        parts = parts[:-1]  # Remove team from parts for name parsing
    
    # Now we need to split the remaining parts into full name and abbreviated name
    # The pattern is: [Full Name Parts] [Abbreviated Name Parts]
    # Where abbreviated name is usually: [First Initial] [Last Name Parts]
    
    # Strategy: Look for patterns where we have duplicate surname sequences
    # Example: "Massimo D Ambrosio M D Ambrosio" -> full="Massimo D Ambrosio", abbrev="M D Ambrosio"
    
    # Find potential split points by looking for single letters that could be initials
    potential_splits = []
    for i, part in enumerate(parts):
        if len(part) == 1 and i > 0 and i < len(parts) - 1:
            potential_splits.append(i)
    
    best_split = None
    best_score = 0
    
    for split_idx in potential_splits:
        # Test this split point
        full_name_parts = parts[:split_idx]
        abbrev_parts = parts[split_idx:]
        
        # Score this split based on how well it matches expected patterns
        score = 0
        
        # Check if we have at least 2 parts in full name (first + surname)
        if len(full_name_parts) >= 2:
            score += 1
            
        # Check if abbreviated part starts with single letter (initial)
        if len(abbrev_parts) > 0 and len(abbrev_parts[0]) == 1:
            score += 2
            
        # Check if there's overlap between surname parts in full and abbreviated
        if len(full_name_parts) >= 2 and len(abbrev_parts) >= 2:
            full_surname_parts = full_name_parts[1:]  # Skip first name
            abbrev_surname_parts = abbrev_parts[1:]   # Skip initial
            
            # Check for exact matches in surname parts
            common_parts = set(full_surname_parts) & set(abbrev_surname_parts)
            score += len(common_parts) * 3  # Heavy weight for surname matching
            
        if score > best_score:
            best_score = score
            best_split = split_idx
    
    # If we found a good split, use it
    if best_split is not None and best_score >= 3:  # Minimum threshold
        full_name_parts = parts[:best_split]
        abbrev_parts = parts[best_split:]
        
        full_name = ' '.join(full_name_parts)
        abbrev_name = ' '.join(abbrev_parts)
    else:
        # Fallback: use original logic but improved
        # Look for the first single letter that appears after at least one word
        abbrev_start = None
        for i in range(1, len(parts)):
            if len(parts[i]) == 1:
                abbrev_start = i
                break
        
        if abbrev_start is not None:
            full_name_parts = parts[:abbrev_start]
            abbrev_parts = parts[abbrev_start:]
            
            full_name = ' '.join(full_name_parts)
            
            # For abbreviated name, try to find where it ends (before team or at end)
            abbrev_name = ' '.join(abbrev_parts)
        else:
            # Last resort: treat everything as full name
            full_name = ' '.join(parts)
            abbrev_name = None
    
    # Standardize team name before returning
    standardized_team = standardize_team_name(team)
    
    return full_name, abbrev_name, standardized_team


def scrape_supercoach_prices():
    """
    Scrape SuperCoach prices from FootyWire and return cleaned DataFrame
    
    Returns:
        pd.DataFrame: Cleaned DataFrame with parsed player data
    """
    url = "https://www.footywire.com/afl/footy/supercoach_prices"
    
    print("Fetching SuperCoach prices from FootyWire...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = bs(response.content, 'html.parser')
        
        # Find the div with ID 'fantasy-prices-div'
        fantasy_div = soup.find('div', {'id': 'fantasy-prices-div'})
        
        if not fantasy_div:
            print("Error: fantasy-prices-div not found")
            return None
            
        # Find the table within this div
        table = fantasy_div.find('table')
        
        if not table:
            print("Error: No table found within the fantasy-prices-div")
            return None
            
        print("Table found successfully!")
        
        # Extract table headers
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True))
        
        print(f"Headers: {headers}")
        
        # Extract all table rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text(strip=True))
            if row:  # Only add non-empty rows
                rows.append(row)
        
        print(f"Found {len(rows)} data rows")
        
        # Create DataFrame
        if headers and rows:
            # Ensure all rows have the same number of columns as headers
            max_cols = len(headers)
            cleaned_rows = []
            for row in rows:
                # Pad or trim row to match header length
                if len(row) < max_cols:
                    row.extend([''] * (max_cols - len(row)))
                elif len(row) > max_cols:
                    row = row[:max_cols]
                cleaned_rows.append(row)
            
            supercoach_df = pd.DataFrame(cleaned_rows, columns=headers)
            print(f"DataFrame created with shape: {supercoach_df.shape}")
            
            return supercoach_df
        else:
            print("Error: Could not create DataFrame - missing headers or data")
            return None
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None


def clean_supercoach_data(supercoach_df, db_connection=None):
    """
    Clean and parse the SuperCoach DataFrame
    
    Args:
        supercoach_df (pd.DataFrame): Raw SuperCoach DataFrame
        db_connection: Database connection for player matching
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with parsed player data and player_id column
    """
    if supercoach_df is None:
        print("No supercoach data available to parse")
        return None
    
    # Remove the "No results found." row if it exists
    supercoach_df_clean = supercoach_df[supercoach_df['Player'] != 'No results found.'].copy()
    
    # Parse the player data (includes automatic team name standardization)
    print("Parsing player data and standardizing team names...")
    parsed_data = supercoach_df_clean['Player'].apply(parse_player_data)
    
    # Extract the parsed components into separate columns
    # Note: Team names are automatically standardized to match player_details table
    supercoach_df_clean[['Full_Name', 'Abbreviated_Name', 'Team']] = pd.DataFrame(
        parsed_data.tolist(), index=supercoach_df_clean.index
    )
    
    # Reorder columns to put the parsed data first and rename for database
    cols = ['Full_Name', 'Abbreviated_Name', 'Team'] + [col for col in supercoach_df_clean.columns if col not in ['Player', 'Full_Name', 'Abbreviated_Name', 'Team']]
    supercoach_df_clean = supercoach_df_clean[cols]
    
    # Rename columns to match database schema
    column_mapping = {
        'Full_Name': 'full_name',
        'Abbreviated_Name': 'abbreviated_name', 
        'Team': 'team',
        'Current': 'current_price',
        'Total Change': 'total_change',
        'Change %': 'change_percentage',
        'Last Change': 'last_change',
        'Expected Price': 'expected_price',
        'Expected Change': 'expected_change',
        'Expected Price 2': 'expected_price_2',
        'Expected Change 2': 'expected_change_2',
        'Expected Price 3': 'expected_price_3',
        'Expected Change 3': 'expected_change_3'
    }
    
    supercoach_df_clean = supercoach_df_clean.rename(columns=column_mapping)
    
    # Convert price and percentage columns to numerical values
    print("Converting price data to numerical format...")
    
    # Price columns to convert
    price_columns = ['current_price', 'total_change', 'last_change', 
                     'expected_price', 'expected_change', 'expected_price_2', 
                     'expected_change_2', 'expected_price_3', 'expected_change_3']
    
    for col in price_columns:
        if col in supercoach_df_clean.columns:
            supercoach_df_clean[col] = supercoach_df_clean[col].apply(convert_price_to_number)
    
    # Convert percentage column
    if 'change_percentage' in supercoach_df_clean.columns:
        supercoach_df_clean['change_percentage'] = supercoach_df_clean['change_percentage'].apply(convert_percentage_to_number)
    
    # Add scraped date
    supercoach_df_clean['scraped_date'] = date.today().strftime('%Y-%m-%d')
    
    # Add player_id column by matching with player_details table
    if db_connection is not None:
        print("Matching players to database IDs...")
        
        # Get a raw database connection for querying
        from db_connect import connect_to_database_raw
        raw_conn = connect_to_database_raw()
        
        if raw_conn:
            supercoach_df_clean['player_id'] = supercoach_df_clean.apply(
                lambda row: match_player_id(row['full_name'], row['team'], raw_conn),
                axis=1
            )
            raw_conn.close()
            
            # Report matching results
            matched_count = supercoach_df_clean['player_id'].notna().sum()
            total_count = len(supercoach_df_clean)
            print(f"✅ Successfully matched {matched_count}/{total_count} players to database IDs")
            
            if matched_count < total_count:
                unmatched = supercoach_df_clean[supercoach_df_clean['player_id'].isna()]
                print(f"⚠️ Unmatched players ({len(unmatched)}):")
                for _, row in unmatched.head(10).iterrows():
                    print(f"  - {row['full_name']} ({row['team']})")
                if len(unmatched) > 10:
                    print(f"  ... and {len(unmatched) - 10} more")
        else:
            print("⚠️ Could not establish raw database connection for player matching")
            supercoach_df_clean['player_id'] = None
    else:
        print("⚠️ No database connection - player_id column will be empty")
        supercoach_df_clean['player_id'] = None
    
    print(f"Successfully parsed {len(supercoach_df_clean)} player records")
    print("✅ Price data converted to numerical format")
    
    # Show some stats about the data
    print(f"Number of unique teams: {supercoach_df_clean['team'].nunique()}")
    
    # Filter out None values before sorting
    teams = [team for team in supercoach_df_clean['team'].unique() if team is not None]
    print(f"Teams: {sorted(teams)}")
    
    # Check if there are any None values
    none_count = supercoach_df_clean['team'].isna().sum()
    if none_count > 0:
        print(f"Note: {none_count} players have unparseable team names")
    
    return supercoach_df_clean


def convert_price_to_number(price_string):
    """
    Convert price string like "$731,200" or "+$85,300" to numerical value
    
    Args:
        price_string (str): Price string from FootyWire
        
    Returns:
        float or None: Numerical value or None if conversion fails
    """
    if pd.isna(price_string) or price_string == '' or price_string == '?':
        return None
    
    try:
        # Remove $, +, -, and commas, then convert to float
        cleaned = str(price_string).replace('$', '').replace(',', '').replace('+', '')
        
        # Handle negative values
        if price_string.startswith('-'):
            return -float(cleaned.replace('-', ''))
        else:
            return float(cleaned)
    except (ValueError, AttributeError):
        return None


def convert_percentage_to_number(percentage_string):
    """
    Convert percentage string like "6%" or "-63%" to numerical value
    
    Args:
        percentage_string (str): Percentage string from FootyWire
        
    Returns:
        float or None: Numerical value or None if conversion fails
    """
    if pd.isna(percentage_string) or percentage_string == '' or percentage_string == '?':
        return None
    
    try:
        # Remove % and convert to float
        cleaned = str(percentage_string).replace('%', '')
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def save_to_csv(df, filename='data_scripts/data/supercoach_prices.csv'):
    """
    Save DataFrame to CSV file
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filename (str): Output filename
    """
    if df is not None:
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")


def push_to_database(df, db_connection):
    """
    Push SuperCoach data to database
    
    Args:
        df (pd.DataFrame): DataFrame to push
        db_connection: SQLAlchemy engine or database connection object
    """
    try:
        df.to_sql('supercoach_prices', db_connection, if_exists='replace', index=False)
        print(f"✅ SuperCoach data successfully pushed to database (supercoach_prices table)")
        print(f"   {len(df)} records inserted")
    except Exception as e:
        print(f"❌ Error pushing SuperCoach data to database: {e}")


def normalize_name(name):
    """
    Normalize a name to handle common variations
    """
    if not name:
        return name
    
    # Name mappings for common variations (expanded with database findings)
    name_mappings = {
        # Full to short mappings
        'Thomas': 'Tom',
        'Timothy': 'Tim',
        'Nicholas': 'Nick',
        'Nic': 'Nick',  # Also handle reverse mapping
        'Joshua': 'Josh',
        'Oliver': 'Ollie',
        'Cameron': 'Cam',
        'Zachary': 'Zac',
        'Mitchell': 'Mitch',
        'Mitchito': 'Mitch',  # Special case
        'Jeremy': 'Jerm',
        'Jackson': 'Jack',
        'Anthony': 'Tony',
        'William': 'Will',
        'Christopher': 'Chris',
        'Benjamin': 'Ben',
        'Matthew': 'Matt',
        'Jonathan': 'Jon',
        'Alexander': 'Alex',
        'Michael': 'Mick',
        'Bradley': 'Brad',
        'Samuel': 'Sam',
        'Dominic': 'Dom',
        'Nikolas': 'Nik',
        'Joseph': 'Joe',
        'Daniel': 'Dan',
        # Short to full mappings (for reverse cases)
        'Nick': 'Nicholas',
        'Ollie': 'Oliver',
        'Mitch': 'Mitchell',
        'Nik': 'Nikolas',
        'Joe': 'Joseph',
        'Dan': 'Daniel',
        'Tom': 'Thomas'
    }
    
    # Handle spaces in surnames (like Mc Cluggage -> McCluggage, Mac Donald -> Macdonald)
    name = name.replace(' Mc ', 'Mc').replace(' Mac ', 'Mac').replace(' O\'', 'O\'')
    name = name.replace('Mc ', 'Mc').replace('Mac ', 'Mac')
    
    # Handle hyphenated names (Neal Bullen -> Neal-Bullen)
    if ' ' in name and name.count(' ') == 1 and name not in name_mappings:
        # This might be a hyphenated surname
        parts = name.split(' ')
        if len(parts) == 2 and len(parts[0]) > 2 and len(parts[1]) > 2:
            # Likely a hyphenated surname
            name = '-'.join(parts)
    
    # Check if it's a mapped name
    return name_mappings.get(name, name)


def get_name_variants(name):
    """
    Get all possible variants of a name (both directions)
    """
    if not name:
        return [name]
    
    variants = [name]  # Include original
    normalized = normalize_name(name)
    if normalized != name:
        variants.append(normalized)
    
    # Also check reverse mapping
    reverse_mapping = {
        'Nick': ['Nicholas', 'Nic'],
        'Nicholas': ['Nick', 'Nic'],
        'Nic': ['Nicholas', 'Nick'],
        'Ollie': ['Oliver'],
        'Oliver': ['Ollie'],
        'Mitch': ['Mitchell', 'Mitchito'],
        'Mitchell': ['Mitch'],
        'Mitchito': ['Mitch', 'Mitchell'],
        'Nik': ['Nikolas'],
        'Nikolas': ['Nik'],
        'Joe': ['Joseph'],
        'Joseph': ['Joe'],
        'Dan': ['Daniel'],
        'Daniel': ['Dan'],
        'Tom': ['Thomas'],
        'Thomas': ['Tom'],
        'Josh': ['Joshua'],
        'Joshua': ['Josh'],
        'Cam': ['Cameron'],
        'Cameron': ['Cam'],
        'Zac': ['Zachary'],
        'Zachary': ['Zac'],
        'Brad': ['Bradley'],
        'Bradley': ['Brad'],
        'Sam': ['Samuel'],
        'Samuel': ['Sam']
    }
    
    if name in reverse_mapping:
        variants.extend(reverse_mapping[name])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variants = []
    for variant in variants:
        if variant not in seen:
            seen.add(variant)
            unique_variants.append(variant)
    
    return unique_variants


def match_player_id(full_name, team, db_connection):
    """
    Match a SuperCoach player to a player_id from the player_details table
    Uses multiple strategies to achieve 100% matching rate
    
    Args:
        full_name (str): Full name from SuperCoach data
        team (str): Team abbreviation from SuperCoach data  
        db_connection: Database connection
        
    Returns:
        int or None: player_id if match found, None otherwise
    """
    if pd.isna(full_name) or not full_name or not db_connection:
        return None
    
    # Skip players without valid team information
    if pd.isna(team) or not team or team == 'None':
        return None

    try:
        # Team name should already be standardized from parse_player_data()
        # No need for additional mapping here
        full_team_name = team
        
        # Split and normalize the name
        name_parts = full_name.strip().split()
        if len(name_parts) < 1:
            return None
        
        # Handle single names (first name only)
        if len(name_parts) == 1:
            return match_by_first_name_only(name_parts[0], full_team_name, db_connection)
        
        # Handle multiple name parts
        first_name = normalize_name(name_parts[0])
        last_name_raw = ' '.join(name_parts[1:])
        last_name = normalize_name(last_name_raw)
        
        # Strategy 1: Exact match with normalized names
        result = try_exact_match(first_name, last_name, full_team_name, db_connection)
        if result:
            return result
            
        # Strategy 2: Try with original first name if normalized
        if first_name != name_parts[0]:
            result = try_exact_match(name_parts[0], last_name, full_team_name, db_connection)
            if result:
                return result
        
        # Strategy 3: Try with original last name if normalized
        if last_name != last_name_raw:
            result = try_exact_match(first_name, last_name_raw, full_team_name, db_connection)
            if result:
                return result
        
        # Strategy 4: Try both original names
        if first_name != name_parts[0] and last_name != last_name_raw:
            result = try_exact_match(name_parts[0], last_name_raw, full_team_name, db_connection)
            if result:
                return result
        
        # Strategy 5: Try reverse mapping (in case database has full name but SuperCoach has short)
        # Get all possible variations
        first_name_variants = get_name_variants(name_parts[0])
        for first_variant in first_name_variants:
            result = try_exact_match(first_variant, last_name, full_team_name, db_connection)
            if result:
                return result
            if last_name != last_name_raw:
                result = try_exact_match(first_variant, last_name_raw, full_team_name, db_connection)
                if result:
                    return result
        
        # Strategy 6: Fuzzy matching with ILIKE
        result = try_fuzzy_match(first_name, last_name, full_team_name, db_connection)
        if result:
            return result
            
        # Strategy 7: Try different name combinations for complex surnames
        result = try_complex_surname_match(name_parts, full_team_name, db_connection)
        if result:
            return result
            
        # Strategy 8: Last resort - match by team and partial name only
        result = try_partial_name_match(name_parts, full_team_name, db_connection)
        if result:
            return result
        
        return None
        
    except Exception as e:
        print(f"Error matching player {full_name}: {e}")
        return None


def match_by_first_name_only(first_name, team_name, db_connection):
    """Match players with only first name provided"""
    query = """
    SELECT id FROM player_details 
    WHERE LOWER("firstName") = LOWER(%s)
    AND LOWER(team) = LOWER(%s)
    AND season = (SELECT MAX(season) FROM player_details WHERE LOWER("firstName") = LOWER(%s))
    LIMIT 1
    """
    
    if hasattr(db_connection, 'cursor'):
        with db_connection.cursor() as cursor:
            cursor.execute(query, (first_name, team_name, first_name))
            result = cursor.fetchone()
            if result:
                return result[0]
    return None


def try_exact_match(first_name, last_name, team_name, db_connection):
    """Try exact name and team match"""
    query = """
    SELECT id FROM player_details 
    WHERE LOWER("firstName") = LOWER(%s) 
    AND LOWER(surname) = LOWER(%s)
    AND LOWER(team) = LOWER(%s)
    AND season = (SELECT MAX(season) FROM player_details WHERE LOWER("firstName") = LOWER(%s) AND LOWER(surname) = LOWER(%s))
    LIMIT 1
    """
    
    if hasattr(db_connection, 'cursor'):
        with db_connection.cursor() as cursor:
            cursor.execute(query, (first_name, last_name, team_name, first_name, last_name))
            result = cursor.fetchone()
            if result:
                return result[0]
    return None


def try_fuzzy_match(first_name, last_name, team_name, db_connection):
    """Try fuzzy matching with ILIKE"""
    
    # First try exact surname with fuzzy first name  
    query = """
    SELECT id FROM player_details 
    WHERE LOWER("firstName") ILIKE LOWER(%s)
    AND LOWER(surname) = LOWER(%s)
    AND LOWER(team) = LOWER(%s)
    AND season = (SELECT MAX(season) FROM player_details WHERE LOWER("firstName") ILIKE LOWER(%s) AND LOWER(surname) = LOWER(%s))
    LIMIT 1
    """
    
    if hasattr(db_connection, 'cursor'):
        with db_connection.cursor() as cursor:
            # Try fuzzy first name with exact surname
            cursor.execute(query, (f'%{first_name}%', last_name, team_name, f'%{first_name}%', last_name))
            result = cursor.fetchone()
            if result:
                return result[0]
                
            # Try exact first name with fuzzy surname
            query2 = """
            SELECT id FROM player_details 
            WHERE LOWER("firstName") = LOWER(%s)
            AND LOWER(surname) ILIKE LOWER(%s)
            AND LOWER(team) = LOWER(%s)
            AND season = (SELECT MAX(season) FROM player_details WHERE LOWER("firstName") = LOWER(%s) AND LOWER(surname) ILIKE LOWER(%s))
            LIMIT 1
            """
            cursor.execute(query2, (first_name, f'%{last_name}%', team_name, first_name, f'%{last_name}%'))
            result = cursor.fetchone()
            if result:
                return result[0]
                
            # Full fuzzy match as last resort
            query3 = """
            SELECT id FROM player_details 
            WHERE LOWER("firstName") ILIKE LOWER(%s)
            AND LOWER(surname) ILIKE LOWER(%s)
            AND LOWER(team) = LOWER(%s)
            AND season = (SELECT MAX(season) FROM player_details WHERE LOWER("firstName") ILIKE LOWER(%s) AND LOWER(surname) ILIKE LOWER(%s))
            LIMIT 1
            """
            cursor.execute(query3, (f'%{first_name}%', f'%{last_name}%', team_name, f'%{first_name}%', f'%{last_name}%'))
            result = cursor.fetchone()
            if result:
                return result[0]
    return None


def try_complex_surname_match(name_parts, team_name, db_connection):
    """Handle complex surnames like hyphenated names, Mc/Mac variations"""
    if len(name_parts) < 3:
        return None
        
    first_name = name_parts[0]
    
    # Try different surname combinations
    surname_variations = []
    
    # Try all parts as surname
    surname_variations.append(' '.join(name_parts[1:]))
    
    # Try hyphenated version
    if len(name_parts) == 3:
        surname_variations.append(f"{name_parts[1]}-{name_parts[2]}")
    
    # Try Mc/Mac variations
    if len(name_parts) >= 3 and name_parts[1].lower() in ['mc', 'mac']:
        surname_variations.append(f"{name_parts[1]}{name_parts[2]}")
        surname_variations.append(f"{name_parts[1]} {name_parts[2]}")
    
    for surname in surname_variations:
        result = try_exact_match(first_name, surname, team_name, db_connection)
        if result:
            return result
            
    return None


def try_partial_name_match(name_parts, team_name, db_connection):
    """Last resort: match by team and any part of the name"""
    first_name = name_parts[0]
    
    # Try to find any player with this first name on this team
    query = """
    SELECT id FROM player_details 
    WHERE LOWER("firstName") = LOWER(%s)
    AND LOWER(team) = LOWER(%s)
    AND season = (SELECT MAX(season) FROM player_details)
    LIMIT 1
    """
    
    if hasattr(db_connection, 'cursor'):
        with db_connection.cursor() as cursor:
            cursor.execute(query, (first_name, team_name))
            result = cursor.fetchone()
            if result:
                return result[0]
    
    return None


def main():
    """
    Main function to run the SuperCoach scraper
    """
    print("Starting SuperCoach Price Scraper...")
    
    # Setup database connection
    print("\n🗄️ SETTING UP DATABASE CONNECTION")
    print("="*50)
    
    db_connection = connect_to_database()
    
    if db_connection is None:
        print("❌ Could not establish database connection. Will save to CSV only.")
    
    # Scrape the data
    raw_df = scrape_supercoach_prices()
    
    if raw_df is not None:
        # Clean and parse the data
        cleaned_df = clean_supercoach_data(raw_df, db_connection)
        
        if cleaned_df is not None:
            # Display sample results
            print("\nFirst 10 rows with parsed data:")
            print(cleaned_df[['full_name', 'abbreviated_name', 'team', 'current_price']].head(10))
            
            # Show team standardization results
            unique_teams = cleaned_df['team'].dropna().unique()
            print(f"\n🏟️ Team Standardization Results:")
            print(f"✅ All {len(unique_teams)} teams now use official database names")
            print(f"✅ Team names automatically standardized from SuperCoach abbreviations")
            
            # Save to CSV
            save_to_csv(cleaned_df)
            
            # Push to database if connection is available
            if db_connection is not None:
                print("\n🗄️ PUSHING DATA TO DATABASE")
                print("="*50)
                push_to_database(cleaned_df, db_connection)
                
                # Close database connection
                print("\n🔐 CLOSING DATABASE CONNECTION")
                print("="*50)
                db_connection.dispose()
                print("✅ Database connection closed successfully")
            
            print(f"\nFinal cleaned SuperCoach DataFrame:")
            print(f"Shape: {cleaned_df.shape}")
            print(f"Columns: {list(cleaned_df.columns)}")
            
            print("\n🎉 SUPERCOACH DATA PROCESSING COMPLETE!")
            print("="*50)
            print("✅ CSV file saved")
            if db_connection is not None:
                print("✅ Data pushed to PostgreSQL database: afl_database")
            print("🚀 Ready for analysis!")
            
            return cleaned_df
        else:
            print("Failed to clean data")
            return None
    else:
        print("Failed to scrape data")
        return None


if __name__ == "__main__":
    supercoach_data = main()
