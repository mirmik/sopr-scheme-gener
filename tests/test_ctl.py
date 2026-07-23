from sopr_scheme_gener.ctl import _json_value, _selector, build_parser


def test_selector_accepts_index_or_stable_id():
	assert _selector("3") == 3
	assert _selector("beams") == "beams"


def test_screenshot_command_defaults_to_canvas():
	args = build_parser().parse_args(["screenshot", "result.png"])
	assert args.target == "canvas"
	assert str(args.output) == "result.png"


def test_doc_set_parses_json_values_and_preserves_plain_strings():
	assert _json_value("2.5") == 2.5
	assert _json_value("true") is True
	assert _json_value("plain-text") == "plain-text"


def test_journal_commands_can_request_clear():
	assert build_parser().parse_args(["events", "--clear"]).clear is True
	assert build_parser().parse_args(["errors", "--clear"]).clear is True
