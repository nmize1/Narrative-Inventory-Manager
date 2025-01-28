import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import random
from datetime import *
import sys
sys.path.append("../Shared")
from StoredProcedures import *
from SphereTrackerCrawler import *


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
nim_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Shared/NIM.db"))

@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@bot.tree.command(name="list")
async def list(interaction: discord.Interaction):
    conn = connect_to_db(nim_db_path)

    user_roles = [role.name for role in interaction.user.roles]
    teams = get_all_teams(conn)
    team_names = {team[1]: team[0] for team in teams}

    matching_team = None
    for role_name in user_roles:
        if role_name in team_names:
            matching_team = (role_name, team_names[role_name])
            break

    if matching_team is None:
        await interaction.response.send_message("No matching team found for your roles.", ephemeral=True)
        conn.close()
        return

    team_name, team_id = matching_team
    inventory = get_inventories_by_team(conn, team_id)

    if not inventory:
        ret = f"Team **{team_name}** has an empty inventory."
    else:
        inventory_list = "\n".join(
            [f"{item[1]} (x{item[4]})" for item in inventory]
        )  # Format: ItemName (xAmount)
        ret = f"**Inventory for House {team_name}:**\n{inventory_list}"

    await interaction.response.send_message(ret)

@bot.tree.command(name="use")
async def use(interaction: discord.Interaction, item_name: str, amount: int = 1):
    conn = connect_to_db(nim_db_path)

    user_roles = [role.name for role in interaction.user.roles]
    teams = get_all_teams(conn)
    team_names = {team[1]: team[0] for team in teams}

    matching_team = None
    for role_name in user_roles:
        if role_name in team_names:
            matching_team = (role_name, team_names[role_name])
            break

    if matching_team is None:
        await interaction.response.send_message("No matching team found for your roles.", ephemeral=True)
        conn.close()
        return

    team_name, team_id = matching_team
    inventory = get_inventories_by_team(conn, team_id)
    item = next((i for i in inventory if i[1].lower() == item_name.lower()), None)

    if not item:
        response = f"Item **{item_name}** not found in the inventory of team **{team_name}**."
        await interaction.response.send_message(response, ephemeral=True)
        conn.close()
        return
    elif item[4] < amount:
        response = f"Not enough of **{item_name}** in the inventory. Only {item[4]} available."
    else:
        item_command = item[3]
        if item_command == "none":
            response = f"Used {amount} of **{item_name}**."
            await interaction.response.send_message(response)
        else:
            admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
            if not admin_role:
                await interaction.response.send_message("Admin role not found. Please ensure an Admin role exists.", ephemeral=True)
                conn.close()
                return

            response = await interaction.response.send_message(
                f"Used {amount} of **{item_name}**.",
                allowed_mentions=discord.AllowedMentions(roles=True)
            )

            followup = await interaction.followup.send(f"Waiting for an {admin_role.mention} to confirm `{item_command}` with a ✅ reaction.")

            expected_reaction = "✅"
            await followup.add_reaction(expected_reaction)

            def check(reaction, user):
                return (
                    reaction.message.id == followup.id and
                    str(reaction.emoji) == expected_reaction and
                    any(role.name.lower() == "admin" for role in user.roles)
                )

            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=86400.00, check=check)
                await interaction.followup.send(f"Admin {user.name} confirmed `{item_command}`.")

                # AP command logic here

            except asyncio.TimeoutError:
                await interaction.followup.send("No Admin reacted in time. Action canceled.")

    # Update the inventory (subtract the used amount)
    new_amount = item[4] - amount
    update_inventory_amount(conn, item[0], new_amount)

    await interaction.followup.send(f"**{item_name}** remaining: {new_amount}.")
    conn.close()

@bot.tree.command(name="add")
async def add(interaction: discord.Interaction, item_name: str, team_list: str, add_amount: int = 1, narrative: int = 1):
    if not any(role.name.lower() == "admin" for role in interaction.user.roles):
        await interaction.response.send_message("Only Admins can add items to team inventories.")
        return

    conn = connect_to_db(nim_db_path)
    teams = [team.strip() for team in team_list.split(",")]

    all_teams = get_teams_by_narrative(conn, narrative)
    team_name_to_id = {team[1]: team[0] for team in all_teams}

    unmatched_teams = []
    for team in teams:
        if team not in team_name_to_id:
            unmatched_teams.append(team)

    if unmatched_teams:
        await interaction.response.send_message(
            f"The following teams were not found in the database: {', '.join(unmatched_teams)}.",
            ephemeral=True
        )
        conn.close()
        return

    await interaction.response.defer()

    for team_name in teams:
        team_id = team_name_to_id[team_name]

        items_in_narrative = get_items_by_narrative(conn, narrative)
        matching_item_in_narrative = next((item for item in items_in_narrative if item[1].lower() == item_name.lower()), None)

        if not matching_item_in_narrative:
            await interaction.followup.send(f"Item **{item_name}** does not exist in the narrative with ID {narrative}.", ephemeral=True)
            continue
        item_id = matching_item_in_narrative[0]
        existing_items = get_inventories_by_team(conn, team_id)
        matching_item = next((item for item in existing_items if item[1].lower() == item_name.lower()), None)

        if matching_item:
            new_amount = matching_item[4] + add_amount
        else:
            create_item(conn, item_name=item_name, item_description="Automatically added item", item_command="none", narrative_id=None)
            item_id = get_item_by_id(conn, item_name)
            create_inventory(conn, team_id=team_id, item_id=item_id, amount=add_amount)

    await interaction.followup.send(f"Item **{item_name}** has been added to the inventories of the following teams: {', '.join(teams)}.")

    conn.close()

