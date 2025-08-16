import datetime
import random
import sys
import json
import os
from game_data import *


def get_valid_input(prompt, valid_options, case_sensitive=False):
    """Get valid input from user with error handling"""
    while True:
        choice = input(prompt).strip()
        if not case_sensitive:
            choice = choice.lower()
        if choice in valid_options:
            return choice
        print(f"Please choose from: {', '.join(valid_options)}")

def confirm_purchase(item, price):
    """Confirm purchase with user"""
    if price > 0:
        return get_valid_input(f"Buy {item.title()} for {price} gold? (y/n): ", ['y', 'n']) == 'y'
    else:
        return get_valid_input(f"Take {item.title()} and gain {abs(price)} gold? (y/n): ", ['y', 'n']) == 'y'

def show_atmosphere(time_of_day, weather):
    """Display atmospheric description"""
    print("\n" + "="*50)
    
    if time_of_day == "morning":
        print(" The morning sun casts long shadows across the cobblestones. Birds chirp in the distance.")
    elif time_of_day == "afternoon":
        print(" The afternoon sun beats down warmly. The village bustles with activity.")
    elif time_of_day == "evening":
        print(" The evening air carries the scent of cooking fires. Lanterns begin to flicker on.")
    elif time_of_day == "night":
        print(" The night is quiet except for distant tavern laughter. Stars twinkle overhead.")
    
    # Weather description
    weather_descriptions = {
        "clear": "The sky is clear and bright.",
        "cloudy": "Gray clouds gather overhead, casting shadows.",
        "rainy": "Light rain patters on the rooftops and cobblestones.",
        "foggy": "A thick fog rolls through the streets, muffling sounds."
    }
    print(f"Weather: {weather_descriptions.get(weather, 'The weather is uncertain.')}")
    print("="*50)

def show_main_menu(gold, cart_size, days_passed, german_arrival_day, quests_completed):
    """Display main menu with clear formatting"""
    days_left = german_arrival_day - days_passed
    
    print(f"\n{'='*20} MAIN MENU {'='*20}")
    print(f" Gold: {gold}")
    print(f" Items: {cart_size}")
    print(f" Day: {days_passed + 1}")
    print(f" German Arrival: {days_left} days")
    print(f" Quests Completed: {quests_completed}")
    print("-" * 48)
    print("i.   Check Inventory")
    print("s.   Visit Shops")
    print("b.   Battle Germanic Tribes")
    if days_passed >= 3:
        print("r.   Raid German Camp")
    print("save.  Save Game")
    print("q.   Quit Game")
    print("="*48)

def show_inventory(gold, cart, completed_quests):
    """Display detailed inventory"""
    print(f"\n{'='*20} INVENTORY {'='*20}")
    print(f" Gold: {gold}")
    print("-" * 44)
    
    if not cart:
        print(" No items in inventory")
    else:
        print(" Current Items:")
        for i, item in enumerate(cart, 1):
            description = ITEM_DESCRIPTIONS.get(item, "A mysterious item")
            print(f"  {i}. {item.title()}")
            print(f"     └─ {description}")
    
    print("-" * 44)
    print(f" Completed Quests: {len(completed_quests)}")
    if completed_quests:
        print("Recent completions:")
        for quest in completed_quests[-3:]:  # Show last 3
            print(f"  • {quest.title()}")
    
    print("="*44)
    input("Press Enter to continue...")

def advance_time(current_time):
    """Advance time of day"""
    time_sequence = ["morning", "afternoon", "evening", "night"]
    current_index = time_sequence.index(current_time)
    return time_sequence[(current_index + 1) % 4]

