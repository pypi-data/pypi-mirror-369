# PLEASE ENTER 
# 'cls'
# 'python -W ignore Terminal_Speil_Main.py'

# TO RUN THE FILE,
# THANKS, BASANTA

import json
import random
import datetime
import os
import sys
from utils import *
from game_data import *

def clear_terminal():
    """Clears the terminal screen."""
    if os.name == 'nt':  # Check if the operating system is Windows
        os.system('cls')
    else:  # Assume Unix-like system
        os.system('clear')

def handle_shop_selection(gold, cart, completed_quests, player_name):
    """Handle shop selection and purchases"""
    result = {
        'gold': gold,
        'cart': cart.copy(),
        'completed_quests': completed_quests.copy(),
        'game_ended': False
    }
    
    # Make copies of shop inventories so we can modify them
    shops = {
        'freelancers': FREELANCERS.copy(),
        'antiques': ANTIQUES.copy(),
        'pet_shop': PET_SHOP.copy(),
        'grocery': GROCERY.copy(),
        'botanical_nursery': BOTANICAL_NURSERY.copy(),
        'farmers_market': FARMERS_MARKET.copy()
    }
    
    shop_loop = True
    while shop_loop and not result['game_ended']:
        print(f"\n=== VILLAGE SHOPS ===")
        print("1. Freelancers")
        print("2. Antiques")
        print("3. Pet Shop")
        print("4. Grocery")
        print("5. Botanical Nursery")
        print("6. Farmers Market")
        print("7. Quest Board")
        print("back. Return to Main Menu")
        
        shop_choice = get_valid_input("Which shop? (1-7 or 'back'): ", ['1', '2', '3', '4', '5', '6', '7', 'back'])
        
        if shop_choice == 'back':
            shop_loop = False
            continue
            
        elif shop_choice == '1':
            # FREELANCERS SHOP
            freelancer_result = handle_freelancers_guild(result['gold'], result['cart'], shops['freelancers'], player_name)
            result.update(freelancer_result)
            if result['game_ended']:
                break
                
        elif shop_choice == '2':
            # ANTIQUE SHOP
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['antiques'], 
                "ANTIQUE SHOP", 
                "Dust motes dance in the filtered sunlight. Ancient treasures gleam mysteriously."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '3':
            # PET SHOP
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['pet_shop'],
                "PET SHOP",
                "The air fills with chirping, squeaking, and the rustle of small creatures."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '4':
            # GROCERY STORE
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['grocery'],
                "GROCERY",
                "The aroma of fresh bread and pungent cheese and aged wine fills your nostrils."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '5':
            # BOTANICAL NURSERY
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['botanical_nursery'],
                "BOTANICAL NURSERY",
                "Sweet floral scents and rich earth surround you."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '6':
            # FARMERS MARKET
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['farmers_market'],
                "FARMERS MARKET", 
                "Fresh produce is arranged in colorful displays."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '7':
            # QUEST BOARD
            quest_result = handle_quest_board(result['gold'], result['completed_quests'])
            result['gold'] = quest_result['gold']
            result['completed_quests'] = quest_result['completed_quests']
    
    return result

