import PIL
from PIL import Image
import sys
from scipy import misc

def bicubic(image,scale):
	width,height = image.size

	width = int(width*scale)
	height = int(height*scale)

	return image.resize((width,height),PIL.Image.BICUBIC)

if __name__ == "__main__":
	scale = float(sys.argv[1])
	image = Image.open(sys.argv[2])
	out   = sys.argv[3]

	misc.toimage(bicubic(image,scale)).save(out)

