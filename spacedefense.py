import asyncio

async def main():
    from spacedefense.game import AsyncSpaceDefense
    await AsyncSpaceDefense().start_game()


if __name__ == "__main__":
    asyncio.run(main())