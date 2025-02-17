import pandas as pd # RUN pip install pandas !!!!!
import time
import xml.etree.ElementTree as ET
import re
import os
from datetime import datetime

# enter the path to your csv file 
csv_file_path = input("Enter the full path to your csv file: ").strip() 

# check path
if not os.path.exists(csv_file_path):
    print(f"Error: File not found at {csv_file_path}")
    input("Press Enter to exit...")
    exit()

# read csv file
try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Error reading the CSV file: {e}")
    input("Press Enter to exit...")
    exit()

# extract MAL id
def extract_mal_id(url):
    match = re.search(r'/manga/(\d+)', str(url))
    return match.group(1) if match else None


def convert_status(status):
    status_mapping = {
        'Reading': "Reading",
        'Completed': "Completed",
        'On-Hold': "On-Hold",
        'Dropped': "Dropped",
        'Plan to Read': "Plan to Read"
    }
    return status_mapping.get(status, "Plan to Read")

def parse_date(date_str):
    if pd.isna(date_str) or not isinstance(date_str, str):
        return "0000-00-00"  # Default if missing

    possible_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]
    for fmt in possible_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d") 
        except ValueError:
            continue  

    return "0000-00-00"  # If all fail, return blank date


root = ET.Element('myanimelist')

# add myinfo entry (adjust as needed)
myinfo = ET.SubElement(root, 'myinfo')
ET.SubElement(myinfo, 'user_id').text = ""  # Leave blank
ET.SubElement(myinfo, 'user_name').text = "kirbon"  #username (not needed to change)
ET.SubElement(myinfo, 'user_export_type').text = "2"
ET.SubElement(myinfo, 'user_total_manga').text = str(len(df))
ET.SubElement(myinfo, 'user_total_reading').text = str(len(df[df['type'] == "Reading"]))
ET.SubElement(myinfo, 'user_total_completed').text = str(len(df[df['type'] == "Completed"]))
ET.SubElement(myinfo, 'user_total_onhold').text = str(len(df[df['type'] == "On-Hold"]))
ET.SubElement(myinfo, 'user_total_dropped').text = str(len(df[df['type'] == "Dropped"]))
ET.SubElement(myinfo, 'user_total_plantoread').text = str(len(df[df['type'] == "Plan to Read"]))

# adds entries (anything that is '0' is defaulted)
for _, row in df.iterrows():
    mal_id = extract_mal_id(row['mal'])
    if mal_id:
        manga = ET.SubElement(root, 'manga')
        ET.SubElement(manga, 'manga_mangadb_id').text = mal_id
        ET.SubElement(manga, 'manga_title').text = f"<![CDATA[{row['title']}]]>"
        ET.SubElement(manga, 'manga_volumes').text = "0" 
        ET.SubElement(manga, 'manga_chapters').text = "0" 
        ET.SubElement(manga, 'my_id').text = "0"
        ET.SubElement(manga, 'my_read_volumes').text = "0"
        ET.SubElement(manga, 'my_read_chapters').text = str(int(row['read'])) if not pd.isna(row['read']) else "0"
        ET.SubElement(manga, 'my_start_date').text = parse_date(row['last_read'])
        ET.SubElement(manga, 'my_finish_date').text = parse_date(row['last_read'])
        ET.SubElement(manga, 'my_scanalation_group').text = ""
        ET.SubElement(manga, 'my_score').text = str(int(row['rating'])) if not pd.isna(row['rating']) else "0"
        ET.SubElement(manga, 'my_storage').text = ""
        ET.SubElement(manga, 'my_status').text = convert_status(row['type'])
        ET.SubElement(manga, 'my_comments').text = ""
        ET.SubElement(manga, 'my_times_read').text = "0"
        ET.SubElement(manga, 'my_tags').text = ""
        ET.SubElement(manga, 'my_reread_value').text = "Low"
        ET.SubElement(manga, 'update_on_import').text = "1"

# xml export
output_file_path = os.path.splitext(csv_file_path)[0] + "_mal.xml"
tree = ET.ElementTree(root)
tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

print(f'XML file "{output_file_path}" created successfully!')
input("Press Enter to exit...")
