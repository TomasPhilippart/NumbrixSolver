# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, \
	recursive_best_first_search
from sys import argv

class NumbrixState:
	state_id = 0

	def __init__(self, board, action=None):
		self.board = board
		self.action = action
		self.id = NumbrixState.state_id
		NumbrixState.state_id += 1

	def __lt__(self, other):
		return self.id < other.id


# TODO: outros metodos da classe


class Board:
	""" Representação interna de um tabuleiro de Numbrix. """

	def __init__(self):
		self.board_repr = []
		self.filled = {}

	def get_number(self, row: int, col: int) -> int:
		""" Devolve o valor na respetiva posição do tabuleiro. """
		return self.board_repr[row][col]

	def get_adjacent_positions(self, row: int, col: int) -> [(int, int)]:
		n = len(self.board_repr)
		adjacent_positions = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
		return [pos for pos in adjacent_positions if
				pos[0] in range(n) and
				pos[1] in range(n) and
				self.board_repr[pos[0]][pos[1]] == 0]

	def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente abaixo e acima,
		respectivamente. """
		if row == 0:
			return (None, self.board_repr[row + 1][col])
		elif row == len(self.board_repr) - 1:
			return (self.board_repr[row - 1][col], None)
		else:
			return (self.board_repr[row - 1][col], self.board_repr[row + 1][col])

	def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente à esquerda e à direita,
		respectivamente. """
		if col == 0:
			return (None, self.board_repr[row][col + 1])
		elif col == len(self.board_repr) - 1:
			return (self.board_repr[row][col - 1], None)
		else:
			return (self.board_repr[row][col - 1], self.board_repr[row][col + 1])

	@staticmethod
	def parse_instance(filename: str):
		""" Lê o ficheiro cujo caminho é passado como argumento e retorna
		uma instância da classe Board. """

		# Read file
		with open(filename, "r") as f:
			board = Board()
			n = int(f.readline())
			for line in f:
				board.board_repr.append(list(map(int, line.rstrip("\n").split("\t"))))

		# Get filled positions
		aux = {}
		for line in board.board_repr:
			for value in line:
				if value != 0:
					row = board.board_repr.index(line)
					col = line.index(value)
					aux[value] = (row, col)

		for key in sorted(aux):
			board.filled[key] = aux[key]

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

		actions = []

		if state.action is None:
			next_value = 1
		else:
			next_value = state.action[2] + 1

		# If next value in board
		if next_value in state.board.filled:
			row, col = state.board.filled[next_value]
			return [(row, col, next_value)]

		# Get next filled values
		next_filled = None
		for value_filled in state.board.filled:
			if value_filled > next_value:
				row, col = state.board.filled[value_filled]
				next_filled = (row, col, value_filled)
				break

		possible_positions = []
		# All available positions for 1
		if next_value == 1:
			for line in state.board.board_repr:
				for col in range(len(line)):
					row = state.board.board_repr.index(line)

					if state.board.board_repr[row][col] != 0:
						continue

					possible_positions += [(row, col)]

		# Adjacent positions to last inserted value
		else:
			possible_positions = state.board.get_adjacent_positions(state.action[0], state.action[1])

		for pos in possible_positions:
			row, col = pos

			# If manhattan distance to next already filled is bigger then the difference of values
			if next_filled is not None and \
					abs(next_filled[0] - row) + abs(next_filled[1] - col) > abs(next_filled[2] - next_value):
				continue

			else:
				actions.append((row, col, next_value))

		#print(f"{next_value} -> {actions}")
		return actions

	def result(self, state: NumbrixState, action) -> NumbrixState:
		""" Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state). """

		# Copy
		row, col, value = action
		new_board = Board()
		new_board.filled = state.board.filled
		new_board.board_repr = state.board.board_repr.copy()
		new_board.board_repr[row] = state.board.board_repr[row].copy()
		new_board.board_repr[row][col] = value
		new_state = NumbrixState(new_board, action)

		return new_state

	def goal_test(self, state: NumbrixState) -> bool:
		""" Retorna True se e só se o estado passado como argumento é
		um estado objetivo. Deve verificar se todas as posições do tabuleiro
		estão preenchidas com uma sequência de números adjacentes. """

		#print(state.board.to_string())

		last_value = len(state.board.board_repr) ** 2
		# Last value hasn't been but
		if state.action is None or state.action[2] != last_value:
			return False

		for line in state.board.board_repr:
			for value in line:
				row = state.board.board_repr.index(line)
				col = line.index(value)

				if value == 0:
					return False

				adj_values = state.board.adjacent_horizontal_numbers(row, col) + state.board.adjacent_vertical_numbers(
					row, col)

				if value == 1 and value + 1 in adj_values:
					continue

				elif value == last_value and value - 1 in adj_values:
					continue

				elif value + 1 not in adj_values or value - 1 not in adj_values:
					return False
		return True

	def h(self, node: Node) -> float:

		state = node.state
		board = node.state.board
		path_cost = len(board.board_repr) ** 2
		if node.state.action is None:
			return path_cost

		last_put = state.action[2]
		last_filled = list(board.filled.keys())[-1]
		lrow, lcol = board.filled[last_filled]

		# Check valid board
		for line in board.board_repr:
			for col in range(len(line)):
				if line[col] != 0:
					continue

				row = board.board_repr.index(line)

				adj_values = board.adjacent_vertical_numbers(row, col) + board.adjacent_horizontal_numbers(row, col)

				# Count adj values
				zero = minor = major = 0
				for value in adj_values:
					if value == 0:
						zero += 1

					elif value is None or value < last_put:
						minor += 1

					else:
						major += 1

				if zero == 1 and minor == 3 and abs(row - lrow) + abs(col-lcol) > path_cost - last_filled:
					return float('inf')
				elif minor == 4:
					return float('inf')

		return path_cost - last_put


# TODO: outros metodos da classe

if __name__ == "__main__":
	bord = Board.parse_instance(argv[1])
	# print("Initial:\n", board.to_string(), sep="")
	# print(board.filled)

	problem = Numbrix(bord)
	goal_node = greedy_search(problem)
	print(goal_node.state.board.to_string(), end='')
