import { playMove, createBoard, redrawBoard } from "./tictactoe.js"


let websocket
let gameFinished = false


window.addEventListener("DOMContentLoaded", () => {
    // Initialize the UI
    // TODO refactor and initialize UI via a createBoard() method from the import.
    // const board = document.getElementById("board")
    const board = createBoard()
    const newGameButton = document.getElementById("new_game")
    const joinGameButton = document.getElementById("join_game")

    // Initialize the websocket 
    websocket = new WebSocket("ws://localhost:8001/")
    sendMoves(board, websocket)
    receiveMoves(board, websocket)

    newGameButton.onclick = startGame
    joinGameButton.onclick = joinGame
})


function startGame() {
    const event = {
        type: "new_game"
    }
    websocket.send(JSON.stringify(event))
}


function joinGame() {
    const tokenInput = document.getElementById("token_input")
    const event = {
        type: "join_game",
        content: {
            token: tokenInput.value
        }
    }
    websocket.send(JSON.stringify(event))
}


function receiveMoves(board, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        console.debug("Message received: " + data)

        let event = JSON.parse(data)
        switch (event.type) {
            case "new_game":
                const token = event.content.token
                console.log("New game. Token: '" + token + "'")
                // display the token
                const tokenElement = document.getElementById("token")
                tokenElement.textContent = "'" + token + "'"
                // TODO clear the board
                setNotification("Waiting for Player 2.")
                break;

            case "game_started":
                setNotification("The game has started!")
                break

            case "move_made":
                // if the game was finished, first redraw the board
                if (gameFinished) {
                    gameFinished = false
                    redrawBoard(board)
                    setNotification("New game has started!")
                }
                playMove(board, event.content.player, event.content.row, event.content.column)
                break;

            case "game_end":
                playMove(board, event.content.player, event.content.row, event.content.column)
                setNotification("The game has ended! Winner: " + event.content.winner)
                gameFinished = true
                break

            case "game_stopped":
                setNotification("The game was stopped: " + event.content.msg)
                break

            case "error":
                setNotification("Error: " + event.content.msg)
                break;

            default:
                console.log("unknown event type: " + event.type)
        }
    })
}


function sendMoves(board, websocket) {
    // event listener for clicking on boxes
    board.addEventListener("click", ({ target }) => {
        const row = target.dataset.row
        const column = target.dataset.column

        // make sure that the click was inside a box
        if (column === undefined || row === undefined) {
            return
        }

        // if a previous game was finished, redraw the board first
        if (gameFinished) {
            redrawBoard(board)
            gameFinished = false
        }

        const event = {
            type: "make_move",
            content: {
                row: parseInt(row),
                column: parseInt(column)
            }
        }
        console.log("Sending following data: " + JSON.stringify(event))
        websocket.send(JSON.stringify(event))
    })
}


function setNotification(msg) {
    const notificationElement = document.getElementById("notification")
    notificationElement.textContent = msg
}
