import math

def dot(u, v):
	return u.a * v.a + u.b * v.b + u.c * v.c

def cross(u, v):
	a = u.b * v.c - u.c * v.b
	b = u.c * v.a - u.a * v.c
	c = u.a * v.b - u.b * v.a
	return a,b,c

def magnitude(a,b,c):
	return (a**2 + b**2 + c**2)**.5

def normalize(a,b,c):
	mag = magnitude(a,b,c)
	return a/mag, b/mag, c/mag
	
def triangle_area(A,B,C):
	abc = cross(vector_2p(B,A), vector_2p(C,A))
	return magnitude(abc[0], abc[1], abc[2])/2

class vertex:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	
	def coordinates(self):
		return self.x, self.y, self.z
	
	def translate(self, v):
		return vertex(self.x+v.a, self.y+v.b, self.z+v.c)

global origin 
origin = vertex(0,0,0)

class matrix:
	def __init__(self, matrix):
		self.matrix = matrix
		self.dimension = self.dimension()
	
	def dimension(self):
		row_length = len(self.matrix[0])
		for i in self.matrix:
			if len(i)!= row_length:
				raise Exception("Not a matrix, row length not equal")
		return len(self.matrix), row_length
	
	def transpose(self):
		M_size = self.dimension
		result = []
		for i in range(M_size[1]):
			row = []
			for j in range(M_size[0]):
				row.append(self.matrix[j][i])
			result.append(row)
		return result
	
	def __mul__(self, obj):
		if isinstance(obj, (int,float)):
			result = self.matrix
			for row in result:
				for i in row:
					i *= obj
		elif isinstance(obj, vector) and self.dimension[0] == 3:
			result = [0,0,0]
			i = 0
			for row in self.matrix:
				result[i] = obj.a * row[0] + obj.b * row[1] + obj.c * row[2]
				i+=1
			result = vector(result[0], result[1], result[2])
		elif isinstance(obj, matrix):
			M_size = self.dimension
			N_size = obj.dimension
			result = []
			N_T = obj.transpose()
			if M_size[0] == N_size[1]:
				for i in range(M_size[1]):
					row = []
					for j in range(N_size[0]):
						r = self.matrix[i]
						c = N_T[j]
						s = 0
						for k in range(len(r)):
							s += r[k]*c[k]
						row.append(s)
					result.append(row)
				result = matrix(result)
			else:
				raise Exception("Can't multiply matrices, row M =/= column N")
		return result


class vector:
	def __init__(self, a, b, c):
		self.a = a
		self.b = b
		self.c = c
	
	def components(self):
		return self.a, self.b, self.c
	
	def magnitude(self):
		self.magnitude = magnitude(self.a, self.b, self.c)
		return self.magnitude
	
	def normalize(self):
		a, b, c = normalize(self.a, self.b, self.c)
		return vector(a,b,c)
	
	def cross(self, v):
		a,b,c = cross(self, v)
		return vector(a,b,c)
	
	def dot(self, v):
		return dot(self, v)
	
	def __add__(self, v):
		return vector(self.a+v.a, self.b+v.b, self.c+v.c)
	
	def __sub__(self, v):
		v = -v
		return(self.__add__(v))
	
	def __mul__(self, l):
		return vector(self.a*l, self.b*l, self.c*l)
	
	def __neg__(self):
		return vector(-self.a, -self.b, -self.c)
	
	#remember, all rotations are anti-clockwise
	def rotate(self, alpha, beta, gamma):
		alpha = math.radians(alpha)
		beta  = math.radians(beta)
		gamma = math.radians(gamma)
		rotation_matrices = []
		R = matrix(((1,0,0),(0,1,0),(0,0,1)))
		if alpha != 0:
			rotation_matrices.append(
				matrix((
					(math.cos(alpha), -math.sin(alpha), 0),
					(math.sin(alpha),  math.cos(alpha), 0),
					(              0,                0, 1)
				))
			)
		if beta != 0:
			rotation_matrices.append(
				matrix((
					( math.cos(beta), 0, math.sin(beta)),
					(              0, 1,              0),
					(-math.sin(beta), 0, math.cos(beta))
				))
			)
		if gamma != 0:
			rotation_matrices.append(
				matrix((
					( 1,               0,                0),
					( 0, math.cos(gamma), -math.sin(gamma)),
					( 0, math.sin(gamma),  math.cos(gamma))
				))
			)	
		
		for M in rotation_matrices:
			R = M * R
		
		return(R*self)

class vector_2p(vector):
	def __init__(self, A, B):
		self.a = A.x - B.x
		self.b = A.y - B.y
		self.c = A.z - B.z

class triangle:
	def __init__(self, A, B, C, colour):
		self.A = A
		self.B = B
		self.C = C
		self.normal()
		self.colour = colour
	
	def points(self):
		return self.A, self.B, self.C
	
	def normal(self):
		u = vector_2p(self.A,self.B)
		v = vector_2p(self.A,self.C)
		cross_product = u.cross(v)
		self.area = cross_product.magnitude()/2 
		self.normal = cross_product.normalize()
	
	def get_colour(self, **kwargs):
		return self.colour

class ray:
	def __init__(self, point, vector):
		self.point = point
		self.ray_vector = vector
	
	def intersection(self, triangle):
		if dot(self.ray_vector, triangle.normal) >= 0:
			#print("facing different directions")
			##print(self.ray_vector.components(), triangle.normal.components(), dot(self.ray_vector, triangle.normal))
			return False
		if True:
			#plane-ray intersection
			D = triangle.normal.dot(vector_2p(origin,triangle.A))
			t = -(triangle.normal.dot(vector_2p(origin,self.point)) + D)/triangle.normal.dot(self.ray_vector)
			##print("t=",t)
			if t <= 0:
				#print("behind camera")
				return False
				
			plane_intersection = origin.translate(self.ray_vector * t)
			#print("plane_intersection: ", plane_intersection.coordinates())
			
			##print("__________")
			AB = vector_2p(triangle.A, triangle.B)
			##print(AB.components())
			AP = vector_2p(triangle.A, plane_intersection)
			##print(AP.components())
			##print("(ABxAP).N = ")
			if triangle.normal.dot(AB.cross(AP)) <= 0:
				#print("not left AB")
				return False
			
			BC = vector_2p(triangle.B, triangle.C)
			BP = vector_2p(triangle.B, plane_intersection)
			if triangle.normal.dot(BC.cross(BP)) <= 0:
				#print("not left BC")
				return False
			
			CA = vector_2p(triangle.C, triangle.A)
			CP = vector_2p(triangle.C, plane_intersection)
			if triangle.normal.dot(CA.cross(CP)) <= 0:
				#print("not left CA")
				return False
			
			else:
				#print("yes")
				return t
			
			"""
			#barycentric coordinates
			APC = triangle_area(triangle.A, triangle.C, plane_intersection)
			if APC > triangle.area:
				return False
				
			else:
				APB = triangle_area(triangle.A, triangle.B, plane_intersection)
				if APB > triangle.area:
					return False
					
				elif APB + APC - triangle.area < 0:
					return False
					
				else:
					return t  #idr what this does , vector(APB, APC, triangle.area - APB + APC) * triangle_area**-1	
			"""
			
			