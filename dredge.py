from random import randint

import pygame


class PointSet(object):
	def __init__(self, *args):
		self.points = [pygame.math.Vector2(p) for p in args]
	
	@property
	def x(self):
		return tuple(p.x for p in self.points)
	
	@x.setter
	def x(self, value):
		for p in self.points:
			p.x = value

	@property
	def y(self):
		return tuple(p.y for p in self.points)
	
	@y.setter
	def y(self, value):
		for p in self.points:
			p.y = value
	
	def move(self, x, y):
		for p in self.points:
			p.x += x
			p.y += y
		return self
	
	def rotate(self, angle):
		for p in self.points:
			p.rotate_ip(angle)
		return self
	
	def copy(self):
		return type(self)(*tuple(p.copy() for p in self.points))


class Obstacle(object):
	__slots__ = ("theta", "_ring", "_speed")
	
	def __init__(self, theta, ring, speed=1):
		self.theta = theta
		self._ring = ring
		self._speed = speed
	
	def __repr__(self):
		return f"Obstacle({self.theta}, {self.ring}, {self.speed})"
	
	@property
	def speed(self):
		return self._speed

	@property
	def ring(self):
		return self._ring
		

def generate_obstacles() -> list[Obstacle]:
	spacing = 35
	# no obstacles in ring 1 with a start of more than 360-60 = 300 deg
	space_before_first = 80
	
	num = 9
	rings = [[], []]
	while len(rings[0]) + len(rings[1]) < num:
		d = randint(0, 359)
		r = randint(0, 1)
		if r == 0 and d > 360 - space_before_first:
			print("too close to start")
			continue
		
		other_ring = 1 - r
		
		min_greater = rings[other_ring][0].theta if rings[other_ring] else 1000
		max_less = rings[other_ring][0].theta if rings[other_ring] else 1000
		for ob in rings[other_ring]:
			if ob.theta > d and ob.theta < min_greater:
				min_greater = ob.theta
			
			if ob.theta < d and ob.theta > max_less:
				max_less = ob.theta
		
		if min_greater - d < spacing and d - max_less < spacing:
			continue

		rings[r].append(Obstacle(d, r+1))

	rings[1].extend(rings[0])
	print(rings[1])
	return rings[1]


def reasonable_patterns():
	p = [
		[Obstacle(123, 2, 2), Obstacle(58, 2, 2), Obstacle(248, 2, 2), Obstacle(306, 2, 2), Obstacle(172, 1, 2), Obstacle(77, 1, 2)],
		[Obstacle(279, 2, 2), Obstacle(258, 2, 2), Obstacle(332, 2, 2), Obstacle(122, 2, 2), Obstacle(203, 1, 2), Obstacle(155, 1, 2)],
		[Obstacle(172, 2, 1), Obstacle(290, 2, 1), Obstacle(259, 2, 1), Obstacle(84, 2, 1), Obstacle(33, 2, 1), Obstacle(121, 1, 1), Obstacle(245, 1, 1), Obstacle(100, 1, 1)],
		[Obstacle(171, 2, 1), Obstacle(118, 2, 1), Obstacle(349, 2, 1), Obstacle(292, 2, 1), Obstacle(236, 1, 1), Obstacle(98, 1, 1), Obstacle(211, 1, 1), Obstacle(272, 1, 1), Obstacle(73, 1, 1)],
		
	]



class Wheel(object):
	def __init__(self):
		#self.obstacles = [
		#	Obstacle(10, 1), Obstacle(180, 1), 
		#	Obstacle(90, 2), Obstacle(140, 2), Obstacle(250, 2)
		#]
		
		self.obstacles = []
		ratio = 0
		while not (.3 < ratio < .7):
			self.obstacles = generate_obstacles()
			ratio = len([o for o in self.obstacles if o.ring == 1]) / len(self.obstacles)
		
		self.size = 250
		self.dist_from_edge = 20
		
		self.box_radius = 10
		box = pygame.Rect(0, 0, 2*self.box_radius, 2*self.box_radius)
		box.move_ip(-self.box_radius, -self.box_radius)
		box.move_ip(0, -self.size + self.dist_from_edge)
		
		box_points1 = PointSet(box.topleft, box.topright, box.bottomright, box.bottomleft)
		box_points2 = box_points1.copy().move(0, RING_SEP)
		
		self.rings = {1: box_points1, 2: box_points2}
	
	def rotate(self):
		for ob in self.obstacles:
			ob.theta += ob.speed
	
	def render(self, screen):
		pygame.draw.circle(screen, "brown", CENTER, self.size)
		pygame.draw.circle(screen, "gray", CENTER, self.size - self.dist_from_edge - RING_SEP//2, width=2)
		
		ob_rects = []
		for ob in self.obstacles:
			box_points = self.rings[ob.ring]
			bp = box_points.copy()
			bp.rotate(ob.theta)
			
			bp.move(CENTER.x, CENTER.y)
		
			rect = pygame.draw.polygon(screen, "red", bp.points)
			ob_rects.append(rect)
		return ob_rects


class Player(object):
	def __init__(self, box_radius, wheel_size):
		self.ring = 1
		
		self.box = pygame.Rect(0, 0, 2*box_radius, 2*box_radius)
		self.box.move_ip(-box_radius, -box_radius)
		self.box.move_ip(0, -wheel_size + 20)
		self.box.move_ip(CENTER.x, CENTER.y)
	
	def render(self, screen):
		return pygame.draw.rect(screen, "green", self.box)
	
	def move(self):
		if self.ring == 1:
			self.ring = 2
			self.box.move_ip(0, RING_SEP)
		else:
			self.ring = 1
			self.box.move_ip(0, -RING_SEP)
			

class ProgressBar(object):
	def __init__(self, x, y, width, height, total):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.green = pygame.Rect(x, y, self.width, self.height)
		self.gray = pygame.Rect(x, y, self.width, self.height)
		self.progress = 0
		self.total = total
	
	def increase(self):
		self.progress += 1
		self.gray.height = self.height * (1 - (self.progress / self.total))
		if self.progress == self.total:
			return True
		return  False
	
	def reset(self):
		self.progress = 0
	
	def render(self, screen):
		pygame.draw.rect(screen, "green", self.green)
		pygame.draw.rect(screen, "gray", self.gray)

SCREEN_DIM = (1280, 720)
CENTER = pygame.math.Vector2(SCREEN_DIM).elementwise() // 2
RING_SEP = 25

def victory():
	print("You Win!")

def main():

	pygame.init()
	screen = pygame.display.set_mode(SCREEN_DIM)
	clock = pygame.time.Clock()
	running = True

	wheel = Wheel()
	player = Player(wheel.box_radius, wheel.size)
	
	progress_bar_width = 30
	
	progress = ProgressBar(
		x=CENTER.x - wheel.size - 60,
		y=CENTER.y - wheel.size,
		width=30,
		height=2*wheel.size,
		total=360 * 2  # 2 full flawless wheel turns
	)


	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					player.move()

		wheel.rotate()
		ob_rects = wheel.render(screen)
		player_rect = player.render(screen)
		
		win = progress.increase()
		progress.render(screen)
		
		if win:
			victory()
			running = False
		
		
		if player_rect.collidelist(ob_rects) != -1:
			# Hit!
			GB = min(255, max(0, round(255 * (1-.5))))
			red_tint = (255, GB, GB)
			screen.fill(red_tint, special_flags = pygame.BLEND_MULT)
			progress.reset()

		pygame.display.flip()

		clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	main()
	#for i in range(5):
	#	print(generate_obstacles())

