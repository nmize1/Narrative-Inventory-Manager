import sqlite3

# Connect to the database
def connect_to_db(db_name="example.db"):
    """Connect to the SQLite database."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

## NARRATIVES ##

# Create operations
def create_narrative(conn, narrative_name, sphere_tracker):
    """Insert a new narrative record."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO Narratives (NarrativeName, SphereTracker)
        VALUES (?)
    '''
    cursor.execute(query, (narrative_name, sphere_tracker,))
    conn.commit()
    return cursor.lastrowid  # Return the newly created NarrativeID


# Read operations
def get_narrative_by_id(conn, narrative_id):
    """Retrieve a specific narrative record by NarrativeID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Narratives
        WHERE NarrativeID = ?
    '''
    cursor.execute(query, (narrative_id,))
    return cursor.fetchone()


def get_all_narratives(conn):
    """Retrieve all narrative records."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Narratives
    '''
    cursor.execute(query)
    return cursor.fetchall()


# Update operations
def update_narrative(conn, narrative_id, narrative_name, sphere_tracker):
    """Update the name of a narrative record."""
    cursor = conn.cursor()
    query = '''
        UPDATE Narratives
        SET NarrativeName, SphereTracker = ?
        WHERE NarrativeID = ?
    '''
    cursor.execute(query, (narrative_name, sphere_tracker, narrative_id))
    conn.commit()
    return cursor.rowcount  # Number of rows updated


# Delete operations
def delete_narrative(conn, narrative_id):
    """Delete a narrative record by NarrativeID."""
    cursor = conn.cursor()
    query = '''
        DELETE FROM Narratives
        WHERE NarrativeID = ?
    '''
    cursor.execute(query, (narrative_id,))
    conn.commit()
    return cursor.rowcount  # Number of rows deleted

## TEAMS##

# Create operations
def create_team(conn, team_name, narrative_id):
    """Insert a new team record."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO Teams (TeamName, NarrativeID)
        VALUES (?, ?)
    '''
    cursor.execute(query, (team_name, narrative_id))
    conn.commit()
    return cursor.lastrowid  # Return the newly created TeamID


# Read operations
def get_team_by_id(conn, team_id):
    """Retrieve a specific team record by TeamID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Teams
        WHERE TeamID = ?
    '''
    cursor.execute(query, (team_id,))
    return cursor.fetchone()


def get_all_teams(conn):
    """Retrieve all team records."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Teams
    '''
    cursor.execute(query)
    return cursor.fetchall()


def get_teams_by_narrative(conn, narrative_id):
    """Retrieve all teams associated with a specific NarrativeID."""
    with conn:  # Ensures the connection stays active
        cursor = conn.cursor()
        query = "SELECT * FROM Teams WHERE NarrativeID = ?"
        cursor.execute(query, (narrative_id,))
        results = cursor.fetchall()
        return results



# Update operations
def update_team(conn, team_id, team_name=None, narrative_id=None):
    """Update a team's details."""
    cursor = conn.cursor()
    updates = []
    params = []

    if team_name is not None:
        updates.append("TeamName = ?")
        params.append(team_name)

    if narrative_id is not None:
        updates.append("NarrativeID = ?")
        params.append(narrative_id)

    params.append(team_id)

    query = f'''
        UPDATE Teams
        SET {", ".join(updates)}
        WHERE TeamID = ?
    '''
    cursor.execute(query, tuple(params))
    conn.commit()
    return cursor.rowcount  # Number of rows updated


# Delete operations
def delete_team(conn, team_id):
    """Delete a team record by TeamID."""
    cursor = conn.cursor()
    query = '''
        DELETE FROM Teams
        WHERE TeamID = ?
    '''
    cursor.execute(query, (team_id,))
    conn.commit()
    return cursor.rowcount  # Number of rows deleted


## ITEMS ##

# Create operations
def create_item(conn, item_name, item_description, item_command, narrative_id):
    """Insert a new item record."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO Items (ItemName, ItemDescription, ItemCommand, NarrativeID)
        VALUES (?, ?, ?, ?)
    '''
    cursor.execute(query, (item_name, item_description, item_command, narrative_id))
    conn.commit()
    return cursor.lastrowid  # Return the newly created ItemID


# Read operations
def get_item_by_id(conn, item_id):
    """Retrieve a specific item record by ItemID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Items
        WHERE ItemID = ?
    '''
    cursor.execute(query, (item_id,))
    return cursor.fetchone()


def get_all_items(conn):
    """Retrieve all item records."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Items
    '''
    cursor.execute(query)
    return cursor.fetchall()


