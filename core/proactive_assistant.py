import asyncio
import time

class ProactiveAssistant:
    def __init__(self):
        self.active = True
        self.last_consolidation = time.time()
        
    async def monitor_and_suggest(self):
        """Background task that monitors context and occasionally offers suggestions."""
        while self.active:
            await asyncio.sleep(3600) # Check every hour
            
            # Idle Consolidation check (e.g. every 7 days)
            # For testing/demonstration, we can set this threshold to 7 days in seconds (604800)
            if time.time() - self.last_consolidation > 604800:
                print("🧹 [Idle Period Detected: Running automatic Memory Consolidation]")
                from memory.consolidation import MemoryConsolidator
                consolidator = MemoryConsolidator()
                consolidator.run_full_consolidation()
                self.last_consolidation = time.time()
                
            print("💡 [Proactive Assistant]: Have you considered reviewing your active project milestones today?")
            
    def start(self):
        asyncio.create_task(self.monitor_and_suggest())
