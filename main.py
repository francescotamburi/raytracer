from primitives import *
import math
from PIL import Image
import numpy as np

global objects
objects = []

class camera(ray):
	def __init__(self, position, direction, fov, resolution, screen_x):
		self.point = position
		self.vector = direction.normalize()
		self.ray_vector = self.vector
		self.fov = math.radians(fov)
		self.resolution = resolution
		zero = (0,0,0)
		self.screen = [[zero for i in range(resolution[0])] for i in range(resolution[1])]
		self.set_pixel_vectors(screen_x, self.vector.cross(screen_x))
		#print("pixel shifts = ",self.x_shift.components(), ", ", self.y_shift.components())
	
	def set_pixel_vectors(self,x_direction,y_direction):
		##print("x: ",x_direction.normalize().components()," y: ",y_direction.normalize().components())
		pixel_shift  = math.tan(self.fov/2)/(self.resolution[0]/2)
		self.x_shift = x_direction.normalize() * pixel_shift	
		self.y_shift = y_direction.normalize() * pixel_shift
	
	def position(self):
		return self.point
	
	def direction(self):
		return self.vector
	
	def cast_rays(self):
		self.ray_vector += self.x_shift*int(self.resolution[0]/2)
		self.ray_vector += self.y_shift*int(self.resolution[1]/2)
		global start
		start = self.ray_vector.components()
		new_screen = []
		for row in self.screen:
			new_row = []
			for pixel in row:
				##print("raycast coordinates", self.ray_vector.components())
				intersected_triangles = []
				for obj in objects:
					for triangle in obj.triangles:
						if distance := self.intersection(triangle):
							intersected_triangles.append((triangle, distance))
				self.ray_vector -= self.x_shift
				intersected_triangles.sort(key= lambda x:x[1]) #sort by distance
				#take closest triangle
				if intersected_triangles:
					surface = intersected_triangles[0][0]
					pixel = surface.get_colour()
				new_row.append(pixel)
			new_screen.append(new_row)
			self.ray_vector += self.x_shift*int(self.resolution[0])
			self.ray_vector += -self.y_shift
		self.screen = new_screen
		global end
		end = self.ray_vector.components()
		return self.screen

class box:
	def __init__(self, position, u, v, w):
		self.position = position
		self.u = vector(1,0,0) * u
		self.v = vector(0,1,0) * v
		self.w = vector(0,0,1) * w
		self.calculate_triangles()
	
	def calculate_triangles(self):
		A = self.position
		B = A.translate(self.u)
		C = B.translate(self.v)
		D = C.translate(-self.u)
		E = D.translate(self.w)
		F = E.translate(-self.v)
		G = F.translate(self.u)
		H = G.translate(self.v)
		
		ABC = triangle(A,B,C, (250,0,0))
		ABC.normal = -self.w.normalize()
		CDA = triangle(C,D,A, (250,250,0))
		CDA.normal = -self.w.normalize()
		
		CBG = triangle(C,B,G, (0,250,0))
		CBG.normal = self.u.normalize()
		CGH = triangle(C,G,H, (0,250,250))
		CGH.normal = self.u.normalize()
		
		EGH = triangle(E,G,H, (0, 0, 250))
		EGH.normal = self.w.normalize()
		EGF = triangle(E,G,F, (250, 0, 250))
		EGF.normal = self.w.normalize()
		
		EDF = triangle(E,D,F, (250,250,250))
		EDF.normal = -self.u.normalize()
		ADF = triangle(A,D,F, (250,125,250))
		ADF.normal = -self.u.normalize()
		
		CHD = triangle(C,H,D, (250,125,150))
		CHD.normal = self.v.normalize()
		EDH = triangle(C,D,A, (20,125,250))
		EDH.normal = self.v.normalize()
		
		ABF = triangle(A,B,F, (250,125,0))
		ABF.normal = -self.v.normalize()
		BGF = triangle(B,G,F, (100,125,250))
		BGF.normal = -self.v.normalize()
		
		self.triangles = [ABC,CDA,CBG,CGH,EGH,EGF,EDF,ADF,CHD,EDH,ABF,BGF]
		
		objects.append(self)

class tri:
	def __init__(self, A,B,C, colour):
		self.triangles = [triangle(A,B,C, colour)]
		#print(self.triangles[0].normal.components())
		objects.append(self)


"""
class room(box):
	self.__init__(self, position, u, v, w):
		super().__init__(position, u, v, w)
		
		for tr in self.triangles:
			tr.normal = -tr.normal
"""



box = box(vertex(0,20,0), 10,10,10)
#tri = tri(vertex(-1,1,0),vertex(1,1,0),vertex(0,1,1), (110,110,0))
camera = camera(vertex(0,0,0), vector(0,1,0), 120, (48,48), vector(1,0,0))
pixels = camera.cast_rays()
array = np.array(pixels, dtype=np.uint8)

#print(start, end)
#print((vector(1,2,3)+vector(1,3,2)).components())
new_image = Image.fromarray(array)
new_image.save('new.png')