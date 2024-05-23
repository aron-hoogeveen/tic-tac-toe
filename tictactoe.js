const playerTick = ["x", "o"]


function createBoard() {
    const board = document.getElementById("board")
    redrawBoard(board)
    return board
}


function redrawBoard(board) {
    let children = []
    for (let row = 0; row < 3; row++) {
        const rowElement = document.createElement("div")
        rowElement.className = "row"

        for (let column = 0; column < 3; column++) {
            const boxElement = document.createElement("div")
            boxElement.className = "box"
            boxElement.dataset.row = row
            boxElement.dataset.column = column

            rowElement.appendChild(boxElement)
        }

        children.push(rowElement)
    }
    board.replaceChildren(...children)
}


function playMove(board, player, row, column) {
    // TODO perform checks

    const rowElement = board.querySelectorAll(".row")[row]
    const boxElement = rowElement.querySelectorAll(".box")[column]
    boxElement.textContent = playerTick[player - 1]
}


export { playMove, createBoard, redrawBoard }
