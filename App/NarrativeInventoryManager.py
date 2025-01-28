import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
sys.path.append("../Shared")
from StoredProcedures import *

class NarrativeInventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Narrative Async Inventory Manager")

        # Database connection
        nim_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Shared/NIM.db"))
        self.conn = connect_to_db(nim_db_path)

        # Main Frames
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.init_narrative_screen()

    def init_narrative_screen(self):
        """Initialize the narrative selection screen."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Narrative management frame
        narrative_management_frame = ttk.Frame(self.main_frame)
        narrative_management_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(narrative_management_frame, text="Narrative Name:").grid(row=0, column=0, padx=5, pady=5)
        narrative_name_entry = ttk.Entry(narrative_management_frame)
        narrative_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Add Narrative Button
        def add_narrative():
            narrative_name = narrative_name_entry.get().strip()
            if not narrative_name:
                tk.messagebox.showerror("Error", "Narrative name is required.")
                return
            create_narrative(self.conn, narrative_name)
            refresh_narratives()
            narrative_name_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Narrative added successfully.")

        add_button = ttk.Button(narrative_management_frame, text="Add Narrative", command=add_narrative)
        add_button.grid(row=0, column=2, padx=5, pady=5)

        # Update Narrative Button
        def update_narrative_gui():
            selected = self.narrative_listbox.curselection()
            if not selected:
                tk.messagebox.showerror("Error", "No narrative selected.")
                return

            narrative_id = narratives[selected[0]][0]  # Get NarrativeID
            narrative_name = narrative_name_entry.get().strip()

            if not narrative_name:
                tk.messagebox.showerror("Error", "Narrative name is required.")
                return

            update_narrative(self.conn, narrative_id, narrative_name)
            refresh_narratives()
            narrative_name_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Narrative updated successfully.")

        update_button = ttk.Button(narrative_management_frame, text="Update Narrative", command=update_narrative_gui)
        update_button.grid(row=0, column=3, padx=5, pady=5)

        # Delete Narrative Button
        def delete_narrative_gui():
            selected = self.narrative_listbox.curselection()
            if not selected:
                tk.messagebox.showerror("Error", "No narrative selected.")
                return

            narrative_id = narratives[selected[0]][0]  # Get NarrativeID

            # Confirm deletion
            confirm = tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this narrative?")
            if confirm:
                delete_narrative(self.conn, narrative_id)
                refresh_narratives()
                narrative_name_entry.delete(0, tk.END)
                tk.messagebox.showinfo("Success", "Narrative deleted successfully.")

        delete_button = ttk.Button(narrative_management_frame, text="Delete Narrative", command=delete_narrative_gui)
        delete_button.grid(row=0, column=4, padx=5, pady=5)

        # Open Narrative Button
        def open_narrative():
            selected = self.narrative_listbox.curselection()
            if not selected:
                tk.messagebox.showerror("Error", "No narrative selected.")
                return

            narrative_id = narratives[selected[0]][0]  # Get NarrativeID
            self.init_team_screen(narrative_id)

        open_button = ttk.Button(narrative_management_frame, text="Open Narrative", command=open_narrative)
        open_button.grid(row=0, column=5, padx=5, pady=5)

        # Narrative list frame
        narrative_list_frame = ttk.Frame(self.main_frame)
        narrative_list_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ttk.Label(narrative_list_frame, text="Narratives:").pack(pady=5)
        self.narrative_listbox = tk.Listbox(narrative_list_frame, height=15)
        self.narrative_listbox.pack(fill="both", expand=True, pady=5)

        # Refresh narratives
        def refresh_narratives():
            global narratives
            self.narrative_listbox.delete(0, tk.END)
            narratives = get_all_narratives(self.conn)
            for narrative in narratives:
                self.narrative_listbox.insert(tk.END, f"{narrative[1]}")  # Add NarrativeName

        refresh_narratives()

        # Populate narrative name on selection
        def on_narrative_select():
            selected = self.narrative_listbox.curselection()
            if not selected:
                return
            narrative_name_entry.delete(0, tk.END)
            narrative_name_entry.insert(0, narratives[selected[0]][1])  # Populate NarrativeName

        self.narrative_listbox.bind("<<ListboxSelect>>", lambda event: on_narrative_select())

        # Double-click to open narrative
        def on_narrative_double_click(event):
            selected = self.narrative_listbox.curselection()
            if not selected:
                return
            narrative_id = narratives[selected[0]][0]  # Get NarrativeID
            self.init_team_screen(narrative_id)

        self.narrative_listbox.bind("<Double-1>", on_narrative_double_click)


    def load_narratives(self):
        """Load all narratives into the listbox."""
        narratives = get_all_narratives(self.conn)
        self.narrative_listbox.delete(0, tk.END)
        for narrative in narratives:
            self.narrative_listbox.insert(tk.END, f"{narrative[0]}: {narrative[1]}")

    def open_selected_narrative(self):
        """Open the selected narrative."""
        selected = self.narrative_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a narrative.")
            return

        narrative_id = int(self.narrative_listbox.get(selected[0]).split(":")[0])
        self.init_team_screen(narrative_id)

    def open_narrative(self, event):
        """Open a narrative by double-clicking."""
        self.open_selected_narrative()
        # Narrative title

    def init_team_screen(self, narrative_id):
        """Initialize the team and inventory screen for a specific narrative."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Top frame for navigation buttons
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill="x", pady=5)

        # Back button
        back_button = ttk.Button(top_frame, text="Back to Narratives", command=self.init_narrative_screen)
        back_button.pack(side="left", padx=(10, 5))

        # Items button
        items_button = ttk.Button(top_frame, text="Items", command=lambda: self.show_items(narrative_id))
        items_button.pack(side="left", padx=(5, 10))

        # Narrative title
        narrative = get_narrative_by_id(self.conn, narrative_id)
        ttk.Label(self.main_frame, text=f"{narrative[1]}", font=("Arial", 14)).pack(pady=10)

        # Frame for team management
        team_management_frame = ttk.Frame(self.main_frame)
        team_management_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(team_management_frame, text="Team Name:").grid(row=0, column=0, padx=5, pady=5)
        team_name_entry = ttk.Entry(team_management_frame)
        team_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Add Team Button
        def add_team():
            team_name = team_name_entry.get().strip()
            if not team_name:
                tk.messagebox.showerror("Error", "Team name is required.")
                return
            create_team(self.conn, team_name, narrative_id)
            refresh_teams()
            team_name_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Team added successfully.")

        add_button = ttk.Button(team_management_frame, text="Add Team", command=add_team)
        add_button.grid(row=0, column=2, padx=5, pady=5)

        # Update Team Button
        def update_team_gui():
            selected = self.team_listbox.curselection()
            if not selected:
                tk.messagebox.showerror("Error", "No team selected.")
                return

            team_id = teams[selected[0]][0]  # Get the TeamID from the teams list
            team_name = team_name_entry.get().strip()

            if not team_name:
                tk.messagebox.showerror("Error", "Team name is required.")
                return

            update_team(self.conn, team_id, team_name=team_name)
            refresh_teams()
            team_name_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Team updated successfully.")

        update_button = ttk.Button(team_management_frame, text="Update Team", command=update_team_gui)
        update_button.grid(row=0, column=3, padx=5, pady=5)

        # Delete Team Button
        def delete_team_gui():
            selected = self.team_listbox.curselection()
            if not selected:
                tk.messagebox.showerror("Error", "No team selected.")
                return

            team_id = teams[selected[0]][0]  # Get the TeamID from the teams list

            # Confirm deletion
            confirm = tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this team?")
            if confirm:
                delete_team(self.conn, team_id)
                refresh_teams()
                team_name_entry.delete(0, tk.END)
                tk.messagebox.showinfo("Success", "Team deleted successfully.")

        delete_button = ttk.Button(team_management_frame, text="Delete Team", command=delete_team_gui)
        delete_button.grid(row=0, column=4, padx=5, pady=5)

        # Frame for Teams and Inventories
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Teams frame
        team_frame = ttk.Frame(content_frame, borderwidth=2, relief="groove")
        team_frame.pack(side="left", fill="both", expand=True, padx=5)

        ttk.Label(team_frame, text="Teams:").pack(pady=5)
        self.team_listbox = tk.Listbox(team_frame, height=15, width=40)
        self.team_listbox.pack(fill="both", expand=True, pady=5)
        self.team_listbox.bind("<<ListboxSelect>>", lambda event: on_team_select())

        # Inventories frame
        inventory_frame = ttk.Frame(content_frame, borderwidth=2, relief="groove")
        inventory_frame.pack(side="right", fill="both", expand=True, padx=5)

        ttk.Label(inventory_frame, text="Inventories:").pack(pady=5)
        self.inventory_table = ttk.Treeview(inventory_frame, columns=("ID", "Name", "Description", "Command", "Amount"), show="headings", height=15)
        self.inventory_table.pack(fill="both", expand=True, pady=5)

        # Set up table headings
        self.inventory_table.column("ID", width=0, stretch=tk.NO)  # Hide the ItemID column
        self.inventory_table.heading("Name", text="Name")
        self.inventory_table.heading("Description", text="Description")
        self.inventory_table.heading("Command", text="Command")
        self.inventory_table.heading("Amount", text="Amount")

        # Refresh teams function
        def refresh_teams():
            global teams
            self.team_listbox.delete(0, tk.END)
            teams = get_teams_by_narrative(self.conn, narrative_id)
            for team in teams:
                self.team_listbox.insert(tk.END, f"{team[1]}")

        refresh_teams()

        # Populate team name on selection
        def on_team_select():
            selected = self.team_listbox.curselection()
            if not selected:
                return
            team_name_entry.delete(0, tk.END)
            team_name_entry.insert(0, teams[selected[0]][1])
            load_team_inventories()

        def load_team_inventories():
            """Load inventories for the selected team."""
            selected = self.team_listbox.curselection()
            if not selected:
                return

            team_id = teams[selected[0]][0]

            # Clear the inventory table
            for row in self.inventory_table.get_children():
                self.inventory_table.delete(row)

            # Fetch inventory data with item details
            inventories = get_inventories_by_team(self.conn, team_id)

            # Populate the inventory table
            for inventory in inventories:
                print(inventory)
                self.inventory_table.insert("", "end", values=inventory)

        # Inventory actions
        inventory_action_frame = ttk.Frame(self.main_frame)
        inventory_action_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(inventory_action_frame, text="Item:").grid(row=0, column=0, padx=5, pady=5)
        item_dropdown = ttk.Combobox(inventory_action_frame, state="readonly", width=20)
        item_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(inventory_action_frame, text="Amount to Add:").grid(row=0, column=2, padx=5, pady=5)
        add_amount_entry = ttk.Entry(inventory_action_frame, width=10)
        add_amount_entry.grid(row=0, column=3, padx=5, pady=5)

        def add_item_to_inventory():
            selected_team = self.team_listbox.curselection()
            if not selected_team:
                tk.messagebox.showerror("Error", "No team selected.")
                return

            team_id = teams[selected_team[0]][0]  # Get TeamID
            selected_item = item_dropdown.get()
            amount_to_add = add_amount_entry.get().strip()

            if not selected_item or not amount_to_add.isdigit() or int(amount_to_add) <= 0:
                tk.messagebox.showerror("Error", "Select a valid item and enter a positive amount.")
                return

            items = get_items_by_narrative(self.conn, narrative_id)
            item_id = next(item[0] for item in items if item[1] == selected_item)
            amount_to_add = int(amount_to_add)

            # Check if the item already exists in inventory
            current_inventory = get_inventories_by_team(self.conn, team_id)
            inventory_item = next((inv for inv in current_inventory if inv[0] == selected_item), None)

            if inventory_item:
                new_amount = inventory_item[3] + amount_to_add
                update_inventory_amount(self.conn, inventory_item[4], new_amount, inventory_item[3])  # Use InventoryID
            else:
                create_inventory(self.conn, team_id, item_id, amount_to_add)

            refresh_inventories(team_id)
            add_amount_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", f"Added {amount_to_add} {selected_item}(s) to inventory.")

        add_button = ttk.Button(inventory_action_frame, text="Add to Inventory", command=add_item_to_inventory)
        add_button.grid(row=0, column=4, padx=5, pady=5)

        ttk.Label(inventory_action_frame, text="Amount to Remove:").grid(row=1, column=2, padx=5, pady=5)
        remove_amount_entry = ttk.Entry(inventory_action_frame, width=10)
        remove_amount_entry.grid(row=1, column=3, padx=5, pady=5)

        def remove_item_from_inventory():
            selected_team = self.team_listbox.curselection()
            if not selected_team:
                tk.messagebox.showerror("Error", "No team selected.")
                return

            team_id = teams[selected_team[0]][0]  # Get TeamID
            selected_item = item_dropdown.get()
            amount_to_remove = remove_amount_entry.get().strip()

            if not selected_item or not amount_to_remove.isdigit() or int(amount_to_remove) <= 0:
                tk.messagebox.showerror("Error", "Select a valid item and enter a positive amount.")
                return

            items = get_items_by_narrative(self.conn, narrative_id)
            item_id = next(item[0] for item in items if item[1] == selected_item)  # Find ItemID by name
            amount_to_remove = int(amount_to_remove)

            # Check if the item exists in inventory
            current_inventory = get_inventories_by_team(self.conn, team_id)
            inventory_item = next((inv for inv in current_inventory if inv[5] == item_id), None)

            if not inventory_item:
                tk.messagebox.showerror("Error", f"{selected_item} is not in the inventory.")
                return

            new_amount = int(inventory_item[4]) - int(amount_to_remove)
            update_inventory_amount(self.conn, inventory_item[0], new_amount, inventory_item[4])

            refresh_inventories(team_id)
            remove_amount_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", f"Removed {amount_to_remove} {selected_item}(s) from inventory.")

        remove_button = ttk.Button(inventory_action_frame, text="Remove from Inventory", command=remove_item_from_inventory)
        remove_button.grid(row=1, column=4, padx=5, pady=5)

        # Refresh inventories
        def refresh_inventories(team_id):
            for row in self.inventory_table.get_children():
                self.inventory_table.delete(row)
            inventories = get_inventories_by_team(self.conn, team_id)
            for inventory in inventories:
                self.inventory_table.insert("", "end", values=inventory)

        # Populate items dropdown
        def populate_items_dropdown():
            items = get_items_by_narrative(self.conn, narrative_id)
            item_names = [item[1] for item in items]
            item_dropdown["values"] = item_names

        populate_items_dropdown()

    def load_teams(self, narrative_id):
        """Load all teams associated with the given narrative ID."""
        teams = get_teams_by_narrative(self.conn, narrative_id)

        # Clear the team listbox
        self.team_listbox.delete(0, tk.END)  # This is fine for a Listbox

        # Clear the inventory table (if applicable)
        for row in self.inventory_table.get_children():  # Correct way to clear Treeview
            self.inventory_table.delete(row)

        # Populate the team listbox
        for team in teams:
            self.team_listbox.insert(tk.END, f"{team[0]}: {team[1]}")


    def show_items(self, narrative_id):
        """Display all items associated with the narrative in a new table."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Top navigation frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill="x", pady=5)

        # Back button
        back_button = ttk.Button(top_frame, text="Back", command=lambda: self.init_team_screen(narrative_id))
        back_button.pack(side="left", padx=10)

        # Items table
        narrative = get_narrative_by_id(self.conn, narrative_id)
        items_label = ttk.Label(self.main_frame, text=f"Items in {narrative[1]}:", font=("Arial", 14))
        items_label.pack(pady=5)
        items_table = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Description", "Command"), show="headings", height=15)
        items_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Set up table headings (exclude ID from display)
        items_table.column("ID", width=0, stretch=tk.NO)  # Hide the ItemID column
        items_table.heading("Name", text="Name")
        items_table.heading("Description", text="Description")
        items_table.heading("Command", text="Command")

        # Fetch and populate item data
        items = get_items_by_narrative(self.conn, narrative_id)
        for item in items:
            items_table.insert("", "end", values=item)

        # Fetch and populate item data
        def refresh_items():
            for row in items_table.get_children():
                items_table.delete(row)
            items = get_items_by_narrative(self.conn, narrative_id)
            for item in items:
                items_table.insert("", "end", values=item)

        refresh_items()

        # Add new item form
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(form_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
        description_entry = ttk.Entry(form_frame)
        description_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Command:").grid(row=0, column=4, padx=5, pady=5)
        command_entry = ttk.Entry(form_frame)
        command_entry.grid(row=0, column=5, padx=5, pady=5)

        def add_item():
            name = name_entry.get().strip()
            description = description_entry.get().strip()
            command = command_entry.get().strip() or "none"

            if not name or not description:
                tk.messagebox.showerror("Error", "Name and description are required.")
                return

            create_item(self.conn, name, description, command, narrative_id)
            refresh_items()
            name_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)
            command_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Item added successfully.")

        add_button = ttk.Button(form_frame, text="Add Item", command=add_item)
        add_button.grid(row=0, column=6, padx=5, pady=5)

        # Update Item Function
        def update_item():
            selected = items_table.selection()
            if not selected:
                tk.messagebox.showerror("Error", "No item selected.")
                return

            values = items_table.item(selected[0], "values")
            item_id = values[0]

            name = name_entry.get().strip()
            description = description_entry.get().strip()
            command = command_entry.get().strip() or "none"

            if not name or not description:
                tk.messagebox.showerror("Error", "Name and Description are required.")
                return

            # Update the item in the database
            update_item(self.conn, item_id=item_id, item_name=name, item_description=description, item_command=command)
            refresh_items()
            name_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)
            command_entry.delete(0, tk.END)
            tk.messagebox.showinfo("Success", "Item updated successfully.")

        update_button = ttk.Button(form_frame, text="Update Item", command=update_item)
        update_button.grid(row=0, column=7, padx=5, pady=5)

        # Delete Item Function
        def delete_item_gui():
            selected = items_table.selection()
            if not selected:
                tk.messagebox.showerror("Error", "No item selected.")
                return

            values = items_table.item(selected[0], "values")
            item_id = values[0]

            # Confirm deletion
            confirm = tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
            if confirm:
                delete_item(self.conn, item_id)
                refresh_items()
                name_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)
                command_entry.delete(0, tk.END)
                tk.messagebox.showinfo("Success", "Item deleted successfully.")

        delete_button = ttk.Button(form_frame, text="Delete Item", command=delete_item_gui)
        delete_button.grid(row=0, column=8, padx=5, pady=5)

        # Populate text fields when a row is selected
        def on_row_select(event):
            selected = items_table.selection()
            if not selected:
                return

            # Get selected item's data
            values = items_table.item(selected[0], "values")
            name_entry.delete(0, tk.END)
            name_entry.insert(0, values[0])  # Name
            description_entry.delete(0, tk.END)
            description_entry.insert(0, values[1])  # Description
            command_entry.delete(0, tk.END)
            command_entry.insert(0, values[2])  # Command

        # Bind selection event to the Treeview
        items_table.bind("<<TreeviewSelect>>", on_row_select)

if __name__ == "__main__":
    # Initialize root and configure weights
    root = tk.Tk()
    root.title("Narrative Async Inventory Manager")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Create the main application
    app = NarrativeInventoryManager(root)

    # Start the application
    root.mainloop()
