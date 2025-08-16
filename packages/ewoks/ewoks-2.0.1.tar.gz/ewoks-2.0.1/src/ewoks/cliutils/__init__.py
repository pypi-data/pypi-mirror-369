from . import cli_convert_utils
from . import cli_execute_utils
from . import cli_install_utils
from . import cli_log_utils
from . import cli_show_utils
from . import cli_submit_utils


def add_execute_parameters(parser, shell=False):
    if shell:
        cli_log_utils.add_log_parameters(parser)
    cli_execute_utils.add_execute_parameters(parser)


def apply_execute_parameters(args, shell=False):
    if shell:
        cli_log_utils.apply_log_parameters(args)
    cli_execute_utils.apply_execute_parameters(args)


def add_convert_parameters(parser, shell=False):
    if shell:
        cli_log_utils.add_log_parameters(parser)
    cli_convert_utils.add_convert_parameters(parser)


def apply_convert_parameters(args, shell=False):
    if shell:
        cli_log_utils.apply_log_parameters(args)
    cli_convert_utils.apply_convert_parameters(args)


def add_submit_parameters(parser, shell=False):
    if shell:
        cli_log_utils.add_log_parameters(parser)
    cli_submit_utils.add_submit_parameters(parser)


def apply_submit_parameters(args, shell=False):
    if shell:
        cli_log_utils.apply_log_parameters(args)
    cli_submit_utils.apply_submit_parameters(args)


def add_install_parameters(parser, shell=False):
    if shell:
        # Show logs of install for better UX
        cli_log_utils.add_log_parameters(parser, default="info")
    cli_install_utils.add_install_parameters(parser)


def apply_install_parameters(args, shell=False):
    if shell:
        cli_log_utils.apply_log_parameters(args)
    cli_install_utils.apply_install_parameters(args)


def add_show_parameters(parser, shell=False):
    if shell:
        cli_log_utils.add_log_parameters(parser)
    cli_show_utils.add_show_parameters(parser)


def apply_show_parameters(args, shell=False):
    if shell:
        cli_log_utils.apply_log_parameters(args)
    cli_show_utils.apply_show_parameters(args)