@bot.tree.command(name="remove")
async def remove(interaction: discord.Interaction, item_name: str, team_list: str, remove_amount: int = 1, narrative: int = 1):
    if not any(role.name.lower() == "admin" for role in interaction.user.roles):
        await interaction.response.send_message("Only Admins can remove items from team inventories.")
        return

    conn = connect_to_db(nim_db_path)
    teams = [team.strip() for team in team_list.split(",")]

    all_teams = get_teams_by_narrative(conn, narrative)
    team_name_to_id = {team[1]: team[0] for team in all_teams}

    unmatched_teams = []
    for team in teams:
        if team not in team_name_to_id:
            unmatched_teams.append(team)

    if unmatched_teams:
        await interaction.response.send_message(
            f"The following teams were not found in the database: {', '.join(unmatched_teams)}.",
            ephemeral=True
        )
        conn.close()
        return

    await interaction.response.defer()

    for team_name in teams:
        team_id = team_name_to_id[team_name]

        items_in_narrative = get_items_by_narrative(conn, narrative)
        matching_item_in_narrative = next((item for item in items_in_narrative if item[1].lower() == item_name.lower()), None)

        if not matching_item_in_narrative:
            await interaction.followup.send(f"Item **{item_name}** does not exist in the narrative with ID {narrative}.", ephemeral=True)
            continue

        existing_items = get_inventories_by_team(conn, team_id)
        matching_item = next((item for item in existing_items if item[1].lower() == item_name.lower()), None)

        if matching_item:
            current_amount = matching_item[4]
            if remove_amount >= current_amount:
                delete_inventory(conn, matching_item[0])
                await interaction.followup.send(f"Item **{item_name}** has been fully removed from Team **{team_name}**.")
            else:
                new_amount = current_amount - remove_amount
                update_inventory_amount(conn, matching_item[0], new_amount)
                await interaction.followup.send(f"Item **{item_name}** in Team **{team_name}** reduced by {remove_amount}. Remaining: {new_amount}.")
        else:
            await interaction.followup.send(f"Item **{item_name}** does not exist in Team **{team_name}**'s inventory.", ephemeral=True)

    await interaction.followup.send(f"Removal process completed for **{item_name}** in the specified teams.")

    conn.close()

@bot.tree.command(name="update_totals")
async def update_totals(interaction: discord.Interaction, narrative_id: int = 1):
    conn = connect_to_db(nim_db_path)
    narrative = get_narrative_by_id(conn, narrative_id)
    if not narrative:
        await interaction.response.send_message(f"Narrative with ID {narrative_id} not found.")
        return

    await interaction.response.defer()
    await shared_update_totals(narrative)
    await interaction.followup.send(f"Totals updated for narrative {narrative[1]}.")

@bot.tree.command(name="list_historic")
async def list_historic(interaction: discord.Interaction, admin: bool = False, narrative_id: int = 1):
    conn = connect_to_db(nim_db_path)
    if admin:
        if not any(role.name.lower() == "admin" for role in interaction.user.roles):
            await interaction.response.send_message("Only Admins can use list_historic with admin = True.")
            return
        await interaction.response.send_message("Admin Historic List")
        teams = get_teams_by_narrative(conn, narrative_id)
        team_names = {team[1]: team[0] for team in teams}

        for team_name, team_id in team_names.items():
            inventory = get_inventories_by_team(conn, team_id)

            if not inventory:
                ret = f"Team **{team_name}** has an empty inventory."
            else:
                inventory_list = "\n".join(
                    [f"{item[1]}: Total:{item[4] + item[5]} | Current:{item[4]} | Used:{item[5]})" for item in inventory]
                )  # Format: ItemName (xAmount)
                ret = f"**Inventory for House {team_name}:**\n{inventory_list}"
            await interaction.followup.send(ret)
    else:
        user_roles = [role.name for role in interaction.user.roles]
        teams = get_all_teams(conn)
        team_names = {team[1]: team[0] for team in teams}

        matching_team = None
        for role_name in user_roles:
            if role_name in team_names:
                matching_team = (role_name, team_names[role_name])
                break

        if matching_team is None:
            await interaction.response.send_message("No matching team found for your roles.", ephemeral=True)
            conn.close()
            return

        team_name, team_id = matching_team
        inventory = get_inventories_by_team(conn, team_id)
        if not inventory:
            ret = f"Team **{team_name}** has an empty inventory."
        else:
            inventory_list = "\n".join(
                [f"{item[1]}: Total:{item[4] + item[5]} | Current:{item[4]} | Used:{item[5]})" for item in inventory]
            )  # Format: ItemName (xAmount)
            ret = f"**Inventory for House {team_name}:**\n{inventory_list}"

        await interaction.response.send_message(ret)

bot.run('xxxx')
