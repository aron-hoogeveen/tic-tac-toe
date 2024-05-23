import asyncio
import logging
import websockets
from tictactoe import TicTacToe
import json
import secrets
from logformatter import MyLoggerFormatter


# initialize our own custom logging
logger = logging.getLogger(__name__)
logger_level = logging.INFO
logger.setLevel(logger_level)
ch = logging.StreamHandler()
ch.setLevel(logger_level)
ch.setFormatter(MyLoggerFormatter())
logger.addHandler(ch)


"""
{
    "token": [
        "game": TicTacToe(),
        "players": [
            p1_websocket,
            p2_websocket
        ],
        "tasks": {
            asyncio.Task,  # game_turn_loop() for player 1
            asyncio.Task   # game_turn_loop() for player 2
        }
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
        "players": players,
        "tasks": set()
    }

    logger.info(f"({token}) - Player 1 connected to game.")

    # send the user the connection token for the new game
    try:
        event = {
            "type": "new_game",
            "content": {
                "token": token
            }
        }
        await websocket.send(json.dumps(event))

        try:
            # start a new task for the game. This enables cancelling of the game via that task
            task = asyncio.create_task(game_turn_loop(token, 1))
            GAMES[token]["tasks"].add(task)
            task.add_done_callback(GAMES[token]["tasks"].discard)
            await task  # actually wait for the main game loop to finish before returning
        except asyncio.CancelledError:
            # The other player has disconnected and the game was stopped.
            try:
                event = {
                    "type": "game_stopped",
                    "content": {
                        "msg": "The other player has disconnected."
                    }
                }
                await websocket.send(json.dumps(event))
            except websockets.ConnectionClosedOK:
                pass  # the already ended, so it is no problem if player 1 now disconnects
            except Exception as e:
                logger.error(f"There was an unexpected exception: {e}.")
        except Exception:
            # Player 1 disconnected, or there was another error. Either way, the game cannot continue so inform player 2
            # first remove the task correcponding to player 1 from the set, then cancel player 2's task
            logger.info(f"({token}) - Player 1 disconnected.")
            GAMES[token]["tasks"].discard(task)
            for task in GAMES[token]["tasks"]:  # actually, there 'should' only be 1 task now so we could use set.pop()
                task.cancel()
    finally:
        del GAMES[token]
        logger.debug(f"Game with token '{token}' has been deleted.")


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
            await send_error(websocket, "This game is already full.")
        finally:
            return

    # add Player 2 to the game
    players.append(websocket)
    logger.info(f"({token}) - Player 2 connected to game.")

    try:
        # start the game for both players
        event_player_1 = {
            "type": "game_started",
            "content": {
                "player": 1
            }
        }
        event_player_2 = {
            "type": "game_started",
            "content": {
                "player": 2
            }
        }
        await players[0].send(json.dumps(event_player_1))
        await players[1].send(json.dumps(event_player_2))

        # enter the main game loop
        task = asyncio.create_task(game_turn_loop(token, 2))
        GAMES[token]["tasks"].add(task)
        task.add_done_callback(GAMES[token]["tasks"].discard)
        await task  # actually wait for the main game loop to finish
    except asyncio.CancelledError:
        # The other player has disconnected and the game was stopped.
        try:
            stop_event = {
                "type": "game_stopped",
                "content": {
                    "msg": "The other player has disconnected."
                }
            }
            await websocket.send(json.dumps(stop_event))
        except Exception as e:
            logger.error(msg=f"There was an unexpected exception: {e}.")
    except Exception:
        # Player 2 disconnected, or there was another error. Either way, the game cannot continue so inform player 1
        # first remove the task correcponding to player 2 from the set, then cancel player 1's task
        logger.info(f"GAME({token}) - Player 2 disconnected.")
        GAMES[token]["tasks"].discard(task)
        for task in GAMES[token]["tasks"]:
            task.cancel()


async def game_turn_loop(token: str, player: int):
    """Perform a turn for the player.

    Returns when the game has ended.
    """
    while True:
        try:
            logger.debug(f"({token}) - GAMES: {GAMES}")  # check if games are not influenced by each other

            websocket = GAMES[token]["players"][player-1]
            game = GAMES[token]["game"]
            players = GAMES[token]["players"]

            event = json.loads(await websocket.recv())
            # are we still waiting for player 2?
            if len(players) != 2:
                await send_error(websocket, "Waiting for Player 2 to connect.")
                continue
            event_type = event.get("type")
            if event_type is None:
                await send_error(websocket, "Malformed request.")
                continue
            if event_type != "make_move":
                # TODO the player might want to start a new game during an activate game.
                await send_error(websocket, "Illegal request. Please send your move.")
                continue
            
            # make sure it is the turn of this player
            if game.current_player != player:
                await send_error(websocket, "It is not your turn!")
                continue

            field_check = await ensure_content_fields(websocket, event, "row", "column")  # this also sends back the error to the user
            if not field_check:
                # TODO refactor ensure_content_fields() to not send the error, but send it here. The same happens in all the other checks
                continue

            tup = game.make_move(event["content"]["row"], event["content"]["column"])
            if tup is None:
                await send_error(websocket, "Illegal move.")
                continue
            row, column, game_end = tup

            if game_end:
                # inform the players of the ending of the game. Also send along the winning move
                winner_text = ["Draw", "Player 1", "Player 2"]
                end_event = {
                    "type": "game_end",
                    "content": {
                        "winner": winner_text[game.winner],
                        "player": player,
                        "row": row,
                        "column": column
                    }
                }
                await send_to_players(end_event, players)
                game.reset()  # allow the players to play again using the same token
                logger.debug(f"The game({token}) has been reset. New state: {GAMES[token]}.")
            else:
                move_event = {
                    "type": "move_made",
                    "content": {
                        "player": player,
                        "row": row,
                        "column": column
                    }
                }
                await send_to_players(move_event, players)
            logger.debug(f"End of game loop: {{token: {token}, GAMES:{GAMES[token]}}}")
        except websockets.ConnectionClosedOK as e:
            raise e  # the exception is handled higher up the chain
        except Exception as e:
            logger.error(msg=f"An unexpected error occurred: {e}")
            raise e


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
            if player is not None:
                await player.send(json.dumps(event))
        except Exception:
            pass


async def handler(websocket):
    """TicTacToe Websocket handler."""
    logger.debug(f"New client: {websocket.id}")
    try:
        while True:
            # first message must be of type "new_game" or "join_game"
            event = json.loads(await websocket.recv())
            event_type = event.get("type")
            if (event_type == "new_game"):
                await start_game(websocket)
            elif (event_type == "join_game"):
                await ensure_content_fields(websocket, event, "token")
                await join_game(websocket, event["content"]["token"])
            # else just wait for another message
    except websockets.ConnectionClosedOK:
        pass
    except Exception as e:
        logger.error(f"There was an uncaught exception: {e}.")
    finally:
        logger.debug(f"Client {websocket.id} disconnected.")


async def websockets_main():
    logger.info("Starting server")
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(websockets_main())
    
