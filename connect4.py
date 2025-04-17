import random
import math 
from queue import Queue

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

#============MCTS==============#

def MCTS(**kwargs):
    root = kwargs.get("root")
    iterations = kwargs.get("iterations", 500)
    bestchild = kwargs.get("bestchild", bestchild_default)
    backprograming = kwargs.get("backprograming", backprograming_default)
    c = kwargs.get("c", 1.41)
    debug=False
    for _ in range(iterations):
        node = selection(root,c=c)
        if not node.is_fully_expanded():
            child = expansion(node)
            result = simulation(child)
            backprograming(child, result)
        else:
            result = node.player if check_winner(node.board,  node.player) else 0
            backprograming(node, result)

    if debug:
        print(f"[MCTS DEBUG] Root visits: {root.visits}")
        print(f"[MCTS DEBUG] Number of children after {iterations} iterations: {len(root.children)}")
        for child in root.children:
            print(f"  - Move: {child.move}, Visits: {child.visits}, Wins: {child.wins}")
            print("    Resulting board:")
            for row in child.board:
                print("    " + "".join(["-" if cell == 0 else ("X" if cell == 1 else "O") for cell in row]))
            print()
    
    chosen = bestchild(root)
    if chosen is None:
        print("[MCTS DEBUG] No child chosen — fallback to random move.")
        return random.choice(get_valid_moves(root.board))

    return chosen.move

def selection(node: MCTSNode, c=1.41):
    while True:
    
        if not node.is_fully_expanded():
            return node

        if not node.children:
            return node

        unvisited = [child for child in node.children if child.visits == 0]
        if unvisited:
            return random.choice(unvisited)

        node = max(node.children, key=lambda child: child.ucb1(node.visits))

def expansion(node: MCTSNode,debug=False) ->MCTSNode:
    
    move=random.choice(node.untried_moves)
    node.untried_moves.remove(move)
    
    row=get_next_open_row(node.board,move)
    new_board=[row[:] for row in node.board]
    
    drop_piece(new_board,row,move,3-node.player)
    if debug:
        print(f"[EXPANSION DEGUB] Player: {3-node.player}")
        print(f"[EXPANSION DEBUG] New node expanded move {move} {print_board(new_board)}")
    
        if any(child.move == move for child in node.children):
            print(f"[WARNING] Move {move} já existe como filho! Isto não devia acontecer.")

        if node.parent is None: 
            print(f"[EXPANSION DEBUG] Expanded move {move} at root")

    expanded_node=MCTSNode(board=new_board,player=3-node.player,parent=node,move=move)

    node.children.append(expanded_node)

    return expanded_node

def get_smart_move(board, player):
  
    for col in get_valid_moves(board):
        row = get_next_open_row(board, col)
        temp_board = [r[:] for r in board]
        drop_piece(temp_board, row, col, player)
        if check_winner(temp_board, player):
            return col

   
    opponent = 3 - player
    for col in get_valid_moves(board):
        row = get_next_open_row(board, col)
        temp_board = [r[:] for r in board]
        drop_piece(temp_board, row, col, opponent)
        if check_winner(temp_board, opponent):
            return col

   
    return random.choice(get_valid_moves(board))

def simulation(node: MCTSNode) ->int:
    board=[row[:] for row in node.board]
    player= 3 - node.player
    while get_valid_moves(board):
    
        move=get_smart_move(board=board,player=player)
        row=get_next_open_row(board,move)

        drop_piece(board,row,move,player)
        
        if check_winner(board,player):
            #print(f"[SIMULATION] Vitória do jogador {player}")
            return player
        player=3-player
    return 0

def backprograming_default(node : MCTSNode,result):
    
    while node is not None:
        node.visits+=1

        if result== node.player: #nao faco a minima porque e que funciona em vez de 3-player
            
            node.wins+=1

        elif result==0:
            node.wins+=0.5
        node=node.parent

def backprograming_greddy(node : MCTSNode,result):

    while node is not None:

        node.visits+=1

        if result==  node.player:
            node.wins+=1

        node=node.parent

def bestchild_default(node: MCTSNode):
    if not node.children:
        print("[BESTCHILD DEBUG] No children in node.")
        return None

    visited_children = [child for child in node.children if child.visits > 0]
    if not visited_children:
        print("[BESTCHILD DEBUG] All children have 0 visits.")
        return None

    best = max(visited_children, key=lambda child: child.wins / child.visits)
    #print(f"[BESTCHILD DEBUG] Selected move: {best.move}, win rate: {best.wins / best.visits:.2f}")
    return best

def bestchild_higherVisits(node : MCTSNode):
    if not node.children:
        print("[BESTCHILD DEBUG] No children in node.")
        return None

    visited_children = [child for child in node.children if child.visits > 0]
    if not visited_children:
        print("[BESTCHILD DEBUG] All children have 0 visits.")
        return None

    best = max(visited_children, key=lambda child: child.visits)
    #print(f"[BESTCHILD DEBUG] Selected move: {best.move}, win rate: {best.wins / best.visits:.2f}")
    return best