def handle_freelancers_guild(gold, cart, freelancers_shop, player_name):
    """Handle the freelancers guild with special battle mechanics"""
    result = {
        'gold': gold,
        'cart': cart.copy(),
        'game_ended': False
    }
    
    print("\n--- Entering Freelancers ---")
    print("\n=== FREELANCERS GUILD ===")
    print("The guild hall echoes with the sounds of sharpening weapons and hushed conversations.")
    
    if not freelancers_shop:
        print("The guild is empty! All freelancers are out on missions.")
        input("Press Enter to continue...")
        return result
    
    print("\nAvailable Freelancers:")
    for name, price in freelancers_shop.items():
        if price == 'dedication and hope':
            print(f"- {name.title()}: Requires dedication and hope")
        else:
            print(f"- {name.title()}: {price} gold")
    
    freelancer_options = list(freelancers_shop.keys()) + ['exit']
    freelancer_choice = get_valid_input("Select a freelancer or 'exit': ", freelancer_options)
    
    if freelancer_choice == 'exit':
        return result
    
    # Process freelancer choice
    price = freelancers_shop[freelancer_choice]
    
    # Handle special cases
    if freelancer_choice == 'minstrel':
        print(f"You hired the minstrel... but he killed and looted you!")
        print("YOU DIED! Thanks for playing.")
        result['game_ended'] = True
        return result
        
    elif freelancer_choice == 'ze germane':
        print(f"You hired ze germane... but he betrayed you immediately!")
        print("YOU DIED! Thanks for playing.")
        result['game_ended'] = True
        return result
        
    elif freelancer_choice == 'god':
        dedication_choice = get_valid_input("Do you have true dedication and hope in your heart? (yes/no): ", ['yes', 'no'])
        if dedication_choice == 'no':
            print("God sees through your lack of faith...")
            input("Press Enter to continue...")
            return result
        else:
            print("God recognizes your pure heart!")
            result['cart'].append(freelancer_choice)
            freelancers_shop.pop(freelancer_choice)
    
    else:
        # Normal purchase
        if isinstance(price, int) and result['gold'] >= price:
            confirm = get_valid_input(f"Hire {freelancer_choice.title()} for {price} gold? (y/n): ", ['y', 'n'])
            if confirm == 'y':
                result['gold'] -= price
                result['cart'].append(freelancer_choice)
                freelancers_shop.pop(freelancer_choice)
                print(f"You hired {freelancer_choice.title()}!")
        else:
            print("Not enough gold!")
            input("Press Enter to continue...")
            return result
    
    # Offer immediate battle option for hired freelancers
    if freelancer_choice in result['cart'] and freelancer_choice not in ['minstrel', 'ze germane']:
        battle_choice = get_valid_input("Ready for battle with your new ally? (yes/no/inventory): ", ['yes', 'no', 'inventory'])
        
        if battle_choice == 'inventory':
            show_inventory(result['gold'], result['cart'], [])
        elif battle_choice == 'yes':
            result['game_ended'] = handle_freelancer_battle(freelancer_choice, player_name)
    
    input("Press Enter to continue...")
    return result

