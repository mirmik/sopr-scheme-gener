def text_prepare_ltext(l, suffix="l"):
	if abs(float(l) - int(l)) < 0.0001:
		text_l = "{}{}".format(int(l+0.1), suffix) if l != 1 else suffix
	else:
		text_l = "{:.3}".format(l) + suffix
	return text_l					