import time
import json
import os
from collections import defaultdict

class GameTracker:
    def __init__(self):
        self.data_file = "game_time.json"
        self.current_game = None
        self.start_time = None
        self.usage = defaultdict(lambda: defaultdict(float))
        self.load_data()
        
        # Optimized game detection list (case-insensitive)
        self.game_keywords = {
            'steam', 'hl2', 'csgo', 'dota', 'fortnite', 
            'overwatch', 'valorant', 'league', 'minecraft',
            'battle.net', 'origin', 'ubisoft', 'riot', 'ea',
            'wow', 'diablo', 'elden', 'gta', 'rockstar',
            'warframe', 'destiny', 'apex', 'fallout', 'skyrim'
        }

    def load_data(self):
        """Load existing game time data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for date, games in data.items():
                        for game, duration in games.items():
                            self.usage[date][game] = duration
            except json.JSONDecodeError:
                print("⚠️ Corrupted data file - starting fresh")
            except Exception as e:
                print(f"⚠️ Error loading data: {e}")

    def save_data(self):
        """Save game time data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.usage, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save data: {e}")

    def get_active_window(self):
        """Windows-only window title detection"""
        try:
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except ImportError:
            print("❌ pywin32 not installed - run 'pip install pywin32'")
            return None
        except Exception:
            return None

    def is_game(self, window_title):
        """Check if window title matches known game keywords"""
        if not window_title:
            return False
        window_lower = window_title.lower()
        return any(keyword in window_lower for keyword in self.game_keywords)

    def track(self):
        """Main tracking loop"""
        print("🎮 Game Tracker started (Ctrl+C to stop)")
        print("🔍 Detecting games...")
        last_save = time.time()
        
        try:
            while True:
                current_window = self.get_active_window()
                now = time.time()
                
                if self.is_game(current_window):
                    if current_window != self.current_game:
                        # Save previous game session
                        if self.current_game and self.start_time:
                            duration = now - self.start_time
                            self.record_session(self.current_game, duration)
                        
                        # Start new game session
                        self.current_game = current_window
                        self.start_time = now
                        print(f"▶️ Tracking: {current_window}")
                else:
                    # Save current game if switching to non-game
                    if self.current_game and self.start_time:
                        duration = now - self.start_time
                        self.record_session(self.current_game, duration)
                        print(f"⏸️ Stopped tracking: {self.current_game} ({duration/60:.1f} mins)")
                        self.current_game = None
                        self.start_time = None
                
                # Auto-save every 5 minutes
                if now - last_save > 300:
                    self.save_data()
                    last_save = now
                
                time.sleep(15)  # Check every 15 seconds
                
        except KeyboardInterrupt:
            self.shutdown()

    def record_session(self, game, duration):
        """Record a gaming session"""
        date = time.strftime("%Y-%m-%d")
        self.usage[date][game] += duration

    def show_stats(self):
        """Display gaming statistics"""
        print("\n📊 Game Time Statistics")
        print("======================")
        
        total_hours = 0
        for date, games in sorted(self.usage.items(), reverse=True):
            daily_total = sum(games.values()) / 3600
            total_hours += daily_total
            print(f"\n📅 {date} ({daily_total:.1f} hours):")
            for game, duration in sorted(games.items(), key=lambda x: -x[1]):
                hours = duration / 3600
                print(f"  ▸ {game}: {hours:.1f}h")
        
        print(f"\n⏳ Total tracked: {total_hours:.1f} hours")

    def shutdown(self):
        """Cleanup before exiting"""
        if self.current_game and self.start_time:
            duration = time.time() - self.start_time
            self.record_session(self.current_game, duration)
        self.save_data()
        self.show_stats()
        print("\n🛑 Game Tracker stopped")

if __name__ == "__main__":
    tracker = GameTracker()
    tracker.track()