def update_root(root,board,col,turn):   
    #print(f"[UPDATE ROOT] Looking for move {col} among children: {[child.move for child in root.children]}")

    matching_child = next((child for child in root.children if child.move == col), None)
    if matching_child:
        root = matching_child
        root.parent = None
    else:
        #print(f"[UPDATE ROOT] Tree restarted. Player {turn} played column {col}, but move not in MCTS tree.")
        root = MCTSNode(board=board, player= turn)
    return root 

#================================#

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

def benchmark(strategy1, strategy2, games=20,silent=True, name1="AI1" , name2="AI2"):
    ai1_wins = 0
    draws = 0

    for i in range(games):
        print(f"Simulating game {i+1} ...")
        winner = simulate_game( ai1=strategy1, ai2=strategy2,silent=silent)
        if winner == 1:
            ai1_wins += 1
        elif winner == 0:
            draws += 1
    print(f"{name1}: {ai1_wins}, Draws: {draws}, {name2}: {games - ai1_wins - draws}")

def simulate_game(ai1,ai2,silent=True):
    board=create_board()
    root1=None
    root2=None
    turn=1
    if callable(ai1):
        try:
            root1 = MCTSNode(board, 2)  
        except:
            pass
    if callable(ai2):
        try:
            root2 = MCTSNode(board, 1)
        except:
            pass

    

    
    while True:
       
        winner = 3 - turn if check_winner(board, 3 - turn) else 0

        if winner != 0 or not get_valid_moves(board):
            
            if winner:
                print(f"Player {winner} ({'X' if winner == 1 else 'O'}) wins!")
            else:
                print("It's a draw!")
            return winner

        if turn==1:
            col=ai1(board=board,root=root1)
        else:
            col=ai2(board=board,root=root2)
        
        row=get_next_open_row(board,col)
        drop_piece(board,row,col,turn)

        if not silent:
            print_board(board)
            print(f"Computer {turn} chooses column {col}")
        

        if root1:
            root1=update_root(root1,board,col,turn)
        if root2:
            root2=update_root(root2,board,col,turn)

        turn= 3-turn
    

def select_mcts_parameters(
    c=1.41,
    iterations=1000,
    bestchild_name="bestchild_default",
    backprograming_name="backprograming_default"
):
    # Dicionário de funções disponíveis
    bestchild_options = {
        "bestchild_default":  bestchild_default,
        "bestchild_higherVisits": bestchild_higherVisits
    }

    backprograming_options = {
        "backprograming_default": backprograming_default,
        "backprograming_greddy": backprograming_greddy
    }

    # Verifica se os nomes fornecidos existem
    if bestchild_name not in bestchild_options:
        raise ValueError(f"Função bestchild '{bestchild_name}' não encontrada.")
    if backprograming_name not in backprograming_options:
        raise ValueError(f"Função backprograming '{backprograming_name}' não encontrada.")

    return {
        "c": c,
        "iterations": iterations,
        "bestchild": bestchild_options[bestchild_name],
        "backprograming": backprograming_options[backprograming_name]
    }

def benchmark_menu():
    print("=== Benchmark Menu ===")
    print("Select AI 1 (random, mcts):")
    ai1_choice = input().strip().lower()

    print("Select AI 2 (random, mcts):")
    ai2_choice = input().strip().lower()

    print("Number of games:")
    games = int(input().strip())

    mcts1_params = {}
    mcts2_params = {}

    def configure_mcts(player_label="MCTS"):
        print(f"\n--- {player_label} Parameters ---")
        use_default = input("Use default MCTS parameters? (Y/N): ").strip().upper()
        if use_default == "Y":
            return select_mcts_parameters()  
        else:
            print("Available bestchild functions: bestchild_default, bestchild_higherVisits")
            bestchild_name = input("Choose bestchild: ").strip()

            print("Available backprograming functions: backprograming_default, backprograming_greddy")
            backprograming_name = input("Choose backprograming: ").strip()

            c = float(input("Exploration parameter c (e.g., 1.41): ").strip())
            iterations = int(input("Number of iterations per move: ").strip())

            return select_mcts_parameters(
                c=c,
                iterations=iterations,
                bestchild_name=bestchild_name,
                backprograming_name=backprograming_name
            )

    if ai1_choice == "mcts":
        mcts1_params = configure_mcts("MCTS 1")
    if ai2_choice == "mcts":
        mcts2_params = configure_mcts("MCTS 2")

    
    def get_ai(name, params):
        if name == "random":
            return get_random_move
        elif name == "mcts":
            return lambda **kwargs: MCTS(**{**kwargs, **params})
        else:
            raise ValueError(f"Unknown AI: {name}")

    print("\nShow board during game? (Y/N):")
    silent = input().strip().upper() != "Y"

    print(f"\nSimulating {ai1_choice} vs {ai2_choice} ...\n")
    benchmark(
        strategy1=get_ai(ai1_choice, mcts1_params),
        strategy2=get_ai(ai2_choice, mcts2_params),
        games=games,
        silent=silent,
        name1=ai1_choice.upper(),
        name2=ai2_choice.upper()
    )

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

        benchmark_menu()
    else:
        print("Invalid mode! Choose 'pvp' (Player vs Player), 'pvc' (Player vs Computer), or 'benchmark' (Computer vs Computer).")

play()

