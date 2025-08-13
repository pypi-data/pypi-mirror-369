import json
import os
import questionary
from emoji import emojize
from time import sleep

DATA_DIR = os.path.join(os.path.expanduser("~"), ".goals_app")
os.makedirs(DATA_DIR, exist_ok=True)
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")

msg = emojize('Welcome to your Goals app! 😁 \nHere you can create, list, mark and delete your goals!',)
goals=[]

def load_goals():
    """This function load all the goals existing, gathering the global goals.
    load_goals will try to open the goals.json and the loads these goals.
    The Exception will raise as goals being a empty tuple, if the file doesn't exist or cannot be read"""
    global goals
    try:
        ## Open the goals.json file in read mode with UTF-8 encoding to load existing goal data
        with open("goals.json","r",encoding="utf-8") as f:
            goals=json.load(f)
    except Exception:
        goals=[]

def save_goals():
    """This function save the goals in the goals.json. """
    #Open the goals.json file in write mode with UTF-8 encoding to load existing goal data
    with open("goals.json","w",encoding="utf-8") as f:
        json.dump(goals, f, ensure_ascii=False, indent=2)   # Save the goals to the file in a nicely formatted way, keeping special characters  

def create_goals():
    """This function create a goal typed by the user, by using the questionary.text (instead of simple input).
    The goal can't be empty, that's why have a if not goal, showing a message for the user and returning.
    If the user typed their goal, it'll append the goal in the global goals(that's our goals.json)"""
    global msg
    # Prompt the user to enter a new goal using a text input dialog
    goal= questionary.text('Type the goal you want to create: ').ask()
    if not goal:
        msg = "The goal can't be empty"
        sleep(1)
        return
    goals.append({"value":goal, "checkend":False})  # Store the goal in the list and mark it as not completed yet
    msg = "Goal created with success!"

def list_goals():
    """This function list all the goals registered in the goals.json. Also, you can select your goals by marking the as finished,
    or unmarked them as opened again. If there are no goals, it'll show to the user and return it.
    The user can select and mark the goals because of the questionary.checkbox. 
    In case the user mark or do not mark any goal, it will prompt the msg accordingly ('No goal selected' if not answers,
    'Goals selected as finished' if the user mark one or more of the goals) """
    global msg
    if not goals:
        msg = "There are no existing goals currently"
        sleep(1)
        return
    choices = [questionary.Choice(g['value'], checked=g['checkend'])  # Create a list of choices for the checkbox prompt, marking each goal as checked or unchecked based on its status
               for g in goals]
    answers = questionary.checkbox(
        "Use the arrows to change the goal, spacebar to mark or unmark the goal, and the Enter to finalize this process",
        choices=choices
    ).ask()   # Display a checkbox prompt allowing the user to select or deselect goals; returns the list of selected goals
    for g in goals:
        g['checkend'] = False
    if not answers:
        msg = "No goal selected"
        sleep(1)
        return
    for a in answers:
        for g in goals:
            if g['value'] == a:    
                g['checkend'] = True ## Mark each selected goal as completed by setting its 'checkend' flag to True
    msg = "Goal(s) selected as finished!"

def finished_goals():
    """This function shows all the finished goals (marked by the user).
    It'll show messages for the users in case that are no goals at all or if there are no finished goals at the moment."""
    global msg
    if not goals:
        msg = "Doesn't exist goals currently"
        sleep(1)
        return
    finished = [g for g in goals if g['checkend']]   # Create a list of all goals that have been marked as completed
    if not finished:
        msg = "Doesn't exist finished goals at moment! =("
        sleep(1)
        return
    questionary.select(
        f"Finished goals: {len(finished)}", 
        choices=[g['value'] for g in finished] 
    ).ask() ## Prompt the user to select one of the completed goals

def open_goals():
    """This function shows all the goals opened (created and unmarked by the user)
    Similar to finished_goals function, this one will show messages for the user in case that are no goals currently or if there are no 
    open goals currently."""
    global msg
    if not goals:
        msg = "Doesn't exist goals currently"
        sleep(1)
        return
    open = [g for g in goals if not g['checkend']]  # Create a list of goals that are still in progress
    if not open:
        msg = "Doesn't exist open goals at the moment =("
        sleep(1)
        return
    questionary.select(
        f"Open Goals: {len(open)}",
        choices=[g['value'] for g in open] #
    ).ask() # Prompt the user to select one of the open (unfinished) goals

def delete_goals():
    """This function can delete all the existing goals (open or finished), by erasing the goal from the goals.json.
    Similar to open_goals and finished_goals, this function will prompt messages for the user in case if there are no goals currently.
    It'll also prompt a message if there are no goals selected to delete.
    TO delete, the function is using the questionary.checkbox to mark the goals the user wants to delete."""
    global msg, goals
    if not goals:
        msg = "Doesn't exist goals currently"
        sleep(1)
        return
    choices = [g['value'] for g in goals] #Get the value of every goal, regardless of completion status
    delete_item= questionary.checkbox(
        "Select the goal that you want to delete: ",
        choices=choices
    ).ask()
    if not delete_item:
        msg = "No goals selected to delete"
        sleep(1)
        return
    goals = [g for g in goals if g['value'] not in delete_item]  # Remove goals whose value is listed in delete_item
    msg = "Goal(s) deleted with success! "

def show_msg():
    """This function as the function to show the messages for the user, getting the right message during the code.
    Instead of using several print statements, it'll use a global message, that will be showed to the user, and redefined to a empty string ' ',
    when then showed again when the variable is redefined by the code. """
    os.system('clear')
    global msg
    if msg:
        print(f"\033[31m{msg}\033[0m")
        print('')
        msg = ''

def main():
    """This function represents the main function, gathering all the functions together to make the Menu.
    Firstly, it load the goals. Them it has a infinite loop in the while True, that's our Menu, showing message and saving the goals,
    and after this, we have a questionary.select to show all the options that the user can selected, and each option redirect the user 
    for the correct function.
    To redirect the user for this, it is used if and elif functions to address the option to the function.
    The program only finishes if the user select to Exit the program, then breaking the while True loop."""
    load_goals()
    while True:
        show_msg()
        save_goals()
        option = questionary.select(
            "Menu > ",
            choices = [
                emojize("Create goal 🚀"),
                emojize("List goals 📚"),
                emojize("Finished goals ✅"),
                emojize("Open goals ⏳"),
                emojize("Delete goal😵"),
                emojize("Exit the program👋")
            ]
        ).ask()
        print(f"Selected option: {option}") 
        if option == emojize("Create goal 🚀"):
            create_goals()
        elif option == emojize("List goals 📚"):
            list_goals()
        elif option == emojize("Finished goals ✅"):
            finished_goals()
        elif option == emojize("Open goals ⏳"):
            open_goals()
        elif option == emojize("Delete goal😵"):
            delete_goals()
        elif option == emojize("Exit the program👋"):
            with open("goals.json","w", encoding="utf-8") as f:  
                json.dump([],f, ensure_ascii=False, indent=2)    # Overwrite goals.json with an empty list to clear all saved goals
            print("See you soon! " \
            "\nThank you! Merci! Obrigado! ")
            break

if __name__ == "__main__":   # Run the following code only if this script is executed directly
    main()


