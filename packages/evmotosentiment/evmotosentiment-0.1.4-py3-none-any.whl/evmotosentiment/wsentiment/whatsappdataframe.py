import pandas as pd
import re

def wdataframe(path):
    """Create a Dataframe from text document

    Parameters
    ----------
    path : str
        Path to text file.
        

    Returns
    -------
    pd.DataFrame
        A dataframe produced from the text document

    """
    # Load the entire chat file
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    # Regular expression pattern
    pattern = r'^(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2})\s?[ap]m\s? - (.*?): (.*)'

    # Store parsed data here
    parsed_chats = []

    for line in lines:
        match = re.match(pattern, line, flags=re.IGNORECASE)
        if match:
            date = match.group(1)
            time = match.group(2)
            sender = match.group(3)
            message = match.group(4)
            parsed_chats.append({
                'date': date,
                'time': time,
                'sender': sender,
                'message': message
            })
        else:
            # Append message to the previous message (multi-line message)
            if parsed_chats:
                parsed_chats[-1]['message'] += '\n' + line

    # Convert to DataFrame
    df = pd.DataFrame(parsed_chats)

    # Optional: combine date and time into a single datetime column
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst=True)

    # Reorder columns
    df = df[['datetime', 'sender', 'message']]

    # Preview
    return df