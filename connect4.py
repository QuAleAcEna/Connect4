import random
import math 
import copy

ROWS = 6
COLS = 7

class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = copy.deepcopy(board)  # Copy of the board at this node
        self.player = player              # The player who made the move leading here
        self.parent = parent              # Parent node
        self.move = move                  # Move that was made to reach this node (column)
        self.children = []                # Child nodes
        self.visits = 0                   # N: number of times node was visited
        self.wins = 0                     # W: number of wins from this node
        self.untried_moves = get_valid_moves(board)  

    def ucb1(self, total_simulations, c=1.41):
        if self.visits == 0:
            return float('inf')  # Encourage exploration
        win_rate = self.wins / self.visits
        return win_rate + c * math.sqrt(math.log(total_simulations) / self.visits)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0


#========CONNECT4 GAME LOGIC=======#

def create_board():
    """Create an empty Connect 4 board."""
    return [[0] * COLS for _ in range(ROWS)]

def print_board(board):
    """Print the board in the requested format."""
    for row in board:
        print("".join("X" if cell == 1 else "O" if cell == 2 else "-" for cell in row))

def is_valid_move(board, col):
    """Check if a move is valid (column is not full)."""
    return board[0][col] == 0

def get_next_open_row(board, col):
    """Find the next available row in a column."""
    for row in range(ROWS - 1, -1, -1):  # Start from the bottom
        if board[row][col] == 0:
            return row
    return None  # Should never happen if move is valid

def drop_piece(board, row, col, piece):
    """Drop a piece into the board."""
    board[row][col] = piece

def check_winner(board, piece):
    """Check if a player has won the game."""
    # Check horizontal locations
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonals
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonals
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False

def get_valid_moves(board):
    """Return a list of valid column moves."""
    return [c for c in range(COLS) if is_valid_move(board, c)]

def get_random_move(**kwargs):
    board = kwargs.get("board")
    """Get a computer's random move"""
    return random.choice(get_valid_moves(board))

def play_game(mode="pvc", ai_strategy1=None, ai_strategy2=None,silent=False):
    board = create_board()
    game_over = False
    turn = 1  # 0 = Player 1 (X), 1 = Player 2 (O)
    first=True
    root = None  # for mcts
    if not silent:
        print_board(board)

    while not game_over:
        

        if mode == "pvp" or (mode == "pvc" and turn == 1):
            # human player
            col = None
            while col is None:
                try:
                    col = int(input(f"Player {turn} ({'X' if turn == 1 else 'O'}), choose column (0-{COLS-1}): "))
                    if col not in get_valid_moves(board):
                        print("Invalid move! Try again.")
                        col = None
                except ValueError:
                    print("Invalid input! Enter a number.")
        else:
            #criar root para cvc mcts
            if first:
                root=MCTSNode(board,turn)
                first=False
            # ai player
            ai = ai_strategy1 if turn == 1 else ai_strategy2
            if ai:
                if root:
                    col = ai(root=root,board=board)
                if not silent:
                    print(f"Computer {turn} chooses column {col}")
            else:
                raise ValueError("AI strategy not provided for computer player.")

        #play the piece
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn)
        if not silent:
            print_board(board)

        # update tree
        if root:
            # find the move played
            matching_child = next((child for child in root.children if child.move == col), None)
            if matching_child:
                root = matching_child
                root.parent = None
            else:
                root = MCTSNode(board=board, player=3 - turn)   
        if check_winner(board, turn):
            print(f"Player {turn} ({'X' if turn == 1 else 'O'}) wins!")
            return turn
        elif not get_valid_moves(board):
            print("It's a draw!")
            return 0

        turn = 3 - turn  #change turn
    return 3-turn

#======MONTE CARLO======#
#Main function
def MCTS(**kwargs):
    root = kwargs.get("root")
    iterations = kwargs.get("iterations", 1000)
    bestchild = kwargs.get("bestchild", bestchild_default)
    backprograming = kwargs.get("backprograming", backprograming_default)
    if backprograming is None:
        backprograming = backprograming_default
    if bestchild is None:
        bestchild = bestchild_default

    
    for _ in range(iterations):
        #Selection based on UCB
        node=selection(root)
        if not node.is_fully_expanded():
            child=expansion(node)
            result=simulation(child)
            backprograming(child,result)
        else:
            result=check_winner(node.board,node.player)
            backprograming(node,result)
    #return the best move based in the select critirea
    return bestchild(root).move

