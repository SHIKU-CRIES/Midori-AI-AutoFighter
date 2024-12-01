git reset --hard HEAD
git pull

# Ask the user if they want to run the updater
echo "Do you want to run the updater? (y/N)"
read answer

# If the user types "y", run the updater and then the game
if [ "$answer" == "y" ]; then
  konsole -e "bash update.sh" &
  uv run main.py
# If the user types anything else, just run the game
else
  uv run main.py
fi