def save_game(player_name, gold, cart, completed_quests, days_passed, time_of_day, weather, german_arrival_day):
    """Save game state to file"""
    save_data = {
        'player_name': player_name,
        'gold': gold,
        'cart': cart,
        'completed_quests': completed_quests,
        'days_passed': days_passed,
        'time_of_day': time_of_day,
        'weather': weather,
        'german_arrival_day': german_arrival_day,
        'timestamp': str(datetime.datetime.now())
    }
    
    try:
        with open('savegame.json', 'w') as f:
            json.dump(save_data, f, indent=2)
        print("  Game saved successfully!")
    except Exception as e:
        print(f"  Error saving game: {e}")

def load_game():
    """Load game state from file"""
    try:
        with open('savegame.json', 'r') as f:
            save_data = json.load(f)
        print("  Game loaded successfully!")
        return save_data
    except Exception as e:
        print(f"  Error loading game: {e}")
        return None

def handle_death_alternatives(cart, player_name):
    """Handle death with healing alternatives"""
    print(f"\n  Sir {player_name} has fallen in battle!")
    print("But wait...")
    
    # Check for healing potion
    if 'healing potion' in cart:
        choice = get_valid_input("Use healing potion to revive? (y/n): ", ['y', 'n'])
        if choice == 'y':
            cart.remove('healing potion')
            print("  The healing potion restores you to life!")
            print("You barely escaped death... but you live to fight another day.")
            return True
    
    # Check for mage
    if 'mage' in cart:
        choice = get_valid_input("Have your mage cast revival magic? (y/n): ", ['y', 'n'])
        if choice == 'y':
            print(" Your mage weaves powerful magic, pulling your soul back from the brink!")
            print("'Death is but a doorway, and I hold the key!' declares your mage.")
            return True
    
    # Check for grim reaper
    if 'grim reaper' in cart:
        choice = get_valid_input("Ask the Grim Reaper to spare you? (y/n): ", ['y', 'n'])
        if choice == 'y':
            print("  The Grim Reaper looks upon you with hollow eyes...")
            print("'You amuse me, mortal. I shall grant you... one more chance.'")
            print("Death himself has given you another chance!")
            return True
    
    # No alternatives available
    print("  With no way to cheat death, your adventure ends here...")
    print("DEATH ENDING: Your heroic attempt will be remembered in village songs.")
    return False

def handle_german_raid(cart, player_name):
    """Handle raiding the German camp"""
    print(f"\n{'='*20} GERMAN CAMP RAID {'='*20}")
    print("You sneak through the forest toward the German encampment...")
    print("Firelight flickers between the trees ahead.")
    
    approach = get_valid_input(
        "How do you approach? (stealth/direct/distraction): ", 
        ['stealth', 'direct', 'distraction']
    )
    
    success_chance = 0.6  # Base 60% success
    
    # Modify chances based on items
    if 'black knight' in cart:
        success_chance += 0.2
        print("The Black Knight's armor gleams in the moonlight, inspiring confidence!")
    if 'mage' in cart:
        success_chance += 0.15
        print("Your mage weaves concealment spells around your party!")
    if 'grim reaper' in cart:
        success_chance += 0.25
        print("Death itself walks beside you - the Germans sense supernatural dread!")
    
    # Approach modifiers
    if approach == 'stealth':
        success_chance += 0.1
        print("You move like shadows through the forest...")
    elif approach == 'direct':
        success_chance -= 0.1
        print("You charge boldly toward their camp!")
    else:  # distraction
        print("You create noise on the far side of camp to draw guards away...")
    
    if random.random() < success_chance:
        print(" SUCCESS! You successfully raid the German supply wagons!")
        print("You steal their siege weapons and scatter their horses!")
        print("The confused Germans will need time to regroup.")
        return 'victory'
    else:
        print("The raid goes wrong! German sentries spot you!")
        print("You're overwhelmed by enemy warriors!")
        return 'death'