def get_items_by_narrative(conn, narrative_id):
    """Retrieve all items associated with a specific NarrativeID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Items
        WHERE NarrativeID = ?
    '''
    cursor.execute(query, (narrative_id,))
    return cursor.fetchall()


# Update operations
def update_item(conn, item_id, item_name=None, item_description=None, item_command=None, narrative_id=None):
    """Update an item record with new values."""
    cursor = conn.cursor()
    updates = []
    params = []

    if item_name is not None:
        updates.append("ItemName = ?")
        params.append(item_name)

    if item_description is not None:
        updates.append("ItemDescription = ?")
        params.append(item_description)

    if item_command is not None:
        updates.append("ItemCommand = ?")
        params.append(item_command)

    if narrative_id is not None:
        updates.append("NarrativeID = ?")
        params.append(narrative_id)

    params.append(item_id)

    query = f'''
        UPDATE Items
        SET {", ".join(updates)}
        WHERE ItemID = ?
    '''
    cursor.execute(query, tuple(params))
    conn.commit()
    return cursor.rowcount  # Number of rows updated


# Delete operations
def delete_item(conn, item_id):
    """Delete an item record by ItemID."""
    cursor = conn.cursor()
    query = '''
        DELETE FROM Items
        WHERE ItemID = ?
    '''
    cursor.execute(query, (item_id,))
    conn.commit()
    return cursor.rowcount  # Number of rows deleted

## INVENTORIES ##

# Create operations
def create_inventory(conn, team_id, item_id, amount):
    """Insert a new inventory record."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO Inventories (TeamID, ItemID, Amount)
        VALUES (?, ?, ?)
    '''
    cursor.execute(query, (team_id, item_id, amount))
    conn.commit()
    return cursor.lastrowid  # Return the newly created InventoryID


# Read operations
def get_inventory_by_id(conn, inventory_id):
    """Retrieve a specific inventory record by InventoryID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Inventories
        WHERE InventoryID = ?
    '''
    cursor.execute(query, (inventory_id,))
    return cursor.fetchone()


def get_all_inventories(conn):
    """Retrieve all inventory records."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Inventories
    '''
    cursor.execute(query)
    return cursor.fetchall()


def get_inventories_by_team(conn, team_id):
    """
    Retrieve inventory details including item information for a specific team.
    """
    cursor = conn.cursor()
    query = f"""
        SELECT InventoryID, Items.ItemName, Items.ItemDescription, Items.ItemCommand, Inventories.Amount, Inventories.Used, Items.ItemID
        FROM Inventories
        JOIN Items ON Inventories.ItemID = Items.ItemID
        WHERE Inventories.TeamID = {team_id}
    """
    cursor.execute(query)
    return cursor.fetchall()


# Update operations
def update_inventory_amount(conn, inventory_id, new_amount, original_amount):
    """Update the amount of an inventory record."""
    cursor = conn.cursor()
    if new_amount <= 0:
        new_amount = 0
    if(original_amount > new_amount):
        used = original_amount - new_amount
        update_query = '''
            UPDATE Inventories
            SET Amount = ?,
                Used = Used + ?
            WHERE InventoryID = ?
        '''
        cursor.execute(update_query, (new_amount, used, inventory_id))
    else:
        update_query = '''
            UPDATE Inventories
            SET Amount = ?
            WHERE InventoryID = ?
        '''
        cursor.execute(update_query, (new_amount, inventory_id))

    conn.commit()
    return "Updated"


# Delete operations
def delete_inventory(conn, inventory_id):
    """Delete an inventory record by InventoryID."""
    cursor = conn.cursor()
    query = '''
        DELETE FROM Inventories
        WHERE InventoryID = ?
    '''
    cursor.execute(query, (inventory_id,))
    conn.commit()
    return cursor.rowcount  # Number of rows deleted

# Create operation
def create_player_slot(conn, slot_name, team_id):
    """Insert a new player slot record."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO PlayerSlots (SlotName, TeamID)
        VALUES (?, ?)
    '''
    cursor.execute(query, (slot_name, team_id))
    conn.commit()
    return cursor.lastrowid  # Return the newly created SlotID

# Read operations
def get_player_slot_by_id(conn, slot_id):
    """Retrieve a specific player slot by SlotID."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM PlayerSlots
        WHERE SlotID = ?
    '''
    cursor.execute(query, (slot_id,))
    return cursor.fetchone()

def get_all_player_slots(conn):
    """Retrieve all player slots."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM PlayerSlots
    '''
    cursor.execute(query)
    return cursor.fetchall()

def get_player_slots_by_team(conn, team_id):
    """Retrieve all player slots for a specific team."""
    cursor = conn.cursor()
    query = '''
        SELECT * FROM PlayerSlots
        WHERE TeamID = ?
    '''
    cursor.execute(query, (team_id,))
    return cursor.fetchall()

# Update operation
def update_player_slot(conn, slot_id, slot_name=None, team_id=None):
    """Update a player slot's details."""
    cursor = conn.cursor()
    updates = []
    params = []

    if slot_name is not None:
        updates.append("SlotName = ?")
        params.append(slot_name)

    if team_id is not None:
        updates.append("TeamID = ?")
        params.append(team_id)

    params.append(slot_id)

    query = f'''
        UPDATE PlayerSlots
        SET {', '.join(updates)}
        WHERE SlotID = ?
    '''
    cursor.execute(query, tuple(params))
    conn.commit()
    return cursor.rowcount  # Number of rows updated

# Delete operation
def delete_player_slot(conn, slot_id):
    """Delete a player slot by SlotID."""
    cursor = conn.cursor()
    query = '''
        DELETE FROM PlayerSlots
        WHERE SlotID = ?
    '''
    cursor.execute(query, (slot_id,))
    conn.commit()
    return cursor.rowcount  # Number of rows deleted
