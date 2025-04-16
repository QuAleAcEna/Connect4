import random
import math 
import copy

ROWS = 6
COLS = 7

class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = [row[:] for row in board]  # Copy of the board at this node
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
        return len(self.untried_moves) == 0 or check_winner(self.board,1) or check_winner(self.board,2)


#========CONNECT4 GAME LOGIC=======#

def create_board():
  
    return [[0] * COLS for _ in range(ROWS)]

def print_board(board):
    
    for row in board:
        print("".join("X" if cell == 1 else "O" if cell == 2 else "-" for cell in row))

def is_valid_move(board, col):
    
    return board[0][col] == 0

def get_next_open_row(board, col):
    
    for row in range(ROWS - 1, -1, -1):  
        if board[row][col] == 0:
            return row
    return None  

def drop_piece(board, row, col, piece):
    
    board[row][col] = piece

def check_winner(board, piece):
    
    
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False

def get_valid_moves(board):

    return [column for column in range(COLS) if is_valid_move(board, column)]

def get_random_move(**kwargs):
    board = kwargs.get("board")
    
    return random.choice(get_valid_moves(board))



def MCTS(**kwargs):
    root = kwargs.get("root")
    iterations = kwargs.get("iterations", 1000)
    bestchild = kwargs.get("bestchild", bestchild_default)
    backprograming = kwargs.get("backprograming", backprograming_default)

    
    for _ in range(iterations):
        
        node=selection(root)
        if not node.is_fully_expanded():
            child=expansion(node)
            result=simulation(child)
            backprograming(child,result)
        else:
            result= 3-node.player if check_winner(node.board,3-node.player) else 0
            backprograming(node,result)
    
    return bestchild(root).move

def selection(node: MCTSNode):
  
    while not node.is_fully_expanded() and node.children:
        node = max(node.children, key=lambda child: child.ucb1(node.visits))
        
    return node

def expansion(node: MCTSNode) ->MCTSNode:
    
    move=random.choice(node.untried_moves)
    node.untried_moves.remove(move)
    
    row=get_next_open_row(node.board,move)
    new_board=[row[:] for row in node.board]
    drop_piece(new_board,row,move,3-node.player)
    
    expanded_node=MCTSNode(board=new_board,player=3-node.player,parent=node,move=move)
    node.children.append(expanded_node)
    return expanded_node


def simulation(node: MCTSNode) ->int:
    board=[row[:] for row in node.board]
    player= 3 - node.player
    while get_valid_moves(board):
    
        move=get_random_move(board=board)
        row=get_next_open_row(board,move)
        if row is None:
            continue
        drop_piece(board,row,move,player)
        
        if check_winner(board,player):
            return player
        player=3-player
    return 0

def backprograming_default(node : MCTSNode,result):

    while node is not None:
        node.visits+=1
        if result== 3 - node.player:
            node.wins+=1
        elif result==0:
            node.wins+=0.5
        node=node.parent

def backprograming_greddy(node : MCTSNode,result):

    while node is not None:

        node.visits+=1

        if result== 3 - node.player:
            node.wins+=1

        node=node.parent

def bestchild_default(node : MCTSNode):
    return max(node.children, key=lambda child:child.wins/child.visits if child.visits > 0 else -1)



def higherVisits(node : MCTSNode):
    return max(node.children, key=lambda child:child.visits)

def play_game(mode="pvc", ai=None):
    board = create_board()
    game_over = False
    turn = 1  
    root=None
    if ai==MCTS:
        root=MCTSNode(board,1)
    
    print_board(board)

    while not game_over:
        
        if mode == "pvp" or (mode == "pvc" and turn == 1):
            
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
    
            if ai:
                col = ai(root=root,board=board)
                    

            
            else:
                raise ValueError("AI strategy not provided for computer player.")
            print(f"Computer {turn} chooses column {col}")
        
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn)
        
        print_board(board)

        
        if root:
           root=update_root(root,board,col,turn)
 
        if check_winner(board, turn):
            print(f"Player {turn} ({'X' if turn == 1 else 'O'}) wins!")
            return turn
        elif not get_valid_moves(board):
            print("It's a draw!")
            return 0

        turn = 3 - turn  

def update_root(root,board,col,turn):   
    matching_child = next((child for child in root.children if child.move == col), None)
    if matching_child:
        root = matching_child
        root.parent = None
    else:
        root = MCTSNode(board=board, player=3 - turn)
    return root 

def benchmark(strategy1, strategy2, games=20):
    ai1_wins = 0
    draws = 0
    silent = input("Do you want to see the moves? (Y/N) ").strip().upper() != "Y"


    for _ in range(games):
        winner = simulate_game( ai1=strategy1, ai2=strategy2,silent=silent)
        if winner == 1:
            ai1_wins += 1
        elif winner == 0:
            draws += 1
    print(f"{strategy1}: {ai1_wins}, Draws: {draws}, {strategy2}: {games - ai1_wins - draws}")

def simulate_game(ai1,ai2,silent=True):
    board=create_board()
    root1=None
    root2=None
    turn=1
    if ai1==MCTS:
        root1=MCTSNode(board,2)

    if ai2==MCTS:
        root2=MCTSNode(board,1)
    
    if not silent:
        print_board(board)
    while True:
        if check_winner(board,3 - turn):
            print(f"Player {turn} ({'X' if turn == 1 else 'O'}) wins!")
            return turn
        elif not get_valid_moves(board):
            print("It's a draw!")
            return 0
        
        if turn==1:
            col=ai1(board=board,root=root1)
        else:
            col=ai2(board=board,root=root2)
        
        row=get_next_open_row(board,col)
        drop_piece(board,row,col,turn)

        if not silent:
            print_board(board)
        

        if root1:
            root1=update_root(root1,board,col,turn)
        if root2:
            root2=update_root(root2,board,col,turn)
        turn= 3-turn
    

def select_mcts_parameters():
    ...

def play():
    mode=input("Choose the mode : (pvp, pvc, benchmark) ").strip().lower()

    if mode=="pvc":
        opponent=input("Choose adversary: (random, mcts) ").strip().lower()
        if opponent=="mcts":
            
            play_game(mode,MCTS)
        elif opponent=="random":

            play_game(mode,get_random_move)
        else:
            print("Error!! Choose adversary: (random, mcts) ")
    elif mode=="pvp":
        play_game(mode)
    
    elif mode=="benchmark":
        ai1=input("Select fisrt algorithm (random, mcts): ").strip().lower()
        ai2=input("Select second algorithm (random, mcts): ").strip().lower()

        print(f"Simulating {ai1} vs {ai2} ...")
        if ai1=="mcts":
            ai1=MCTS
            
        elif ai1=="random":
            ai1=get_random_move
        
        if ai2=="mcts":
            ai2=MCTS
        elif ai2=="random":
            ai2=get_random_move
        
        benchmark(ai1,ai2)
    else:
        print("Invalid mode! Choose 'pvp' (Player vs Player), 'pvc' (Player vs Computer), or 'cvc' (Computer vs Computer).")

play()