def selection(node: MCTSNode):
    #check if there is a winner
    while not check_winner(node.board, node.player):
        if not node.is_fully_expanded() or not node.children:
            return node
        
        node = max(node.children, key=lambda child: child.ucb1(node.visits))
        
    return node

def expansion(node: MCTSNode) ->MCTSNode:
    #get a  move 
    move=random.choice(node.untried_moves)
    node.untried_moves.remove(move)
    
    row=get_next_open_row(node.board,move)
    new_board=copy.deepcopy(node.board)
    drop_piece(new_board,row,move,3-node.player)
    #create the new node
    expanded_node=MCTSNode(board=new_board,player=3-node.player,parent=node,move=move)
    #add the new node to the children of the node
    node.children.append(expanded_node)
    return expanded_node

def simulation(node: MCTSNode) ->int:
    board=copy.deepcopy(node.board)
    player=3- node.player
    while get_valid_moves(board):
        #Simulate moves until a  winner or no more moves
        move=get_random_move(board=board)
        row=get_next_open_row(board,move)
        drop_piece(board,row,move,player)
        
        if check_winner(board,player):
            return player
        player=3-player
    return 0

def backprograming_default(node : MCTSNode,result):
    #update the nodes with the simulation result
    while node is not None:
        node.visits+=1
        if result==node.player:
            node.wins+=1
        elif result==0:
            node.wins+=0.5
        node=node.parent

def backprograming_greddy(node : MCTSNode,result):
    #update the nodes with the simulation result
    while node is not None:
        node.visits+=1
        #consider a draw as a loss
        if result==node.player:
            node.wins+=1

        node=node.parent

#find the next move based on win%
def bestchild_default(node : MCTSNode):
    return max(node.children, key=lambda child:child.wins/child.visits if child.visits > 0 else -1)

#find the next move based on visits on the node

def higherVisits(node : MCTSNode):
    return max(node.children, key=lambda child:child.visits)

#benchmark algorithms
def benchmark(strategy1, strategy2, games=100):
    mcts_wins = 0
    draws = 0
    for _ in range(games):
        winner = play_game("cvc", ai_strategy1=strategy1, ai_strategy2=strategy2, silent=True)
        if winner == 1:
            mcts_wins += 1
        elif winner == 0:
            draws += 1
    print(f"MCTS Wins: {mcts_wins}, Draws: {draws}, Random Wins: {games - mcts_wins - draws}")

# Select game mode

#play_game("pvc", MCTS,get_random_move)
#benchmark(MCTS,get_random_move,20)
#lambda **kwargs: MCTS(bestchild=higherVisits, **kwargs

while True:
    mode = input("Select mode (pvp, pvc, cvc): ").strip().lower()
    if mode in {"pvp", "pvc", "cvc"}:
        if mode =="pvp":
            play_game(mode)
            break
        elif mode=="pvc":
            adversary=input("Select a adversary (random, mcts): ").strip().lower()
            if adversary=="random":
                play_game(mode,ai_strategy=get_random_move)
                break
            elif adversary =="mcts":
                play_game(mode,ai_strategy=MCTS)
                break
        else:
            ai1=input("Select fisrt algorithm (random, mcts): ").strip().lower()
            if ai1=="mcts":
                interations1=input("Choose the numer of iterations of MCTS: ").strip().lower()
                ai1=MCTS
                
            elif ai1=="random":
                ai1=get_random_move
            else:
                print("Erro!!")

            ai2=input("Select fisrt algorithm (random, mcts): ").strip().lower()
            if ai2=="mcts":
                ai2=MCTS
                interations2=input("Choose the numer of iterations of MCTS: ").strip().lower()
            else:
                ai2=get_random_move
            play_game(mode,MCTS,random)
            break
    else:
        print("Invalid mode! Choose 'pvp' (Player vs Player), 'pvc' (Player vs Computer), or 'cvc' (Computer vs Computer).")


