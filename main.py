"""
If one of two players disconnects, the game should end as soon as possible for both players.
It may be the case that the game is waiting for a message of player 1, during which player 2 disconnects.
The server should now cancel the waiting of player 1 and inform that player 2 disconnected and then delete the game.
"""

import asyncio
import websockets
from tictactoe import TicTacToe
import json
import my_logger
from my_logger import info_log
import secrets


"""
{
    "token_identifier": [
        "game": TicTacToe(),
        "players": [
            p1_websocket,
            p2_websocket
        ],
        "tasks": [
            asyncio.Task,  # game_turn_loop() for player 1
            asyncio.Task   # game_turn_loop() for player 2
        ]
    ]
}
"""
GAMES = {}


async def start_game(websocket):
    """Start a new game.
    
    This also makes this websocket Player 1.
    """
    game = TicTacToe()
    players = [websocket]
    token = secrets.token_urlsafe(10)
    GAMES[token] = {
        "game": game, 
        "players": players
    }

    info_log(id=f"GAME({token})", msg="Player 1 connected to game.")

    # send the user the connection token for the new game
    try:
        event = {
            "type": "new_game",
            "content": {
                "token": token
            }
        }
        await websocket.send(json.dumps(event))

        await game_turn_loop(token, 1)
        # try:
        #     task = asyncio.create_task(game_turn_loop(token, 1))
        #     GAMES[token]["tasks"] = [task]
        # finally:
        #     # try to inform both players that the game is stopped.
        #     event = {
        #         "type": "game_stopped",
        #         "content": {
        #             "msg": "The game stopped. Player 1 not available."
        #         }
        #     }
        #     await send_to_players(event, players)
    finally:
        del GAMES[token]
        # raise


async def join_game(websocket, token: str):
    """Join an existing game as Player 2.
    
    The token for connecting is generated in method start_game()
    """
    # make sure the game exists
    game_dict = GAMES.get(token)
    if game_dict is None:
        try:
            await send_error(websocket, "Invalid token.")
        finally:
            return

    players = game_dict["players"]

    # Player 2 can only join a game where there is only a Player 1
    if len(players) != 1:
        try:
            print(GAMES[token])
            await send_error(websocket, "This game is already full.")
        finally:
            return

    # add Player 2 to the game
    players.append(websocket)
    info_log(id=f"GAME({token})", msg="Player 2 connected to game.")

    # start the game for both players
    try:
        event = {
            "type": "game_started"
        }
        await send_to_players(event, players)
    except Exception as e:
        info_log(msg=f"An error happened while trying to start the game: {e}.")
        return

    try:
        await game_turn_loop(token, 2)  # TODO this await must be canceled when Player 1 disconnects for some reason
    except Exception:
        del GAMES[token]
        raise


async def game_turn_loop(token: str, player: int):
    """Perform a turn for the player.

    Returns when the game has ended.
    """
    while True:
        try:
            event = json.loads(await GAMES[token]["players"][player-1].recv())
            # are we still waiting for player 2?
            if len(GAMES[token]["players"]) != 2:
                await send_error(GAMES[token]["players"][player-1], "Waiting for Player 2 to connect.")
                continue
            event_type = event.get("type")
            if event_type is None:
                await send_error(GAMES[token]["players"][player-1], "Malformed request.")
                continue
            if event_type != "make_move":
                await send_error(GAMES[token]["players"][player-1], "Illegal request. Please send your move.")
                continue
            
            # make sure it is the turn of this player
            if GAMES[token]["game"].current_player != player:
                await send_error(GAMES[token]["players"][player-1], "It is not your turn!")
                continue

            field_check = await ensure_content_fields(GAMES[token]["players"][player-1], event, "row", "column")  # this also sends back the error to the user
            if not field_check:
                # TODO refactor ensure_content_fields() to not send the error, but send it here. The same happens in all the other checks
                continue

            tup = GAMES[token]["game"].make_move(event["content"]["row"], event["content"]["column"])
            if tup is None:
                await send_error(GAMES[token]["players"][player-1], "Illegal move.")
                continue
            row, column, game_end = tup

            if game_end:
                # inform the players of the ending of the game. Also send along the winning move
                winner_text = ["Draw", "Player 1", "Player 2"]
                end_event = {
                    "type": "game_end",
                    "content": {
                        "winner": winner_text[GAMES[token]["game"].winner],
                        "player": player,
                        "row": row,
                        "column": column
                    }
                }
                await send_to_players(end_event, GAMES[token]["players"])
                GAMES[token]["game"].reset()  # allow the players to play again using the same token
                continue
            else:
                move_event = {
                    "type": "move_made",
                    "content": {
                        "player": player,
                        "row": row,
                        "column": column
                    }
                }
                await send_to_players(move_event, GAMES[token]["players"])
        except websockets.ConnectionClosedOK:
            event = {
                "type": "game_stopped",
                "content": {
                    "msg": "The other player disconnected."
                }
            }
            await send_to_players(event, GAMES[token]["players"])
            return
        except Exception as e:
            info_log(msg=f"An unexpected error occurred: {e}")
            event = {
                "type": "game_stopped",
                "content": {
                    "msg": "The game stopped."
                }
            }
            await send_to_players(event, GAMES[token]["players"])
            raise


async def ensure_content_fields(websocket: websockets.WebSocketServerProtocol, event: dict, *fields: str) -> bool:
    """Ensure that all the fields are in the received event.
    
    Returns True if all fields are present."""
    content = event.get("content")
    if content is None:
        await send_error(websocket, "content")
        return False

    err_fields = []
    for field in fields:
        f = content.get(field)
        if f is None:
            err_fields.append(field)
    if len(err_fields) != 0:
        err_str = ','.join(err_fields)
        await send_error(websocket, err_str)
        return False
    
    return True


async def send_error(websocket, msg: str):
    """Send the error msg to the websocket."""
    event = {
        "type": "error",
        "content": {
            "msg": msg
        }
    }
    await websocket.send(json.dumps(event))


async def send_to_players(event: dict, players: list[websockets.WebSocketServerProtocol]):
    """Send the event to all players"""
    for player in players:
        try:
            await player.send(json.dumps(event))
        except Exception:
            pass


async def handler(websocket):
    """TicTacToe Websocket handler.
    
    This server only supports two players and a single game. Whoever connects first will be
    player_1, and the next person will be player_2. If one of the two players disconnects, the game
    will end prematurely.

    Player_1 uses crosses ('x') and player_2 uses circles ('o') to tick off a box.
    """
    info_log(msg=f"New client: {websocket.id}")
    try:
        # first message must be of type "new_game" or "join_game"
        event = json.loads(await websocket.recv())
        event_type = event.get("type")
        if (event_type == "new_game"):
            await start_game(websocket)
        elif (event_type == "join_game"):
            await ensure_content_fields(websocket, event, "token")
            await join_game(websocket, event["content"]["token"])
        # else just wait for another message
    finally:
        info_log(msg=f"Client {websocket.id} disconnected.")


async def websockets_main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == '__main__':
    my_logger.setup()
    asyncio.run(websockets_main())
    
