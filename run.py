import asyncio
import sys
from src.bot import main

if __name__ == "__main__":
    try:
        # Windows specific event loop policy
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("EduBot stopped")