import sys
from .gui import AlarmGUI

def main(args=None):
    args = args or sys.argv[1:]
    AlarmGUI.main(args)


if __name__ == "__main__":
    main(sys.argv[1:])

try:
    from fandango.doc import get_fn_autodoc

    __doc__ = get_fn_autodoc(__name__, vars())
except:
    # import traceback
    # traceback.print_exc()
    pass
