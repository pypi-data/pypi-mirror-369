🎯 Goals App
Welcome to the Goals App — a simple, interactive command-line tool to help you manage your personal goals with ease. Create, list, mark as finished, and delete goals using a friendly interface powered by questionary and emoji-enhanced prompts.

📦 Features
- 🚀 Create new goals
- 📚 List all goals
- ✅ Mark goals as finished
- ⏳ View open (unfinished) goals
- 🗑️ Delete selected goals
- 💾 Persistent storage via goals.json
- 😁 Emoji-enhanced user experience

🛠️ Installation
Before running the app, make sure you have Python 3 installed. Then, install the required dependencies:
pip install questionary emoji


▶️ Usage
Run the app from your terminal:
>python app.py


You'll be greeted with a menu where you can:
- Create a goal
- List and mark goals as finished
- View finished or open goals
- Delete goals
- Exit the program
All goals are saved in a local goals.json file, so your progress is preserved between sessions.


📁 File Structure
app.py       # Main application script
goals.json         # Stores your goals persistently
README.md          # Project documentation


📚 Code Overview
- load_goals() – Loads goals from goals.json
- save_goals() – Saves current goals to file
- create_goals() – Adds a new goal
- list_goals() – Lists and allows marking goals as finished
- finished_goals() – Displays completed goals
- open_goals() – Displays goals still in progress
- delete_goals() – Deletes selected goals
- show_msg() – Displays status messages
- main() – Runs the interactive menu loop


🧪 Example
Menu >
❯ Create goal 🚀
  List goals 📚
  Finished goals ✅
  Open goals ⏳
  Delete goal😵
  Exit the program👋


📄 License
This project is open-source and free to use. Feel free to modify and share it!
