import pandas as pd
import re


def load_whatsapp_chat(file_path):
    """
    Read the WhatsApp chat file into a list of lines for processing.
    
    Args:
        file_path (str): Path to the WhatsApp chat export file
        
    Returns:
        list: List of lines from the chat file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def parse_chat_lines(lines):
    """
    Extract the date, time, sender's number, and message from each line using regular expressions.
    
    Args:
        lines (list): List of lines from the chat file
        
    Returns:
        pd.DataFrame: DataFrame with columns: date, time, number, message
    """
    pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - ([^:]+?)(?:: (.*)| added .*)$')

    parsed_data = []
    for line in lines:
        match = pattern.match(line)
        if match:
            date, time, sender, message = match.groups()
            if message is None:
                message = line.split(' - ', 1)[-1].split(': ', 1)[-1] if ': ' in line else line.split(' - ', 1)[-1]
            parsed_data.append({
                'date': date,
                'time': time,
                'number': sender,
                'message': message.strip()
            })

    return pd.DataFrame(parsed_data)


def flag_message(msg):
    """
    Flag messages based on their content.
    
    Args:
        msg (str): Message text
        
    Returns:
        str: Flag type ('added', 'removed', 'contains number', 'other')
    """
    has_non_at_number = bool(re.search(r'(?<!@)(?<!@ )\b(\d+)\b', msg))
    if re.search(r'\badded\b', msg, re.IGNORECASE):
        return 'added'
    if re.search(r'\bremoved\b', msg, re.IGNORECASE):
        return 'removed'
    elif has_non_at_number:
        return 'contains number'
    else:
        return 'other'


def extract_number(msg):
    """
    Extract the first number from a message, excluding numbers prefixed with @.
    
    Args:
        msg (str): Message text
        
    Returns:
        int or None: First number found in the message, or None if no number found
    """
    matches = re.findall(r'(?<!@)(?<!@ )\b(\d+)\b', msg)
    return int(matches[0]) if matches else None


def process_chat_data(chat_df):
    """
    Process the chat DataFrame by adding flags, extracting numbers, and calculating cumulative additions.
    
    Args:
        chat_df (pd.DataFrame): DataFrame with columns: date, time, number, message
        
    Returns:
        pd.DataFrame: Processed DataFrame with additional columns: flag, n_beers, n_added
    """
    chat_df = chat_df.copy()
    
    # Add flags
    chat_df['flag'] = chat_df['message'].apply(flag_message)
    
    # Extract numbers for messages flagged as 'contains number'
    chat_df['n_beers'] = chat_df.apply(
        lambda row: extract_number(row['message']) if row['flag'] == 'contains number' else None, 
        axis=1
    )
    
    # Calculate cumulative number of people added
    chat_df['n_added'] = (chat_df['flag'] == 'added').cumsum() - (chat_df['flag'] == 'removed').cumsum()
    
    return chat_df