def handle_final_battle(cart, player_name, completed_quests, days_passed):
    """Handle the final battle sequence"""
    print(f"\n{'='*15} FINAL BATTLE {'='*15}")
    print("The Germanic warband storms toward the village gates!")
    print("This is your moment of truth, Sir {player_name}!")
    
    # Determine ending based on preparation
    battle_power = calculate_battle_power(cart, completed_quests, days_passed)
    
    if battle_power >= 10:
        return epic_victory_ending(cart, player_name, battle_power)
    elif battle_power >= 7:
        return heroic_victory_ending(cart, player_name, battle_power)
    elif battle_power >= 4:
        return close_victory_ending(cart, player_name, battle_power)
    else:
        return tragic_ending(cart, player_name, battle_power)

def calculate_battle_power(cart, completed_quests, days_passed):
    """Calculate total battle effectiveness"""
    power = 0
    
    # Ally power
    ally_power = {
        'brian': 2, 'black knight': 3, 'grim reaper': 5, 'god': 6,
        'mage': 4, 'nordic': 3, 'biccus diccus': 4, 'raddragonore': 5
    }
    
    for ally in ally_power:
        if ally in cart:
            power += ally_power[ally]
    
    # Equipment power
    equipment_power = {
        'spear': 1, 'axe': 2, 'scythe': 3, 'catapult': 2,
        'body armor': 2, 'dragon': 4, 'wolf': 1
    }
    
    for equipment in equipment_power:
        if equipment in cart:
            power += equipment_power[equipment]
    
    # Quest bonus (preparation matters)
    power += len(completed_quests) // 3
    
    # Time bonus/penalty
    if days_passed < 5:
        power += 1  # Well prepared
    elif days_passed > 8:
        power -= 1  # Rushed
    
    return power

# Battle ending functions
def epic_victory_ending(cart, player_name, power):
    print(f"\n EPIC VICTORY! (Power: {power})")
    
    if 'god' in cart:
        print("GOD himself fights beside you!")
        print("Divine light blinds the German forces as heavenly power flows through you!")
    elif 'grim reaper' in cart:
        print("Death incarnate reaps the souls of your enemies!")
        print("The German warriors flee in supernatural terror!")
    elif 'raddragonore' in cart:
        print("Mythical dragons soar overhead, raining fire upon the invaders!")
    
    print(f"\nSir {player_name}, your legendary victory echoes across all kingdoms!")
    print("Elena rushes to your arms as the village celebrates your triumph!")
    print("You are crowned as the new Lord Protector of the realm!")
    print("\n LEGENDARY ENDING: Your name will be sung for generations! ✨")
    return True

def heroic_victory_ending(cart, player_name, power):
    print(f"\n HEROIC VICTORY! (Power: {power})")
    print("Your well-prepared forces clash with the Germans in epic battle!")
    print("Though the fight is fierce, your superior strategy wins the day!")
    print(f"\nSir {player_name}, you have saved the village and won Elena's heart!")
    print("The grateful villagers build a statue in your honor!")
    print("\n HEROIC ENDING: You are remembered as the village's greatest champion!")
    return True

def close_victory_ending(cart, player_name, power):
    print(f"\n NARROW VICTORY! (Power: {power})")
    print("The battle is desperate and bloody, with victory hanging by a thread!")
    print("Just when all seems lost, your determination turns the tide!")
    print(f"\nSir {player_name}, you barely saved the village, but at great cost...")
    print("Elena tends your wounds as the village slowly rebuilds.")
    print("\n SURVIVOR ENDING: You proved that courage conquers all!")
    return True

def tragic_ending(cart, player_name, power):
    print(f"\n  TRAGIC DEFEAT... (Power: {power})")
    print("Despite your brave efforts, you were simply not prepared enough...")
    print("The Germans overwhelm your meager forces!")
    
    # Check for death alternatives one last time
    death_handled = handle_death_alternatives(cart, player_name)
    if not death_handled:
        print(f"\nSir {player_name}'s valiant sacrifice will always be remembered...")
        print("Though the village falls, your courage inspired others to eventually fight back.")
        print("\n MARTYR ENDING: Your noble death sparked a rebellion that would free the land.")
    return True

