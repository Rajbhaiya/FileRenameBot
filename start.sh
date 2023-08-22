echo "Running..."
git pull -f -q 
pip3 install --no-cache-dir -r requirements.txt
python3 bot.py
