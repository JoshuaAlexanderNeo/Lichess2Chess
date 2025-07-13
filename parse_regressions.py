import pandas as pd
from requests_html import HTMLSession
import sys
import time

def parse_table(table_element):
    # Extract headers, cleaning up <br> tags
    headers = []
    for th in table_element.find('th'):
        # Replace <br> with a space and then get text, strip extra whitespace
        header_text = th.text.replace('\n', ' ').strip()
        headers.append(header_text)

    rows = []
    # Iterate through rows, skipping the header row (which is the first tr)
    for tr in table_element.find('tr')[1:]:
        row_data = [td.text.strip() for td in tr.find('td')]
        # Filter out empty strings from row_data if any td is empty
        row_data = [item for item in row_data if item]
        if row_data: # Only add non-empty rows
            rows.append(row_data)
    return pd.DataFrame(rows, columns=headers)

def main():
    session = HTMLSession()
    url = 'https://chessgoals.com/rating-comparison/'
    try:
        response = session.get(url)
        # Render JavaScript to load dynamic content and tables
        # Wait for the first pagination select element to be present
        response.html.render(wait_for_selector='#dt-length-0', timeout=30, sleep=5) 
        response.raise_for_status() # Raise an exception for bad status codes
    except Exception as e:
        print(f"Error fetching or rendering URL: {e}")
        sys.exit(1)

    # Execute JavaScript to change entries per page to 100 for both tables
    # tablepress-24 is the first table, tablepress-27 is the second
    script = """
        document.querySelector('#dt-length-0').value = '100';
        document.querySelector('#dt-length-0').dispatchEvent(new Event('change'));
        document.querySelector('#dt-length-1').value = '100';
        document.querySelector('#dt-length-1').dispatchEvent(new Event('change'));
    """
    try:
        # Execute the script using render's script argument
        # Wait for the second pagination select element to be present before executing script
        response.html.render(script=script, wait_for_selector='#dt-length-1', timeout=30, sleep=5) 
    except Exception as e:
        print(f"Error executing JavaScript or re-rendering after pagination change: {e}")
        sys.exit(1)

    # Find tables by their specific IDs
    tablepress_24 = response.html.find('#tablepress-24', first=True)
    tablepress_27 = response.html.find('#tablepress-27', first=True)

    if not tablepress_24 or not tablepress_27:
        print("Error: Could not find both required tables (tablepress-24 and tablepress-27) after pagination update.")
        sys.exit(1)

    # Process tablepress-24 (Chess.com vs. FIDE and USCF)
    df_24 = parse_table(tablepress_24)
    filename_24 = 'chess_com_to_chess_com_data.csv'
    # Rename columns to match the original CSV for consistency
    df_24 = df_24.rename(columns={
        'Chess.com Blitz': 'chess_com_blitz',
        'Bullet (+/- 130) N=9249': 'chess_com_bullet',
        'Rapid (+/- 115) N=10193': 'chess_com_rapid',
        'USCF (+/- 130) N=1293': 'uscf',
        'FIDE (+/- 85) N=1873': 'fide'
    })
    # Select only the columns we need and ensure order
    df_24 = df_24[['chess_com_blitz', 'chess_com_bullet', 'chess_com_rapid', 'uscf', 'fide']]
    
    updated_24 = False
    try:
        existing_df_24 = pd.read_csv(filename_24)
        if not df_24.equals(existing_df_24): # Use .equals for DataFrame comparison
            df_24.to_csv(filename_24, index=False)
            updated_24 = True
    except FileNotFoundError:
        df_24.to_csv(filename_24, index=False)
        updated_24 = True

    if updated_24:
        print(f"Updated {filename_24}")
    else:
        print(f"{filename_24} is already up to date.")

    # Process tablepress-27 (Lichess vs. Chess.com)
    df_27 = parse_table(tablepress_27)
    filename_27 = 'lichess_to_chess_com_data.csv'
    # Rename columns to match the original CSV for consistency
    df_27 = df_27.rename(columns={
        'Chess.com Blitz': 'chess_com_blitz',
        'Lichess Blitz (+/- 75) N=2489': 'lichess_blitz',
        'Lichess Bullet (+/- 120) N=1945': 'lichess_bullet',
        'Lichess Rapid (+/- 100) N=1344': 'lichess_rapid',
        'Lichess Classical (+/- 85) N=314': 'lichess_classical'
    })
    # Select only the columns we need and ensure order
    df_27 = df_27[['chess_com_blitz', 'lichess_blitz', 'lichess_bullet', 'lichess_rapid', 'lichess_classical']]

    updated_27 = False
    try:
        existing_df_27 = pd.read_csv(filename_27)
        if not df_27.equals(existing_df_27): # Use .equals for DataFrame comparison
            df_27.to_csv(filename_27, index=False)
            updated_27 = True
    except FileNotFoundError:
        df_27.to_csv(filename_27, index=False)
        updated_27 = True

    if updated_27:
        print(f"Updated {filename_27}")
    else:
        print(f"{filename_27} is already up to date.")

if __name__ == '__main__':
    main()
