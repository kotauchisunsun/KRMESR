#coding:utf-8
from collections import OrderedDict

def calc_ssim(xs,ys,c1,c2,c3):
	n = float(len(xs))
	assert(n==len(ys))

	mx = sum(xs) / n
	my = sum(ys) / n

	vx  = ( sum((x-mx)**2 for x in xs) / n ) ** 0.5
	vy  = ( sum((y-my)**2 for y in ys) / n ) ** 0.5

	vxy = ( sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / n ) 

	m = ( ( 2 * mx * my + c1 ) / ( mx * mx + my * my + c1 ) )
	v = ( ( 2 * vx * vy + c2 ) / ( vx * vx + vy * vy + c2 ) )
	r = ( ( vxy + c3 ) / ( vx*vy + c3 ) )

	return m * v * r

def calc_np_ssim(xs,ys,c1,c2,c3):
	import numpy as np
	n = float(len(xs))
	assert(n==len(ys))

	xs = np.array(xs)
	ys = np.array(ys)

	mx = xs.mean()
	my = ys.mean()

	vx  = xs.std()
	vy  = ys.std()

	vxy = ((xs-mx)*(ys-my)).mean()

	m = ( ( 2 * mx * my + c1 ) / ( mx * mx + my * my + c1 ) )
	v = ( ( 2 * vx * vy + c2 ) / ( vx * vx + vy * vy + c2 ) )
	r = ( ( vxy + c3 ) / ( vx*vy + c3 ) )

	return m * v * r

def calc_f_ssim(xs,ys,c1,c2,c3,ssim_func):
	hight = len(xs)
	width = len(xs[0])

	window = 11

	h8 = hight/window
	w8 = width/window

	return sum(
		ssim_func(
			[
				xs[yi*window+i][xi*window+j]
				for i in range(window)
				for j in range(window)	
			],
			[
				ys[yi*window+i][xi*window+j]
				for i in range(window)
				for j in range(window)	
			],
			c1,c2,c3
		)
		for yi in range(h8)
		for xi in range(w8)
	) / float(h8*w8)

