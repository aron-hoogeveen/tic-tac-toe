# Online Tic-Tac-Toe writting in Python

This project was created so that I could introduce myself to websockets. The back-end side is 
written in Python and the front-end is written in html/css/js. 

## Setup

The project uses Conda for dependency management:

```sh
# run the following from within the project's root directory
conda env create
# conda env update
conda activate websockets
```

## Running the code

The websocket server can be started with:

```sh
python main.py
```

The webserver (for serving the html/css/js files) is run with:

```sh
python -m http.server
```

and can then be accessed via a webbrowser at http://localhost:8000/tictactoe.html.