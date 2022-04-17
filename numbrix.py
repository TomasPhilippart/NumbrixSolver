# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, \
	recursive_best_first_search
from copy import deepcopy
from sys import argv


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
		self.filled = []

	def get_number(self, row: int, col: int) -> int:
		""" Devolve o valor na respetiva posição do tabuleiro. """
		return self.board_repr[row][col]

	def get_adjacent_positions(self, row: int, col: int) -> [(int, int)]:
		adjacent_positions = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
		valid_adjacent_positions = []

		for position in adjacent_positions:
			if (position[0] in range(0, self.n) and position[1] in range(0, self.n)):
				valid_adjacent_positions.append(position)
		return valid_adjacent_positions

	def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente abaixo e acima,
		respectivamente. """
		if (row == 0):
			return (None, self.board_repr[row + 1][col])
		elif (row == self.n - 1):
			return (self.board_repr[row - 1][col], None)
		else:
			return (self.board_repr[row - 1][col], self.board_repr[row + 1][col])

	def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente à esquerda e à direita,
		respectivamente. """
		if (col == 0):
			return (None, self.board_repr[row][col + 1])
		elif (col == self.n - 1):
			return (self.board_repr[row][col - 1], None)
		else:
			return (self.board_repr[row][col - 1], self.board_repr[row][col + 1])

	@staticmethod
	def parse_instance(filename: str):
		""" Lê o ficheiro cujo caminho é passado como argumento e retorna
		uma instância da classe Board. """

		# Read file
		with open(filename, "r") as f:
			board = Board(int(f.readline()))
			for line in f:
				board.board_repr.append(list(map(int, line.rstrip("\n").split("\t"))))

		# Get filled positions
		for line in board.board_repr:
			for value in line:
				if value != 0:
					row = board.board_repr.index(line)
					col = line.index(value)
					board.filled.append((row, col, value))

		# Sort by value
		board.filled.sort(key=lambda e: e[2])

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
		next_filled = None
		for x in state.board.filled:
			if(x[2] >= next_value):
				next_filled = x
				break

		actions = []

		# Find actions for initial value
		if next_value == 1:
			# 1 is already on the board
			if next_filled[2] == next_value:
				return [next_filled]

			for line in state.board.board_repr:
				for line_i in range(len(line)):
					row = state.board.board_repr.index(line)
					col = line_i

					if line[line_i] != 0:
						continue

					# Manhattan distance is bigger than the difference between the values
					if abs(next_filled[0] - row) + abs(next_filled[1] - col) > next_filled[2] - next_value:
						continue

					else:
						actions.append((row, col, next_value))

		# Find actions for next values
		else:
			adj_positions = state.board.get_adjacent_positions(state.position[0], state.position[1])

			# If next value is already filled
			if next_filled is not None and next_filled[2] == next_value:
				# In adjacent position
				if (next_filled[0], next_filled[1]) in adj_positions:
					actions.append(next_filled)

			else:
				for pos in adj_positions:
					row = pos[0]
					col = pos[1]

					if state.board.board_repr[row][col] != 0:
						continue

					# Manhattan distance is bigger than the difference between the values
					elif next_filled is not None and abs(next_filled[0] - row) + abs(next_filled[1] - col) > \
							next_filled[2] - next_value:
						continue

					else:
						actions.append((row, col, next_value))

		return actions

	def result(self, state: NumbrixState, action) -> NumbrixState:
		""" Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state). """

		# Copy
		board_copy = Board(board.n)
		board_copy.board_repr = [x[:] for x in state.board.board_repr] # copy
		board_copy.filled = state.board.filled

		new_state = NumbrixState(board_copy, (action[0], action[1]), action[2])
		new_state.board.board_repr[action[0]][action[1]] = action[2]
		return new_state

	def goal_test(self, state: NumbrixState) -> bool:
		""" Retorna True se e só se o estado passado como argumento é
		um estado objetivo. Deve verificar se todas as posições do tabuleiro
		estão preenchidas com uma sequência de números adjacentes. """

		# Last value hasn't been but
		if state.value != state.board.n ** 2:
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

				elif value == state.board.n ** 2 and value - 1 in adj_values:
					continue

				elif value + 1 not in adj_values or value - 1 not in adj_values:
					return False

		return True

	def h(self, node: Node) -> int:
		""" Função heuristica utilizada para a procura A*. """

		return (node.state.board.n ** 2 - node.state.value) * (1.0 + 1 / node.state.board.n ** 2)


# TODO: outros metodos da classe

if __name__ == "__main__":
	board = Board.parse_instance(argv[1])
	# print("Initial:\n", board.to_string(), sep="")
	# print(board.filled)

	problem = Numbrix(board)
	goal_node = astar_search(problem)
	print(goal_node.state.board.to_string(), end='')
