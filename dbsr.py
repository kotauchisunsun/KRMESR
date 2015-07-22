#coding:utf-8
import PIL
from PIL import Image
import numpy as np

from scipy import misc
from image_db import image_db,make_db
from config import *
from utils import bicubic

def db_super_resolution(db,image,index,scale,p):
	width,height = image.size
	window_size  = db.window_size
	bias         = window_size / 2

	width = int(width*scale)
	height = int(height*scale)

	image = image.resize((width,height),PIL.Image.BICUBIC)

	image = np.asarray(image)[:,:,index] / 255.0

	data = [[[ image[j][i] ] for i in range(width)] for j in range(height)]

	step = 2

	def return_data(p_data):
		return [
			[
				np.mean(a) if len(a) > 0 else 0.0
				for a
				in  l
			]
			for l
			in p_data
		]

	from bisect import insort_right

	job_list = []

	for i in range(bias, height - bias, step):
		for j in range(bias , width - bias, step):

			x = j - bias
			y = i - bias
				
			patch  = image[y:y+window_size,x:x+window_size].reshape((window_size*window_size,))

			mean_idx = db.get_mean_idx(patch)
			std_idx  = db.get_std_idx(patch)

		 	decision_value = np.std(patch) / 0.5
			if decision_value > 0.5 or np.random.random() < decision_value:
				insort_right(job_list,(mean_idx,np.std(patch),std_idx,x,y))


	for i,(m,_s,s,x,y) in enumerate(reversed(job_list)):
		patch  = image[y:y+window_size,x:x+window_size].reshape((window_size*window_size,))

		patch_list = db.select_fast(patch,p,1e-2,30)
		if i % 10 == 0:
			print "rest:",len(job_list)-i
			print _s
			print x,y,m,s,index
			print len(patch_list)
			print "end"

		for pp in patch_list:
			for c in range(len(pp)):
				iy = c / window_size
				ix = c % window_size

				data[y + iy][x + ix].append(pp[c])
		
		if i%1000 == 0:
			print "call"
			misc.toimage(return_data(data)).save("test.png")
	

	return return_data(data)


import sys
if __name__=="__main__":

	name      = sys.argv[1]
	out_name  = sys.argv[2]
	image     =  Image.open(name).convert("YCbCr")

	out = np.array(bicubic(image,scale))

	for index in range(3):
		db = image_db(db_name[index],window_size,index_precision)
		data = 255.0 * np.array(db_super_resolution(db,image,index,scale,0.95))
		out[:,:,index] = data

	misc.toimage(out, mode="YCbCr").convert("RGB").save(out_name)

