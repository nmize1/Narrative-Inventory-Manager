import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from StoredProcedures import *
import os

import os
import json

async def crawl_tracker(narrative):
    # Set up database connection
    nim_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Shared/NIM.db"))
    conn = connect_to_db(nim_db_path)

    # Tracker JSON file path
    tracker_file = "item_tracker.json"

    # Load previous tracker data
    if os.path.exists(tracker_file):
        with open(tracker_file, "r") as f:
            previous_tracker = json.load(f)
    else:
        previous_tracker = {}

    url = narrative[2]
    print(url)

    # Fetch and parse the tracker page
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to fetch the page. Status code: {response.status}")
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find('table')
            if not table:
                print("Table not found on the page.")
                return None

            headers = [th.text.strip() for th in table.find_all('th')]

            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = [td.text.strip() for td in tr.find_all('td')]
                if len(cells) == len(headers):
                    rows.append(cells)

            df = pd.DataFrame(rows, columns=headers)
            filtered_df = df[df['Receiver'] == "IAAcademy"]

            slots = get_all_player_slots(conn)
            slot_names = [slot[1] for slot in slots]
            items_in_narrative = get_items_by_narrative(conn, narrative[0])
            item_tracker = {}

            for index, row in filtered_df.iterrows():
                if row['Finder'] in slot_names:
                    matching_item = None
                    for item in items_in_narrative:
                        if item[1].lower() == row['Item'].lower():
                            matching_item = item
                            item_id = item[0]
                            break

                    if matching_item:
                        for slot in slots:
                            if slot[1] == row['Finder']:
                                team = get_team_by_id(conn, slot[2])

                        if team:
                            team_id = team[0]
                            if team_id not in item_tracker:
                                item_tracker[team_id] = {}
                            if item_id not in item_tracker[team_id]:
                                item_tracker[team_id][item_id] = 0
                            item_tracker[team_id][item_id] += 1
                    else:
                        print(f"Item '{row['Item']}' does not exist in the narrative")
                else:
                    print(f"Tracker has a slot named '{row['Finder']}' that isn't in PlayerSlots table.")

            for team_id, items in item_tracker.items():
                for item_id, count in items.items():
                    previous_count = previous_tracker.get(str(team_id), {}).get(str(item_id), 0)
                    if count > previous_count:
                        existing_inventory = get_inventories_by_team(conn, team_id)
                        matching_inventory = next((inv for inv in existing_inventory if inv[1] == item_id), None)

                        if matching_inventory:
                            new_amount = matching_inventory[2] + (count - previous_count)
                            update_inventory_amount(conn, matching_inventory[0], new_amount)
                        else:
                            create_inventory(conn, team_id=team_id, item_id=item_id, amount=count)

            with open(tracker_file, "w") as f:
                json.dump(item_tracker, f)

            return "Inventories updated from tracker."


async def shared_update_totals(narrative):
    tracker = await crawl_tracker(narrative)
