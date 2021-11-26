import pygame
import os
import random
import numpy as np
import time

def main():
	pygame.init()

	screen = pygame.display.set_mode((500,400))
	pygame.display.set_caption("Memory")

	# Add a relative path to read images from a folder stored in the same directory as the code file.
	path = str(os.path.dirname(os.path.realpath(__file__))) + "/"

	game = Game(screen, path)

	# When a new round starts, shuffle the rows of the board as well as the tiles on each row.
	random.shuffle(game.board)
	for row in game.board:
		random.shuffle(row)

	game.play()

	pygame.quit()

class Game:
	def __init__(self, screen, path):
		self.screen = screen
		self.path = path
		self.bg_color = pygame.Color("black")

		self.FPS = 60
		self.game_clock = pygame.time.Clock()
		self.close_clicked = False
		self.continue_game = True
		self.score = 0  # Score is initally set to 0.

		self.board_size = 4  # Assuming it's always a n*n board, this is the number of rows as well as the number of columns of the board.
		
		# Find all images in the images folder stored in the same directory as the code file. Duplicate each image and store all them in a list.
		self.all_images = [self.path+"images/"+item for item in os.listdir(self.path+"images") * 2 if item != "image0.bmp"]
		random.shuffle(self.all_images)  # Shuffle the list of images.
		self.all_images = [list(row) for row in np.array_split(self.all_images, self.board_size)]  # Split the list of images into n equaly sized lists.

		self.board = self.create_tiles()
		self.flipped_tiles = []  # Keep track of the tiles flipped.
		self.images_shown = []  # Keep track of how many times an image is shown.
		
	def play(self):
		while not self.close_clicked:
			self.handle_events()
			self.draw()
			if self.continue_game:
				self.update()
				self.decide_continue()
			self.game_clock.tick(self.FPS)
			
	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.close_clicked = True
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self.handle_mouse_down(event)

	def handle_mouse_down(self, event):
		for row in self.board:
			for tile in row:
				if tile.select(event.pos):
					# If not all tiles are flipped, the image behind the tile selected are not shown twice and the it's a different tile being selected:
					if self.continue_game and self.images_shown.count(tile.hidden_content) < 2 and tile not in self.flipped_tiles:
						self.images_shown.append(tile.hidden_content)  # hidden_content being the image behind a tile
						self.flipped_tiles.append(tile)
						tile.flip()

	def draw(self):
		self.screen.fill(self.bg_color)
		self.draw_all_tiles()
		self.draw_score()
		pygame.display.flip()

	def all_tiles_flipped(self):
		# Check if all tiles are flipped. If the number of tiles flipped equal the total number of tiles, return True, else False.
		return len(self.flipped_tiles) == self.board_size ** 2

	def decide_continue(self):
		# If all tiles are flipped, self.continue_game = False, else remains True.
		if self.all_tiles_flipped():
			self.continue_game = False

	def create_tiles(self):
		screen_width = self.screen.get_width()
		screen_height = self.screen.get_height()

		tile_width = (screen_width - 100) // self.board_size
		tile_height = screen_height // self.board_size

		tiles = []
		for r in range(self.board_size):
			row = []
			for c in range(self.board_size):
				x = c * tile_width
				y = r * tile_height
				tile = Tile(self.screen, x, y, tile_width, tile_height, self.path, self.all_images[r][c])  # The image in the list of images having the same position as the tile in the board is the image behind the tile.
				row.append(tile)
			tiles.append(row)
				
		return tiles

	def draw_all_tiles(self):
		for row in self.board:
			for tile in row:
				tile.draw()

	def draw_score(self):
		score_string = str(self.score)
		score_color = pygame.Color("white")
		font = pygame.font.SysFont("Calibri", 40, bold = True, italic = False)
		score_image = font.render(score_string, True, score_color)
		self.screen.blit(score_image, (self.screen.get_width()-10-score_image.get_width(), 10))

	def update(self):
		# Update the score.
		self.score = pygame.time.get_ticks() // 1000

		# Flip the 2 tiles most recently pressed back if they don't match
		if len(self.flipped_tiles)%2 == 0 and len(self.flipped_tiles) > 0:  # If tiles are flipped and the number of tiles flipped is even, we know to check if the 2 images match.
			second_last_img = self.flipped_tiles[-2].hidden_content
			last_img = self.flipped_tiles[-1].hidden_content
			if second_last_img != last_img:  # If the 2 images don't match:
				time.sleep(1)  # Show the images for a second
				self.flipped_tiles[-2].unflip()  # Then, unflip the first image pressed.
				self.flipped_tiles[-1].unflip()  # Unflip the second image pressed.
				# Remove the tiles from the list of tiles flipped and remove the images from the list of images shown.
				self.flipped_tiles.pop(-2)
				self.flipped_tiles.pop(-1)
				self.images_shown.pop(-2)
				self.images_shown.pop(-1)

class Tile:
	def __init__(self, screen, x, y, width, height, path, hidden_content):
		self.screen = screen
		self.rect = pygame.Rect(x, y, width, height)
		self.path = path
		
		self.hidden_content = hidden_content
		self.content = pygame.image.load(self.path+"images/image0.bmp")  # Inially, all tiles have the same image of a question mark.

		self.line_width = 3  # The space between each tile is 3 pixels.

	def draw(self):
		pygame.draw.rect(self.screen, pygame.Color("black"), self.rect, self.line_width)
		self.draw_content()

	def draw_content(self):
		x = self.rect.x
		y = self.rect.y
		location = (x,y)
		self.screen.blit(self.content, location)

	def select(self, pos):
		return self.rect.collidepoint(pos)

	def flip(self):
		# To flip a tile, show the image behind the tile.
		self.content = pygame.image.load(self.hidden_content)

	def unflip(self):
		# To unflip a tile, show the image of a question mark.
		self.content = pygame.image.load(self.path+"images/image0.bmp")
			
main()