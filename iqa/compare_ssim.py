#coding:utf-8

import sys
from PIL import Image
from ssim import *
import numpy as np

if __name__=="__main__":
	image1 = Image.open(sys.argv[1]).convert("L")
	image2 = Image.open(sys.argv[2]).convert("L")

	print calc_f_ssim(
		np.asarray(image1),
		np.asarray(image2),
		1e-3,
		1e-3,
		1e-3,
		calc_np_ssim
	)
