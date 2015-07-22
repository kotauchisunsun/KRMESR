import sqlite3
import numpy as np
from utils import bicubic
from PIL import Image

class image_db(object):
	def __init__(self,path,window_size,precision):
		self.conn        = sqlite3.connect(path,isolation_level="EXLUSIVE")
		self.window_size = window_size
		self.pixel_num   = window_size ** 2
		self.precision   = precision
		self.coefficient = 10 ** (self.precision)

		self.cursor = self.conn.cursor()
		self.cursor.execute("select * from sqlite_master");
		self.is_new = False

		self.insert_buffer = []

		self.cache = dict()

		if len(self.cursor.fetchall()) == 0:
			self.is_new = True
			self.cursor.execute("""
create table patch (
mean real, 
std  real,
mean_idx int,
std_idx  int,
%s
)
""" % (
	",\n".join(
		c + " real"
		for c
		in self.get_pixel_column()
	)			
))
			self.cursor.execute("create index meanindex on patch(mean_idx)")
			self.cursor.execute("create index stdindex  on patch(std_idx)")
			self.conn.commit()

		self.cursor.execute("PRAGMA cache_size = 500000")
		self.conn.commit()

	def get_pixel_column(self):
		return [
			"p_%02d" % i
			for i
			in range(self.pixel_num)
		]

	def __enter__(self):
		self.cursor.execute("begin")

	def __exit__(self, type, value, traceback):
		if len(self.insert_buffer) > 0:
			self.multiple_insert(self.insert_buffer)
		self.conn.commit()

	def multiple_insert(self,images):
		param_num = 4 + len(images[0])

		stmt = """
insert into patch values 
(%s);
""" % (",".join("?"*param_num))
	 	
		params = [
				(lambda mean,std:(
						mean,
	  					std,					
						int(mean*self.coefficient),
						int(std*self.coefficient)
					) + tuple(image)
				 )(np.mean(image),np.std(image))
				for image
			    in images	
			]

	 	self.cursor.executemany(
			stmt,
			params
		)


	def insert(self,image):
		self.insert_buffer.append(image)
		if len(self.insert_buffer) > 100000:
			self.multiple_insert(self.insert_buffer)
			self.insert_buffer = []

	def get_mean_idx(self,image):
		return int(np.mean(image) * self.coefficient)

	def get_std_idx(self,image):
		return int(np.std(image) * self.coefficient)

	def select_fast(self,image,p,lim,num):
		mean = np.mean(image)
		std  = np.std(image)
		n    = len(self.get_pixel_column())

		mean_idx = self.get_mean_idx(image)
		std_idx  = self.get_std_idx(image)

		column_params = ",".join(self.get_pixel_column())

		result = None

		if not self.cache.has_key(mean_idx):
			del self.cache
			self.cursor.execute("select mean,std,%s from patch where mean_idx = %d"%(column_params,mean_idx))
			result = data = np.array(self.cursor.fetchall())
			self.cache = {mean_idx:data}
		else:
			result = self.cache[mean_idx]

		target = result[
					  ( ( mean + lim ) > result[:,0] )
					& ( ( mean - lim ) < result[:,0] )
					& ( ( std  + lim ) > result[:,1] )
					& ( ( std  - lim ) < result[:,1] )
				]

		l = len(target)
		diff = ( target[:,2:] - target[:,0].reshape((l,1)) )
		sigma_xy = np.mean(( image - mean ) * diff,axis=1)
		numerator = 2 * mean * target[:,0] * 2 * sigma_xy + 1e-7
		denominator =  ( (mean ** 2) + (target[:,0] ** 2) ) * ( ( std **2 ) + ( target[:,1] ** 2 ) ) + 1e-7

		target = target[numerator/denominator > p][:,2:]

		if len(target) > num:
			indexs = np.array(([True] * num+ [False]*(len(target) - num)))
			np.random.shuffle(indexs)
			
			return target[indexs]
		else:
			return target


def make_db(db,image_list,sample_num):
	window_size = db.window_size

	c = 0

	with db:
		for image in image_list:
			height,width = image.shape

			image = image / 255.0

			xs = np.random.choice(range(width-window_size)  , sample_num)
			ys = np.random.choice(range(height-window_size) , sample_num)
			pair = np.array([xs,ys]).T

			for bx,by in pair:
				window_img = image[by:by+window_size,bx:bx+window_size].reshape((window_size*window_size,))

				if c % 10000 == 0:
					print c/(float(sample_num) * len(image_list))

				db.insert(window_img)
				c += 1

if __name__ == "__main__":
	import sys
	from config import *

	image_list = []

	try:
		while 1:
			image_list.append(raw_input())
	except EOFError as e:
		pass

	for index in range(3):
		_db_name = db_name[index]
		db = image_db(_db_name,window_size,index_precision)
		make_db(
			db,
			[ np.asarray(bicubic(Image.open(name).convert("YCbCr"),scale))[:,:,index] for name in image_list],
			sample_num
		)
