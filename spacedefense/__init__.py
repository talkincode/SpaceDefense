def runapp():
    try:
        import asyncio
        import argparse
        parser = argparse.ArgumentParser(description="Run game.")
        parser.add_argument("-D", "--debug", action="store_true", help="Run game in debug mode.")
        parser.add_argument("-t", "--train", action="store_true", help="Run game in eye train mode.")
        parser.add_argument("-l", "--level", choices=["x", "xx", "xxx"], default="x", help="Set game Level.")
        args = parser.parse_args()

        from spacedefense.game import AsyncSpaceDefense
        asyncio.run(AsyncSpaceDefense().start_game())
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

