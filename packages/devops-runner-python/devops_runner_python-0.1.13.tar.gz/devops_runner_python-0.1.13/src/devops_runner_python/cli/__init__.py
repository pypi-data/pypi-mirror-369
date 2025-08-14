import argparse
import sys
from .run import run
from .run_many import run_many
from .uv import uv


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(prog='devops')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for the 'exec' command under 'devopspy'
    parser_exec = subparsers.add_parser('exec', help='Execute a command in a project')
    parser_exec.add_argument('--env', default='development', help='Environment to load (default: development)')
    parser_exec.add_argument('--in', dest='project', required=True, help='Specify the project')
    parser_exec.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the exec command')

    # Subparser for the 'run' command
    parser_run = subparsers.add_parser('run', help='Run a script in a specific project')
    parser_run.add_argument('--env', default='development', help='Environment to load (default: development)')
    parser_run.add_argument('arg', help='Argument for the run command, of the form "project:script"')
    parser_run.add_argument('script_args', nargs=argparse.REMAINDER, 
                         help='Additional arguments to pass to the script')

    # Subparser for the 'run-many' command
    parser_run_many = subparsers.add_parser('run-many', 
                                         help='Run a script concurrently in all projects that define it')
    parser_run_many.add_argument('--env', default='development', help='Environment to load (default: development)')
    parser_run_many.add_argument('script_name', help='Name of the script to run')
    parser_run_many.add_argument('--kill-others-on-fail', action='store_true', 
                              help='Kill all other running processes if one fails')
    parser_run_many.add_argument('script_args', nargs=argparse.REMAINDER, 
                              help='Additional arguments to pass to the script')

    # Subparser for the 'uv' command
    parser_uv = subparsers.add_parser('uv', help='Run arbitrary uv commands on all discovered projects')
    parser_uv.add_argument('--env', default='development', help='Environment to load (default: development)')
    parser_uv.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to uv')
    
    # Parse the arguments
    args = parser.parse_args()

    # Dispatch based on the command
    if args.command == 'exec':
        handle_exec(args.project, args.args, args.env)
    elif args.command == 'run':
        handle_run(args.arg, args.script_args, args.env)
    elif args.command == 'run-many':
        handle_run_many(args.script_name, args.kill_others_on_fail, args.script_args, args.env)
    elif args.command == 'uv':
        handle_uv(args.args)

def handle_exec(project, args, env):
    from .exec import exec
    exit_code = exec(project, env, args)
    if exit_code != 0:
        sys.exit(exit_code)

def handle_run(arg, script_args, env):
    # If the first argument is '--', remove it as it's just a separator
    if script_args and script_args[0] == '--':
        script_args = script_args[1:]
        
    exit_code = run(arg, env, script_args)
    if exit_code != 0:
        sys.exit(exit_code)

def handle_run_many(script_name, kill_others_on_fail, script_args, env):
    # If the first argument is '--', remove it as it's just a separator
    if script_args and script_args[0] == '--':
        script_args = script_args[1:]
        
    exit_code = run_many(script_name, env, kill_others_on_fail, script_args)
    if exit_code != 0:
        sys.exit(exit_code)

def handle_uv(args):
    exit_code = uv(args)
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == '__main__':
    main()