import cadquery as cq
from ocp_vscode import show
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults
set_port(3939)

solid = cq.importers.importStep("dataset/sample_1.step").val()

show(solid)
