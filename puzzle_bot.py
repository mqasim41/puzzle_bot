import pywhatkit
import requests
import os
import random
import schedule
import time
from datetime import datetime

PUZZLE_ARCHIVE = [
    {
        "image": "https://lichess1.org/export/fen.gif?fen=r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R%20w%20KQkq%20-%200%203&theme=blue&piece=merida",
        "title": "The Opera Game Mate (Paul Morphy)",
        "turn": "w",
        "fen": "4kb1r/p2n1ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 w k - 0 1"
    },
    {
        "image": "https://lichess1.org/export/fen.gif?fen=rnbqk2r/ppp2ppp/3b4/3p4/3Pn3/3B1N2/PPP2PPP/RNBQ1RK1%20b%20kq%20-%200%207&theme=blue&piece=merida",
        "title": "Queen Sacrifice (Byrne vs. Fischer, 1956)",
        "turn": "b",
        "fen": "rnbqk2r/ppp2ppp/3b4/3p4/3Pn3/3B1N2/PPP2PPP/RNBQ1RK1 b kq - 0 7"
    },
    {
        "image": "https://lichess1.org/export/fen.gif?fen=r3k2r/ppp2ppp/2n5/3q4/8/2N5/PPP2PPP/R3K2R%20w%20KQkq%20-%200%201&theme=blue&piece=merida",
        "title": "Knight Fork Tactics",
        "turn": "w",
        "fen": "r3k2r/ppp2ppp/2n5/3q4/8/2N5/PPP2PPP/R3K2R w KQkq - 0 1"
    },
    {
        "image": "https://lichess1.org/export/fen.gif?fen=2kr3r/ppp2ppp/2n5/3q4/8/2N5/PPP2PPP/R4RK1%20w%20-%20-%200%201&theme=blue&piece=merida",
        "title": "Back Rank Mate Pattern",
        "turn": "w",
        "fen": "2kr3r/ppp2ppp/2n5/3q4/8/2N5/PPP2PPP/R4RK1 w - - 0 1"
    },
    {
        "image": "https://lichess1.org/export/fen.gif?fen=r1bq1rk1/pppn1ppp/4pn2/3p4/3P4/2NBPN2/PPPQ1PPP/R3K2R%20w%20KQ%20-%200%208&theme=blue&piece=merida",
        "title": "Greek Gift Sacrifice",
        "turn": "w",
        "fen": "r1bq1rk1/pppn1ppp/4pn2/3p4/3P4/2NBPN2/PPPQ1PPP/R3K2R w KQ - 0 8"
    }
]

def send_whatsapp_message(image_path: str, caption: str, group_name: str):
    """Send image with caption to WhatsApp group using pywhatkit"""
    try:
        print(f"Sending message at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pywhatkit.sendwhats_image(
            receiver=group_name,
            img_path=image_path,
            caption=caption,
            tab_close=True,
            close_time=10
        )
        print("Message sent successfully")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def fetch_chess_puzzle() -> dict:
    """Fetch daily chess puzzle with uniqueness check"""
    used_file = "used_puzzles.txt"
    try:
        # Try Chess.com API first
        response = requests.get(
            "https://api.chess.com/pub/puzzle",
            headers={"User-Agent": "ChessClubBot/1.0"}
        )
        response.raise_for_status()
        data = response.json().get('puzzle', response.json())
        
        # Check if puzzle already used
        puzzle_id = data.get("puzzle_id", data.get("title", ""))
        if os.path.exists(used_file):
            with open(used_file, "r") as f:
                used = set(line.strip() for line in f)
                if puzzle_id in used:
                    raise ValueError("Puzzle already used")
        
        # Store used puzzle
        with open(used_file, "a") as f:
            f.write(f"{puzzle_id}\n")
            
        return data
    except Exception as e:
        print(f"Using archive: {str(e)}")
        return random.choice(PUZZLE_ARCHIVE)

def download_image(image_url: str) -> str:
    """Download image from URL to temporary file"""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        temp_file = f"temp_{datetime.now().timestamp()}.jpg"
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return temp_file
    except Exception as e:
        print(f"Image download failed: {str(e)}")
        return "fallback_image.jpg"  # Have a default image ready

def generate_caption(puzzle_data: dict) -> str:
    """Create formatted caption with current datetime"""
    timestamp = datetime.now().strftime("%A, %B %d at %I:%M %p")
    base = f"♟️ Chess Puzzle ({timestamp}) ♟️\n\n"
    base += f"Title: {puzzle_data.get('title', 'Daily Challenge')}\n"
    
    if 'fen' in puzzle_data:
        turn = "White" if puzzle_data['fen'].split()[1] == 'w' else "Black"
        base += f"Turn: {turn}\n"
        
    if 'solution' in puzzle_data:
        base += f"Solution: {' '.join(puzzle_data['solution'])}\n"
        
    base += f"URL: {puzzle_data.get('url', 'https://lichess.org/training')}"
    return base

def puzzle_job():
    """Main job to be scheduled"""
    print(f"\n{'='*40}\nRunning puzzle job at {datetime.now()}")
    try:
        puzzle = fetch_chess_puzzle()
        image_path = download_image(puzzle['image'])
        caption = generate_caption(puzzle)
        send_whatsapp_message(
            image_path=image_path,
            caption=caption,
            group_name="+923155290169"  # Replace with your group name/number
        )
        # Cleanup temporary file
        if image_path.startswith("temp_"):
            os.remove(image_path)
    except Exception as e:
        print(f"Job failed: {str(e)}")

if __name__ == "__main__":
    # Schedule daily posts
    schedule.every().day.at("01:19").do(puzzle_job)  # 9 AM
    schedule.every().day.at("15:00").do(puzzle_job)  # 3 PM
    # puzzle_job()
    print("Chess Bot Scheduler Started")
    print("Scheduled times:")
    for job in schedule.get_jobs():
        print(f"- {job.next_run.strftime('%H:%M')}")

    # Keep script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

    # For testing: Run immediately
    