def handle_freelancer_battle(freelancer_name, player_name):
    """Handle immediate battle with hired freelancer"""
    print(f"\n=== BATTLE BEGINS ===")
    
    if freelancer_name == 'brian':
        print("You used Brian as a meatshield... using the element of surprise!")
        print("You defeated ze germanz! You're now the village king!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'black knight':
        print("The Black Knight dies heroically in battle, winning it!")
        print("You revive him with your healing potion.")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'grim reaper':
        print("The Grim Reaper uses 'GRIM EYES' ability...")
        print("""
        ___       ___
        (_o_)     (_o_)
    . |     /\\      |.
    (   )   /  \\     (  )
    \\  /           /  /
    \\............../
        \\_____________/
        """)
        print("REAPING...............")
        print("You defeated ze germanz and became village king!")
        print("With literal death by your side you are crowned!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'god':
        print("GOD APPRECIATES JUSTICE!")
        print("GOD used 'BRIGHT EYE' ability!")
        print("""
    _,.--~=~"~=~--.._  
    _.-"  / \\ !   ! / \\  "-._  
,"     / ,`    .---. `, \\     ". 
/.'   `~  |   /:::::\\   |  ~`   '.
\\`.  `~   |  \\:::::/   | ~`  ~ .'
    `.  `~  \\ `, `~~~' ,` /   ~`.' 
    "-._   \\ / !   ! \\ /  _.-"  
        "=~~.._  _..~~=`"        
        """)
        print("You received the blessing of god!")
        print("You, the son of god have started Terminality with your followers!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'mage':
        print("Your mage fights variantly,")
        print("MAGE USES STAFF OF UROPE,")
        print("""
        ____
    /----\\.    
    ++++++===(O)[=====\\--\\=====l
    \\----/.
        """)
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'raddragonore':
        print("Bro, ya dat cool? damnn!")
        print("DRAGONORE SUMMONS HIS MYTHICAL CREATURES,")
        print("""
<>=======() 
(/\\___   /|\\\\          ()==========<>_
\\_/ | \\\\        //|\\   ______/ \\)
\\_|  \\\\      // | \\_/
    \\|\\/|\\_   //  /\\/
    (.\\/.\)\\ \\_//  /
        //_/\\_\\/ /  |
        @@//-|=\\  \\  |
        \\_=\\_  \\ |
        \\==\\ \\|\\_ 
        __(\\===\\(  )\\l
    (((~) __(_/   |
    (((~) \\  /
    ______/ /
    '------'
        """)
        print("Yo enemies are ash bro,")
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    else:
        print(f"{freelancer_name.title()} fights valiantly!")
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True

def handle_generic_shop(gold, cart, shop_inventory, shop_name, shop_description):
    """Handle generic shop purchases"""
    result = {
        'gold': gold,
        'cart': cart.copy()
    }
    
    print(f"\n--- Entering {shop_name} ---")
    print(f"\n=== {shop_name} ===")
    print(shop_description)
    
    if not shop_inventory:
        print("The shop is empty! Come back later.")
        input("Press Enter to continue...")
        return result
    
    print(f"\nAvailable items:")
    for item, price in shop_inventory.items():
        print(f"- {item.title()}: {price} gold")
    
    shop_options = list(shop_inventory.keys()) + ['exit']
    choice = get_valid_input("Select an item or 'exit': ", shop_options)
    
    if choice == 'exit':
        return result
    
    if choice in shop_inventory:
        price = shop_inventory[choice]
        
        if price > 0 and result['gold'] >= price:
            confirm = get_valid_input(f"Buy {choice} for {price} gold? (y/n): ", ['y', 'n'])
            if confirm == 'y':
                result['gold'] -= price
                result['cart'].append(choice)
                shop_inventory.pop(choice)
                print(f"You bought {choice} for {price} gold!")
                
                # Special messages
                if choice == 'magic beans':
                    print("These beans tingle with magical energy... they might grow into something amazing!")
                elif choice == 'newt':
                    print("The newt looks at you knowingly... something special about this one!")
                    
        elif price < 0:
            result['gold'] += abs(price)
            result['cart'].append(choice)
            shop_inventory.pop(choice)
            print(f"You took {choice} and gained {abs(price)} gold!")
        else:
            print("Not enough gold!")
    
    input("Press Enter to continue...")
    return result

def handle_quest_board(gold, completed_quests):
    """Handle quest board activities"""
    result = {
        'gold': gold,
        'completed_quests': completed_quests.copy()
    }
    
    print("\n--- Entering Quest Board ---")
    print("\n=== VILLAGE QUEST & BOUNTY BOARD ===")
    print("The wooden board creaks in the wind, covered with parchment notices.")
    
    print("\nAvailable Village Quests:")
    quest_choices = {}
    i = 1
    for quest, details in VILLAGE_QUESTS.items():
        if quest not in result['completed_quests']:
            quest_choices[str(i)] = quest
            print(f"{i}. {quest.title()} - {details['description']} [Reward: {details['reward']} gold]")
            i += 1

    print("\nBlacksmith Jobs:")
    for j, (job, details) in enumerate(BLACKSMITH_JOBS.items(), 1):
        if job not in result['completed_quests']:
            quest_choices[f"b{j}"] = job
            print(f"b{j}. {job.title()} - {details['description']} [Reward: {details['reward']} gold]")

    print("\nTavern Activities:")
    for k, (activity, details) in enumerate(TAVERN_ACTIVITIES.items(), 1):
        if activity not in result['completed_quests']:
            quest_choices[f"t{k}"] = activity
            print(f"t{k}. {activity.title()} - {details['description']} [Reward: {details['reward']} gold]")

    valid_choices = list(quest_choices.keys()) + ['r', 'back']
    quest_choice = get_valid_input("Choose a quest, 'r' for random adventure, or 'back': ", valid_choices)

    if quest_choice == 'back':
        pass
    elif quest_choice == 'r':
        # Random event
        event = random.choice(RANDOM_EVENTS)
        print(f"\n=== RANDOM ADVENTURE ===")
        print(f"{event['event']}")
        result['gold'] += event['gold']
        print(f"You gained {event['gold']} gold!")
    else:
        # Handle quest completion
        quest_name = quest_choices[quest_choice]
        
        # Determine quest type and reward
        if quest_name in VILLAGE_QUESTS:
            reward = VILLAGE_QUESTS[quest_name]['reward']
        elif quest_name in BLACKSMITH_JOBS:
            reward = BLACKSMITH_JOBS[quest_name]['reward']
        else:
            reward = TAVERN_ACTIVITIES[quest_name]['reward']
        
        print(f"\n=== {quest_name.upper()} ===")
        
        # Quest-specific adventures
        if quest_name == 'hunt wild boar':
            approach = get_valid_input("How do you approach the boar? (stealth/direct/trap): ", ['stealth', 'direct', 'trap'])
            if approach == 'stealth':
                print("You sneak up and take the boar by surprise! Clean kill!")
                reward += 25
            elif approach == 'direct':
                print("You charge head-on! Dangerous but heroic!")
            else:
                print("You set a clever trap! The boar walks right into it!")
                reward += 15
        
        elif quest_name == 'explore haunted ruins':
            approach = get_valid_input("How do you explore the ruins? (careful/bold/mystical): ", ['careful', 'bold', 'mystical'])
            if approach == 'careful':
                print("You carefully avoid the traps and find extra treasure!")
                reward += 50
            elif approach == 'bold':
                print("You boldly march through and face the dangers head-on!")
            else:
                print("You use mystical knowledge to commune with the spirits!")
                reward += 30
        
        # Complete the quest
        print(f"Quest completed! You earned {reward} gold!")
        result['gold'] += reward
        result['completed_quests'].append(quest_name)

    input("Press Enter to continue...")
    return result

def main():
    clear_terminal()
    print("Starting Terminal Speil...")
    
    # GLOBAL VARIABLES/DEFINES
    completed_quests = []
    time_of_day = "morning"
    weather = "clear"
    gold = 10000
    cart = ["healing potion"]
    game_ended = False
    days_passed = 0
    german_arrival_day = 7
    player_name = ""
    
    # MAIN CODE
    print("=== MEDIEVAL VILLAGE DEFENSE ===")
    print("Welcome, brave hero!")

    # Check for save file
    if os.path.exists("savegame.json"):
        load_choice = get_valid_input("Found a saved game! Load it? (y/n): ", ['y', 'n'])
        if load_choice == 'y':
            try:
                save_data = load_game()
                if save_data:
                    player_name = save_data.get('player_name', '')
                    gold = save_data.get('gold', 10000)
                    cart = save_data.get('cart', ["healing potion"])
                    completed_quests = save_data.get('completed_quests', [])
                    days_passed = save_data.get('days_passed', 0)
                    time_of_day = save_data.get('time_of_day', 'morning')
                    weather = save_data.get('weather', 'clear')
                    german_arrival_day = save_data.get('german_arrival_day', 7)
                    print(f"Welcome back, Sir {player_name}!")
            except Exception as e:
                print(f"Error loading save file: {e}")
                print("Starting new game...")

    if not player_name:
        # Get start game input
        start_choice = get_valid_input("Shall we begin our adventure? (y/n): ", ['y', 'n'])
        if start_choice == 'n':
            print("Game cancelled!")
            sys.exit()

        # Get player name
        player_name = input("Enter character name: ").strip()
        if not player_name:
            player_name = "Hero"

    # Show current time
    current_hour = datetime.datetime.now().hour
    current_time = datetime.datetime.now()
    print(f"Adventure continues at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Set time_of_day based on real time if starting new game
    if days_passed == 0:
        if current_hour < 6:
            time_of_day = "night"
        elif current_hour < 12:
            time_of_day = "morning" 
        elif current_hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

    # Show intro
    print(f"""
=== MEDIEVAL VILLAGE DEFENSE ===

Sir {player_name}!
Your village is under attack by a Germanic tribe! 
You must gather allies, weapons, and supplies to defend your home.
The fate of your village (and that special someone) depends on you!

Current Status: Day {days_passed + 1}, {time_of_day.title()}, {weather} weather
Time until German arrival: {german_arrival_day - days_passed} days
Ze germanz are approaching... time is running out!
    """)

    # Main game loop
    while not game_ended:
        # Check if Germans have arrived
        if days_passed >= german_arrival_day:
            print("\nThe Germanic warband has arrived at the village gates!")
            print("You must face them now or all is lost!")
            
            battle_choice = get_valid_input("Face the Germans in battle? (yes/flee): ", ['yes', 'flee'])
            if battle_choice == 'flee':
                print("You flee the village in shame...")
                print("COWARD'S ENDING: The villagers are left to their fate.")
                print("Thanks for playing!")
                game_ended = True
                break
            else:
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
                break

        # Random events
        if random.random() < 0.3:
            event = random.choice(RANDOM_EVENTS)
            print(f"\n--- RANDOM EVENT ---")
            print(f"{event['event']}")
            gold += event['gold']
            print(f"You gained {event['gold']} gold!")
            input("Press Enter to continue...")

        # Weather changes
        if random.random() < 0.2:
            old_weather = weather
            weather = random.choice(["clear", "cloudy", "rainy", "foggy"])
            if weather != old_weather:
                print(f"\nThe weather changes to {weather}...")

        # Show atmosphere
        show_atmosphere(time_of_day, weather)
        
        # Show main menu
        show_main_menu(gold, len(cart), days_passed, german_arrival_day, len(completed_quests))
        
        # Get main menu choice
        main_choice = get_valid_input("Choose an option: ", ['i', 's', 'b', 'r', 'save', 'q'])
        
        if main_choice == 'q':
            save_choice = get_valid_input(f"Save before quitting? (y/n): ", ['y', 'n'])
            if save_choice == 'y':
                save_game(player_name, gold, cart, completed_quests, days_passed, 
                        time_of_day, weather, german_arrival_day)
            print(f"Thanks for playing, Sir {player_name}!")
            game_ended = True
            
        elif main_choice == 'save':
            save_game(player_name, gold, cart, completed_quests, days_passed, 
                    time_of_day, weather, german_arrival_day)
            print("Game saved successfully!")
            input("Press Enter to continue...")
            
        elif main_choice == 'i':
            show_inventory(gold, cart, completed_quests)
            
        elif main_choice == 'r':
            if days_passed >= 3:
                raid_result = handle_german_raid(cart, player_name)
                if raid_result == 'victory':
                    german_arrival_day += 2
                    print("Your successful raid has delayed the German attack by 2 days!")
                elif raid_result == 'death':
                    death_handled = handle_death_alternatives(cart, player_name)
                    if not death_handled:
                        game_ended = True
                        break
                days_passed += 1
            else:
                print("You need more preparation before attempting a raid! (Available after day 3)")
                input("Press Enter to continue...")
                
        elif main_choice == 'b':
            # Check battle ready
            battle_items = ['brian', 'black knight', 'grim reaper', 'god', 'mage', 'nordic', 'biccus diccus', 'raddragonore']
            battle_ready = any(item in cart for item in battle_items)
            
            if battle_ready:
                print("You decide to face the Germanic threat head-on!")
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
            else:
                print("You need allies or powerful weapons before you can battle the Germans!")
                print("Visit the Freelancers Guild or Antique Shop to prepare.")
                input("Press Enter to continue...")
                
        elif main_choice == 's':
            # Shop selection
            shop_result = handle_shop_selection(gold, cart, completed_quests, player_name)
            gold = shop_result['gold']
            cart = shop_result['cart'] 
            completed_quests = shop_result['completed_quests']
            if shop_result['game_ended']:
                game_ended = True
                break
            
            # Advance time after shopping
            time_of_day = advance_time(time_of_day)
            if time_of_day == "morning":
                days_passed += 1

if __name__ == "__main__":
    main()