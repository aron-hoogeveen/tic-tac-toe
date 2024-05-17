# HelloWebsockets - Tic Tac Toe

The design.

## Application

The game will run in a 'main' loop. There is also a 'connection' loop which handles new incoming
connections.

### Use Case

#### New Players

 - **Initial**: There are currently no players connected. 
   
   **Event**: A new player connects (a new websocket is opened). Then two more players connect.

   **Action**: The handler for the websocket signals the 'game' loop that a new player has connected.
   The websocket is added to the game. The game then signals all connected player's websockets that a
   new player has connected, and how many players still need to connect. If the second player connects,
   the same thing happens. The 'game' loop signals the players that the game has started and awaits
   turns. When the third websocket is created, the player list is already full and the
   socket is replied to with a message that the game is already full (the socket is then closed).

#### A player disconnects

 - **Initial**: There are two players playing an active game.
   
   **Event**: Player two disconnects.

   **Action**: The 'game' loop is signalled that player two disconnected. The game loop signals player one that the other player disconnected. The game is reset and waits for a new player.

## Communication

See file 'normal_game.wsd' for a sequence diagram.

### JSON formats

#### Server outgoing:

```json
{
    "type": "move_made",
    "content": {
        "next_player": 2,
        "row": 0,
        "column": 0
    }
}
```

```json
{
    "type": "winning_move",
    "content": {
        "winner": "Draw"
    }
}
```

```json
{
    "type": "error",
    "content": {
        "msg": "Illegal move! 2,0 is already occupied."
    }
}
```

```json
{
    "type": "error",
    "content": {
        "msg": "It is not your turn!"
    }
}
```

```json
{
    "type": "error",
    "content": {
        "msg": "3,0 is not a legit location to put your mark..."
    }
}
```

```json
{
    "type": "error",
    "content": {
        "msg": "The game has already ended! You can start a new game if you wish."
    }
}
```

```json
{
    "type": "new_game"
}
```

```json
{
    "type": "waiting_for_players",
    "content": {
        "connected": "player_1"
    }
}
```

```json
{
    "type": "game_start",
}
```

```json
{
    "type": "game_full",
    "content": {
        "msg": "The game is already full."
    }
}
```

#### Server Incoming

```json
{
    "type": "make_move",
    "content": {
        "row": 2,
        "column": 1
    }
}
```

```json
{
    "type": "new_game",
}
```