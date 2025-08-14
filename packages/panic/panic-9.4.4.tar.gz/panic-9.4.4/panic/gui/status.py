"""
This file belongs to the PANIC Alarm Suite, 
developed by ALBA Synchrotron for Tango Control System
GPL Licensed 
"""

from fandango import defaultdict
from fandango.qt import getApplication
from fandango.tango import check_device

import panic
import sys

from taurus.external.qt import Qt


def get_panic_status(*args):
    if args and isinstance(args[0], panic.AlarmAPI):
        api = args[0]
    else:
        api = panic.api(*args)

    txt = ['Panic({}) Status:'.format(str(api.filters))]
    txt.append('\t{:d} alarms in db'.format(len(api)))
    txt.append('\t{:d} devices in db'.format(len(api.devices)))
    txt.append('')

    states = defaultdict(list)
    [states[check_device(d)].append(d) for d in api.devices]
    for s, v in sorted(states.items()):
        txt.append('{:d} devices in {} state'.format(len(v), s))
        ds = ['{} ({:d})'.format(d, len(api.devices[d].alarms)) for d in sorted(v)]
        txt.append('\t{}'.format(', '.join(ds)))

        return '\n'.join(txt)

    class PanicStatus(Qt.QTextBrowser):

        def __init__(self, *args, **kwargs):
            """
            args passed to QWidget
            kwargs passed to updateStyle()
            """
            Qt.QWidget.__init__(self, *args)
            self.load(**kwargs)
            self.updateStyle(**kwargs)

        def load(self, **kwargs):
            self.filters = kwargs.get('filters')
            self.api = panic.api(self.filters)

        def updateStyle(self, **kwargs):
            self.setText(get_panic_status(self.api))

    def main(*args):
        args = args or sys.argv[1:]
        if '--raw' in args:
            print(get_panic_status(
                [a for a in args if not a.startswith('-')][-1:]))
        else:
            qapp = getApplication()
            w = PanicStatus()
            w.show()
            sys.exit(qapp.exec_())

    if __name__ == '__main__':
        main()
