def convert_and_trim_bb(image, rect,scale_factor):
	# extract the starting and ending (x, y)-coordinates of the
	# bounding box
	startX = int(rect.left()*scale_factor)
	startY = int(rect.top()*scale_factor)
	endX =int( rect.right()*scale_factor)
	endY = int(rect.bottom()*scale_factor)
	# ensure the bounding box coordinates fall within the spatial
	# dimensions of the image
	startX = max(0, startX)
	startY = max(0, startY)
	endX = min(endX, image.shape[1])
	endY = min(endY, image.shape[0])
	# compute the width and height of the bounding box
	w = endX - startX
	h = endY - startY
	# return our bounding box coordinates
	return (startX, startY, w, h)