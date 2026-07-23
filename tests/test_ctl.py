from sopr_scheme_gener.ctl import _selector, build_parser


def test_selector_accepts_index_or_stable_id():
	assert _selector("3") == 3
	assert _selector("beams") == "beams"


def test_screenshot_command_defaults_to_canvas():
	args = build_parser().parse_args(["screenshot", "result.png"])
	assert args.target == "canvas"
	assert str(args.output) == "result.png"
