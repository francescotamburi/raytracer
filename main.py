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
		self.ray_vector -= self.x_shift*int(self.resolution[0]/2)
		self.ray_vector -= self.y_shift*int(self.resolution[1]/2)
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
				self.ray_vector += self.x_shift
				intersected_triangles.sort(key= lambda x:x[1]) #sort by distance
				#take closest triangle
				if intersected_triangles:
					surface = intersected_triangles[0][0]
					pixel = surface.get_colour()
				new_row.append(pixel)
			new_screen.append(new_row)
			self.ray_vector += -self.x_shift*int(self.resolution[0])
			self.ray_vector += self.y_shift
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
		objects.append(self)
	
	def calculate_triangles(self):
		A = self.position
		print("A = ", A.coordinates()) 
		B = A.translate(self.u)
		print("B = ", B.coordinates())
		C = B.translate(self.w)
		print("C = ", C.coordinates())
		D = C.translate(-self.u)
		print("D = ", D.coordinates())
		
		
		E = D.translate(self.v)
		print("E = ", E.coordinates())
		F = E.translate(-self.w)
		print("F = ", F.coordinates())
		G = F.translate(self.u)
		print("G = ", G.coordinates())
		H = G.translate(self.w)
		print("H = ", H.coordinates())
		
		ABC = triangle(A,B,C, (100,100,100))
		#ABC.normal = -self.v.normalize()
		CDA = triangle(C,D,A, (255,255,255))
		#CDA.normal = -self.v.normalize()
		
		CBG = triangle(C,B,G, (100,  0,  0))
		#CBG.normal = self.u.normalize()
		CGH = triangle(C,G,H, (255,  0,  0))
		#CGH.normal = self.u.normalize()
		
		EHG = triangle(E,H,G, (  0,  0,100))
		#EHG.normal = self.v.normalize()
		EGF = triangle(E,G,F, (  0,  0,255))
		#EGF.normal = self.v.normalize()
		
		EFD = triangle(E,F,D, (  0,100,  0))
		#EFD.normal = -self.u.normalize()
		ADF = triangle(A,D,F, (  0,255,  0))
		#ADF.normal = -self.u.normalize()
		
		CHD = triangle(C,H,D, (255,  0,255))
		#CHD.normal = self.w.normalize()
		EDH = triangle(E,D,H, (100,  0,100))
		#EDH.normal = self.w.normalize()
		
		BAF = triangle(B,A,F, (100,100,  0))
		#BAF.normal = -self.w.normalize()
		BFG = triangle(B,F,G, (255,255,  0))
		#BFG.normal = -self.w.normalize()
		
		self.triangles = [ABC,CDA,CBG,CGH,EHG,EGF,EFD,ADF,CHD,EDH,BAF,BFG]
	
	def rotate(self,a,b,c):
		self.u = self.u.rotate(a,b,c)
		self.v = self.v.rotate(a,b,c)
		self.w = self.w.rotate(a,b,c)
		print(self.u.components(), self.v.components(),self.w.components())
		self.calculate_triangles()

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



box = box(vertex(0,8,0), 10,10,10)
box.rotate(0,0,45)
#print(box.u.components(), box.v.components(), box.w.components())
#tri = tri(vertex(-1,1,0),vertex(1,1,0),vertex(0,1,1), (110,110,0))
camera = camera(vertex(-10,0,-10), vector(0,1,0), 120, (480,480), vector(1,0,0))
pixels = camera.cast_rays()
array = np.array(pixels, dtype=np.uint8)

#print(start, end)
#print((vector(1,2,3)+vector(1,3,2)).components())
new_image = Image.fromarray(array)
new_image.save('new.png')