import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import qInstallMessageHandler

from sopr_scheme_gener.app import build_parser, create_runtime


def test_switching_all_tasks_does_not_repaint_recursively_or_print_debug(capsys):
	args = build_parser().parse_args(["--no-maximize"])
	context = create_runtime(args)
	messages = []

	def collect_message(_message_type, _message_context, message):
		messages.append(message)

	previous_handler = qInstallMessageHandler(collect_message)
	try:
		for spec in context.task_specs:
			context.controller.select(spec.identifier)
			context.app.processEvents()
			context.canvas.grab()
			context.app.processEvents()
	finally:
		qInstallMessageHandler(previous_handler)
		context.window.close()

	output = capsys.readouterr()
	assert "Recursive repaint detected" not in "\n".join(messages)
	assert "SectionContainer" not in output.out
