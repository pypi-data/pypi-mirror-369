import logging

from nomnomdata.engine import Engine, Parameter, ParameterGroup
from nomnomdata.engine.parameters import Int, String

logger = logging.getLogger("engine.hello_world")

engine = Engine(
    uuid="CHANGE-ME-PLEASE",
    alias="Hello World Sample",
    description="Demonstrates basic app structure and functionality.",
    categories=["general"],
)


@engine.action(
    display_name="Hello World",
    description="Prints a greeting multiple times in the Task execution log.",
)
@engine.parameter_group(
    name="general_parameters",
    display_name="General Parameters",
    description="Parameters for Hello World",
    parameter_group=ParameterGroup(
        Parameter(
            type=Int(),
            name="repeat",
            display_name="Repeat",
            description="Specify how many times to print.",
            default=1,
            required=True,
        ),
        Parameter(
            type=String(),
            name="name",
            display_name="Name",
            description="Specify a name to print instead of World.",
            required=False,
        ),
    ),
)
def hello_world(parameters):
    i = 0
    x = f"Hello {parameters.get('name') or 'World'}"
    while i < parameters["repeat"]:
        logger.info(x)
        i += 1
    return i, x
