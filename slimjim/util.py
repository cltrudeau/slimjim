# slimjim.util
import subprocess

# ===========================================================================

def common_args(parser):
    parser.add_argument('-r', '--raw', action='store_true', help=("Type exactly "
        "what is seen, don't compensate for auto-indent in the target"))
    parser.add_argument('app', help=('Name of app to target keystrokes to'))


def validate_app(target_app):
    proc = subprocess.run(['/usr/local/bin/sendkeys', 'apps'],
        capture_output=True)

    if not target_app in str(proc.stdout):
        print((f'Target app "{target_app}" not found by sendkeys, run '
            '"sendkeys apps" to see a full list of possible targets'))
        quit()
