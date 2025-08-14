import subprocess


def execute(*args, run_with_bash=True, **kwargs):
    if run_with_bash:
        cmd_args = ['/bin/bash', '-c']
        cmd_args.extend(args)
    else:
        cmd_args = args
    return subprocess.run(cmd_args, text=True, capture_output=True, **kwargs)
