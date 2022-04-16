# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

from cgi import print_environ
from os import system
from lib.search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, recursive_best_first_search
from copy import deepcopy

from lib.utils import print_table

class NumbrixState:
    state_id = 0

    def __init__(self, board, position=None, value=0):
        self.position = position
        self.value = value
        self.board = board
        self.id = NumbrixState.state_id
        NumbrixState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id
        
    # TODO: outros metodos da classe


class Board:
    """ Representação interna de um tabuleiro de Numbrix. """

    def __init__(self, n: int):
        self.n = n
        self.board_repr = []
        self.filled = {}
    
    def get_number(self, row: int, col: int) -> int:
        """ Devolve o valor na respetiva posição do tabuleiro. """
        return self.board_repr[row][col]

    def get_adjacent_positions(self, row: int, col: int) -> [(int, int)]:
        adjacent_positions = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        valid_adjacent_positions = []

        for position in adjacent_positions:
            if (position[0] in range(0, self.n) and position[1] in range(0, self.n)):
                valid_adjacent_positions.append(position)
        return valid_adjacent_positions

    def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente abaixo e acima, 
        respectivamente. """    
        if (row == 0):
            return (None, self.board_repr[row+1][col])
        elif (row == self.n - 1):
            return (self.board_repr[row-1][col], None)
        else:
            return (self.board_repr[row-1][col], self.board_repr[row+1][col])
    
    def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente à esquerda e à direita, 
        respectivamente. """
        if (col == 0):
            return (None, self.board_repr[row][col+1])
        elif (col == self.n - 1):
            return (self.board_repr[row][col-1], None)
        else:
            return (self.board_repr[row][col-1], self.board_repr[row][col+1])

    @staticmethod    
    def parse_instance(filename: str):
        """ Lê o ficheiro cujo caminho é passado como argumento e retorna
        uma instância da classe Board. """

        with open(filename, "r") as f:
            board = Board(int(f.readline()))
            for line in f:
                board.board_repr.append(list(map(int, line.rstrip("\n").split("\t"))))

        for line in board.board_repr:
            for value in line:
                if value != 0:
                    board.filled[value] = (board.board_repr.index(line), line.index(value))

        return board
    
    def __repr__(self):
        return self.board_repr
    
    def to_string(self):
        output = ''
        for i in self.board_repr:
            output += '\t'.join(map(str, i))
            output += '\n'
        return output


class Numbrix(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """
        self.initial = NumbrixState(board)
        pass

    def actions(self, state: NumbrixState) -> [(int, int, int)]:
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """

        next_value = state.value + 1
        actions = []

        #Possible actions for next states
        if state.position is not None:
            
            adj_positions = state.board.get_adjacent_positions(state.position[0], state.position[1])
            
            # If next value is already filled and not adjancent
            if next_value in state.board.filled and state.board.filled[next_value] not in adj_positions:
                return []

            # If next value is already filled
            elif next_value in state.board.filled:
                return [state.board.filled[next_value] + (next_value, )]

            return [(*x, next_value) for x in adj_positions if state.board.board_repr[x[0]][x[1]] == 0]
            
        #Actions for initial state
        else:
            if next_value in state.board.filled:
                return [state.board.filled[next_value] + (next_value, )]

            for line in state.board.board_repr:
                for value in line:
                    row = state.board.board_repr.index(line)
                    col = line.index(value)
                    action = (row, col, next_value)

                    if value != 0:
                        continue

                    else:
                        actions.append(action)

        return actions

    def result(self, state: NumbrixState, action) -> NumbrixState:
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de 
        self.actions(state). """

        # Copy
        board_copy = Board(board.n)
        board_copy.board_repr = deepcopy(state.board.board_repr)
        board_copy.filled = deepcopy(state.board.filled)
        
        if(action == 0):
            return NumbrixState(board_copy, None, 0)

        new_state = NumbrixState(board_copy, (action[0], action[1]), action[2])
        new_state.board.board_repr[action[0]][action[1]] = action[2]
        return new_state

    def goal_test(self, state: NumbrixState) -> bool:
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes. """

        print(state.board.to_string())

        for line in state.board.board_repr:
                for value in line:
                    row = state.board.board_repr.index(line)
                    col = line.index(value)

                    if value == 0:
                        return False

                    adj_values = state.board.adjacent_horizontal_numbers(row,col) + state.board.adjacent_vertical_numbers(row,col)
                    if value == 1 and value + 1 in adj_values:
                        continue;  
                    
                    elif value == state.board.n ** 2 and value - 1 in adj_values:
                        continue
                    
                    elif value + 1 not in adj_values or value - 1 not in adj_values:
                        return False

        return True       
    
    #
    def h(self, node: Node) -> int:
        """ Função heuristica utilizada para a procura A*. """

        if node.state.position is None:
            return 0

        row = node.action[0]
        col = node.action[1]
        value = node.action[2]
        heuristic = 2

        adj_values = board.adjacent_vertical_numbers(row, col) + board.adjacent_horizontal_numbers(row, col)

        for var in adj_values:
            if value + 1 == var or value - 1 == var:
                heuristic -= 1

        if (value == 1 or value == board.n ** 2) and heuristic == 1:
            heuristic = 0

        return heuristic
    
    # TODO: outros metodos da classe


if __name__ == "__main__":
    board = Board.parse_instance("../tests/input7.txt")
    print("Initial:\n", board.to_string(), sep="")
    #print(board.filled)

    problem = Numbrix(board)

    goal_node = depth_first_tree_search(problem)
    print(goal_node.state.board.to_string())
