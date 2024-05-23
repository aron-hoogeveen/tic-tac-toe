from copy import deepcopy


class TicTacToe:
    """TicTacToe

    What it takes:
    - a 3x3 board;
    - 2 players;
    """

    player_1 = 1
    player_2 = 2

    def __init__(self) -> None:
        self.current_player = self.player_1
        self.winner = None  # 0 -> Draw, 1 -> Player 1, 2 -> Player 2
        self._board = [[0 for _ in range(3)] for _ in range(3)]
        self._number_of_moves = 0

    def make_move(self, row: int, column: int) -> tuple[int, int, bool] | None:
        """Make a move.

        Let the current player make a move. If the (legal) move results in the game ending, the returned
        bool will be True. It will be False otherwise.

        Moves can only be made as long as there is no winner, otherwise None is returned.

        Returns:
        the move and state of the game if it was a legal move, None otherwise.
        """
        if self.winner is not None or self._is_invalid_move(row, column):
            return None

        # update the board
        self._board[row][column] = self.current_player
        self._number_of_moves += 1

        # update the winner
        self.winner = self._winner_or_draw()
        if self.winner is not None:
            return row, column, True

        # update the current_player to the next player
        self.current_player = self.current_player % 2 + 1
        return row, column, False

    def _is_invalid_move(self, row: int, column: int) -> bool:
        """Returns whether the move is an invalid move.

        The following are invalid moves:
        - when row or index are < 0 or > 2
        - when there is already a 'tick' in the box.
        """
        return (
            row < 0
            or row > 2
            or column < 0
            or column > 2
            or self._board[row][column] != 0
        )

    def _winner_or_draw(self) -> int | None:
        """Returns whether there is a winner or a draw.

        Returns:
        0 if there is a draw;
        1 if player_1 won;
        2 if player_2 won;
        None if the game is not in a final state.
        """
        # Check winning combination for R1 and C1
        if self._board[0][0] != 0:
            if (
                self._board[0][0] == self._board[0][1] == self._board[0][2]  # R1
                or self._board[0][0] == self._board[1][0] == self._board[2][0]  # C1
            ):
                # Win!
                winner = self._board[0][0]
                return winner

        # Check winning combination for R2, C2, D1 and D2
        if self._board[1][1] != 0:
            if (
                self._board[0][0] == self._board[1][1] == self._board[2][2]  # D1
                or self._board[0][2] == self._board[1][1] == self._board[2][0]  # D2
                or self._board[1][0] == self._board[1][1] == self._board[1][2]  # R2
                or self._board[0][1] == self._board[1][1] == self._board[2][1]  # C2
            ):
                # Win!
                winner = self._board[1][1]
                return winner

        # Check winning combination for R3 and C3
        if self._board[2][2] != 0:
            if (
                self._board[0][2] == self._board[1][2] == self._board[2][2]  # C3
                or self._board[2][0] == self._board[2][1] == self._board[2][2]  # R3
            ):
                # Win!
                winner = self._board[2][2]
                return winner

        if self._number_of_moves == 9:
            # Draw!
            return 0

        return None

    def reset(self) -> None:
        """Resets the game."""
        self.current_player = self.player_1
        self.winner = None
        self._board = [[0 for _ in range(0, 3)] for _ in range(0, 3)]
        self._number_of_moves = 0

    @property
    def board(self) -> list[list[int]]:
        """Returns a copy of the board."""
        return deepcopy(self._board)
    
    def __repr__(self) -> str:
        return self.board.__repr__()
