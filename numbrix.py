# Grupo 68:
# 95665 Rodrigo Gonçalves
# 95683 Tomás Phillipart

from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, \
	recursive_best_first_search
from sys import argv
import numpy as np

from search import *


class NumbrixState:
	state_id = 0

	def __init__(self, board, position=None):
		self.board = board
		self.position = position
		self.id = NumbrixState.state_id
		NumbrixState.state_id += 1

	def __lt__(self, other):
		return self.id < other.id


class Board:
	""" Representação interna de um tabuleiro de Numbrix. """

	def __init__(self, n):
		self.board_repr = np.zeros((n, n), dtype=int)
		self.filled = {}

	def size(self):
		"""Devolve o tamanho da board"""

		return len(self.board_repr)

	def change_entry(self, row, col, value):
		"""Muda uma entrada na board"""

		self.board_repr[row, col] = value

	def get_number(self, row: int, col: int) -> int:
		""" Devolve o valor na respetiva posição do tabuleiro. """

		return self.board_repr[row, col]

	def adjacent_empty_positions(self, row: int, col: int) -> [(int, int)]:
		"""Devolve as posições adjacentes vazias"""

		n = len(self.board_repr)
		adjacent_positions = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
		return [pos for pos in adjacent_positions if
				pos[0] in range(n) and
				pos[1] in range(n) and
				self.get_number(pos[0], pos[1]) == 0]

	def adjacent_numbers(self, row: int, col: int):
		"""Devolve todos os valores adjacentes"""

		return self.adjacent_vertical_numbers(row, col) + self.adjacent_horizontal_numbers(row, col)

	def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente abaixo e acima,
		respectivamente. """

		if row == 0:
			return (None, self.get_number(row + 1, col))
		elif row == len(self.board_repr) - 1:
			return (self.get_number(row - 1, col), None)
		else:
			return (self.get_number(row - 1, col), self.get_number(row + 1, col))

	def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
		""" Devolve os valores imediatamente à esquerda e à direita,
		respectivamente. """
		if col == 0:
			return (None, self.get_number(row, col + 1))
		elif col == len(self.board_repr) - 1:
			return (self.get_number(row, col - 1), None)
		else:
			return (self.get_number(row, col - 1), self.get_number(row, col + 1))

	@staticmethod
	def parse_instance(filename: str):
		""" Lê o ficheiro cujo caminho é passado como argumento e retorna
		uma instância da classe Board. """

		# Read file
		with open(filename, "r") as f:
			n = int(f.readline())
			board = Board(n)
			for line, i in zip(f, range(n)):
				board.board_repr[i] = (list(map(int, line.rstrip("\n").split("\t"))))

		# Get filled positions
		aux = {}
		n = len(board.board_repr)
		for row in range(n):
			for col in range(n):
				value = board.get_number(row, col)
				if value != 0:
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
		board = state.board
		n = board.size()

		if state.position is None:
			next_value = 1
		else:
			row, col = state.position
			next_value = board.get_number(row, col) + 1

		# If next value in board
		if next_value in board.filled:
			row, col = board.filled[next_value]
			return [(row, col, next_value)]

		# Get next filled values
		bigger_values_filled = [filled_value for filled_value in board.filled if filled_value > next_value]
		if len(bigger_values_filled) == 0:
			next_filled = None
		else:
			value = bigger_values_filled[0]
			row, col = board.filled[value]
			next_filled = (row, col, value)

		possible_positions = []
		# All available positions for 1
		if next_value == 1:
			for row in range(n):
				for col in range(n):
					if board.get_number(row, col) != 0:
						continue

					possible_positions.append((row, col))

		# Adjacent positions to last inserted value
		else:
			row, col = state.position
			possible_positions = state.board.adjacent_empty_positions(row, col)

		for pos in possible_positions:
			row, col = pos

			# If manhattan distance to next already filled is bigger then the difference of values
			if next_filled is not None and \
					abs(next_filled[0] - row) + abs(next_filled[1] - col) > abs(next_filled[2] - next_value):
				continue

			else:
				actions.append((row, col, next_value))

		return actions

	def result(self, state: NumbrixState, action) -> NumbrixState:
		""" Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state). """

		board = state.board
		row, col, value = action

		# Create new board with action applied
		new_board = Board(board.size())
		new_board.filled = board.filled
		new_board.board_repr = board.board_repr.copy()
		new_board.change_entry(row, col, value)

		# Create new state with the new board
		new_state = NumbrixState(new_board, (row, col))

		return new_state

	def goal_test(self, state: NumbrixState) -> bool:
		""" Retorna True se e só se o estado passado como argumento é
		um estado objetivo. Deve verificar se todas as posições do tabuleiro
		estão preenchidas com uma sequência de números adjacentes. """

		board = state.board
		n = board.size()

		# Last value hasn't been put
		if state.position is None or board.get_number(state.position[0], state.position[1]) != n ** 2:
			return False

		for row in range(n):
			for col in range(n):
				value = board.get_number(row, col)

				if value == 0:
					return False

				adj_values = board.adjacent_numbers(row, col)

				if value == 1 and value + 1 in adj_values:
					continue

				elif value == n ** 2 and value - 1 in adj_values:
					continue

				elif value + 1 not in adj_values or value - 1 not in adj_values:
					return False

		return True

	def h(self, node: Node) -> float:
		board = node.state.board

		path_cost = board.size() ** 2
		if node.action is None:
			return path_cost

		value_put = node.action[2]
		if node.parent.action is None:
			return path_cost - value_put

		last_filled = list(board.filled.keys())[-1]
		lrow, lcol = board.filled[last_filled]

		# Check if it creates an invalid position next to parent
		adj_parent = board.adjacent_empty_positions(node.parent.action[0], node.parent.action[1])
		for pos in adj_parent:
			row = pos[0]
			col = pos[1]

			adj_values = board.adjacent_numbers(row, col)

			# Classify adjacent values
			zero = minor = major = 0
			for value in adj_values:
				if value == 0:
					zero += 1

				elif value is None or value < value_put:
					minor += 1

				else:
					major += 1

			# Check the existence of dead ends
			if zero == 1 and minor == 3 and abs(row - lrow) + abs(col - lcol) > path_cost - last_filled:
				return float('inf')

			# Check the existence an entry surrounded by smaller values
			elif minor == 4:
				return float('inf')

		return path_cost - value_put







def compare_searchers(problems, header,
					  searchers=[breadth_first_tree_search,
								 depth_first_tree_search,
								 greedy_search,
								 astar_search,
								 recursive_best_first_search]):
	def do(searcher, problem):
		start = time.time()
		p = InstrumentedProblem(problem)
		searcher(p)
		end = time.time()
		p.time = end - start
		return p

	table = [[name(s)] + [do(s, p) for p in problems] for s in searchers]
	print_table(table, header)


def compare__searchers():
	"""Prints a table of search results."""
	compare_searchers(problems=[Numbrix(Board.parse_instance(argv[1]))],
					  header=['Searcher', argv[1]])



if __name__ == "__main__":
	# bord = Board.parse_instance(argv[1])
	#
	# problem = Numbrix(bord)
	# goal_node = breadth_first_tree_search(problem)
	# print(goal_node.state.board.to_string(), end='')

	compare__searchers()



