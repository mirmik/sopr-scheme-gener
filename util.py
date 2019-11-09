def text_prepare_ltext(l):
	if abs(float(l) - int(l)) < 0.0001:
		text_l = "{}l".format(int(l+0.1)) if l != 1 else "l"
	else:
		text_l = str(float(l)) + "l"
	return text_l					