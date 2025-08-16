import json
import logging
import os
import subprocess
from argparse import ArgumentParser
from fnmatch import fnmatch
from glob import glob
from json.decoder import JSONDecodeError
from typing import Any
from typing import List
from typing import Sequence
from typing import Tuple

from .requirements_utils import sanitize_requirements

logger = logging.getLogger(__name__)


class AbortException(Exception):
    pass


def add_common_parameters(parser: ArgumentParser, action: str):
    parser.add_argument(
        "workflows",
        type=str,
        help=f"Workflow(s) to {action} (e.g. JSON filename)",
        nargs="+",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="The 'workflow' argument refers to the name of a test graph",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="The 'workflow' argument is a pattern to be search",
    )


def add_subworkflows_parameters(parser: ArgumentParser):
    parser.add_argument(
        "--workflow-dir",
        type=str,
        default="",
        dest="root_dir",
        help="Directory of sub-workflows (current working directory by default)",
    )
    parser.add_argument(
        "--workflow-module",
        type=str,
        default="",
        dest="root_module",
        help="Python module of sub-workflows (current working directory by default)",
    )


def add_ewoks_inputs_parameters(parser: ArgumentParser):
    parser.add_argument(
        "-p",
        "--parameter",
        dest="parameters",
        action="append",
        default=[],
        metavar="[NODE:]NAME=VALUE",
        help="Input variable for a particular node (or all start nodes when missing)",
    )
    parser.add_argument(
        "--input-node-id",
        dest="node_attr",
        type=str,
        choices=["id", "label", "taskid"],
        default="id",
        help="The NODE attribute used when specifying an input parameter with [NODE:]NAME=VALUE",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        choices=["start", "all"],
        default="start",
        help="Inputs without a specific node are given to either all start nodes or all nodes",
    )


def parse_ewoks_inputs_parameters(args):
    return [
        parse_parameter(input_item, args.node_attr, args.inputs == "all")
        for input_item in args.parameters
    ]


def parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except JSONDecodeError:
        return value


_NODE_ATTR_MAP = {"id": "id", "label": "label", "taskid": "task_identifier"}


def parse_parameter(input_item: str, node_attr: str, all: bool) -> dict:
    """The format of `input_item` is `"[NODE]:name=value"`"""
    node_and_name, _, value = input_item.partition("=")
    a, sep, b = node_and_name.partition(":")
    if sep:
        node = a
        var_name = b
    else:
        node = None
        var_name = a
    var_value = parse_value(value)
    if node is None:
        return {"all": all, "name": var_name, "value": var_value}
    return {
        _NODE_ATTR_MAP[node_attr]: node,
        "name": var_name,
        "value": var_value,
    }


def parse_option(option: str) -> Tuple[str, Any]:
    option, _, value = option.partition("=")
    return option, parse_value(value)


def parse_workflows(args) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    if args.test:
        return _parse_test_workflows(args.workflows, args.search)
    return _parse_workflows(args.workflows, args.search)


def _parse_workflows(workflows: List[str], search: bool) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    if not search:
        return workflows, workflows
    parsed_workflows = list()
    files = (filename for workflow in workflows for filename in glob(workflow))
    for filename in sorted(files, key=os.path.getmtime):
        if filename not in parsed_workflows:
            parsed_workflows.append(filename)
    return parsed_workflows, parsed_workflows


def _parse_test_workflows(
    workflows: List[str], search: bool
) -> Tuple[List[str], List[dict]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    from ewokscore.tests.examples.graphs import get_graph
    from ewokscore.tests.examples.graphs import graph_names

    test_workflows = list(graph_names())
    if search:
        parsed_workflows = list()
        for workflow in workflows:
            for test_graph in test_workflows:
                if fnmatch(test_graph, workflow) and test_graph not in parsed_workflows:
                    parsed_workflows.append(test_graph)
    else:
        for workflow in workflows:
            if workflow not in test_workflows:
                raise RuntimeError(
                    f"Test graph '{workflow}' does not exist: {test_workflows}"
                )
        parsed_workflows = workflows

    graphs = [get_graph(workflow)[0] for workflow in parsed_workflows]
    return parsed_workflows, graphs


def parse_destinations(args):
    dest_dirname = os.path.dirname(args.destination)
    basename = os.path.basename(args.destination)
    dest_basename, dest_ext = os.path.splitext(basename)
    if not dest_ext:
        dest_ext = dest_basename
        dest_basename = ""
        if not dest_ext.startswith("."):
            dest_ext = f".{dest_ext}"

    if len(args.workflows) == 1 and dest_basename:
        return [os.path.join(dest_dirname, f"{dest_basename}{dest_ext}")]

    destinations = list()
    for workflow in args.workflows:
        basename, _ = os.path.splitext(os.path.basename(workflow))
        destination = os.path.join(dest_dirname, f"{basename}{dest_basename}{dest_ext}")
        destinations.append(destination)

    return destinations


def pip_install(requirements: Sequence[str], python_path: str) -> int:
    requirements, warnings = sanitize_requirements(requirements)
    for warning in warnings:
        logger.warning(warning)
    # https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
    return subprocess.check_call([python_path, "-m", "pip", "install", *requirements])
