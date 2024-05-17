import asyncio
import time
from tictactoe import TicTacToe


async def main_loop():
    """The main loop."""
    print_time("[Main Loop] - Start")
    game = TicTacToe()

    # run player_1 and player_2
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(player_1())
        task2 = tg.create_task(player_2())

    print_time("[Main Loop] - End")


async def player_1():
    print_time("[Player 1] - Start")
    await asyncio.sleep(0.5)
    print_time("[Player 1] - move 0,0")
    await asyncio.sleep(1)
    print_time("[Player 1] - move 1,1")
    await asyncio.sleep(1)
    print_time("[Player 1] - move 2,2")
    await asyncio.sleep(1)
    print_time("[Player 1] - End")


async def player_2():
    print_time("[Player 2] - Start")
    await asyncio.sleep(1)
    print_time("[Player 2] - move 2,0")
    await asyncio.sleep(1)
    print_time("[Player 2] - move 2,1")
    await asyncio.sleep(1)
    print_time("[Player 2] - End")


def print_time(msg: str) -> None:
    print(f"[{time.strftime('%X')}]: {msg}")


if __name__ == '__main__':
    asyncio.run(main_loop())
