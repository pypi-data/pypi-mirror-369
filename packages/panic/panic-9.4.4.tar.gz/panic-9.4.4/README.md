# PANIC, a Python Alarm System for TANGO

## Table of Contents
* [Description](#description)  
* [Other Project Pages](#other-project-pages)  
* [PyAlarm Device Server](#pyalarm-device-server)  
* [Panic GUI](#panic-gui)  
* [Authors](#authors)  
* [License and Warranty](#license-and-warranty)  

## Description

PANIC is a set of tools (API, Tango device server, user interface) that provides:

- Periodic evaluation of a set of conditions.  
- Notification (email, SMS, pop-up, speakers)  
- Logging of events (files, Tango Snapshots)  
- Automated actions (Tango commands / attributes)  
- Tools for configuration/visualization  

The `panic` package contains the Python `AlarmAPI` for managing the `PyAlarm` device servers from a client application or a Python shell. The `panic` module is used by **PyAlarm**, **Panic Toolbar**, and **Panic GUI**.

> **Note:** PANIC is tested on Linux only. Windows/macOS may not be fully supported in the master branch.

Optional `panic` submodules:

- `panic.ds`: PyAlarm device server  
- `panic.gui`: Placeholder for the PanicGUI application  

Documentation PANIC v6: [http://www.pythonhosted.org/panic](http://www.pythonhosted.org/panic)  
Recipes: [https://gitlab.com/tango-controls/PANIC/tree/documentation/doc/recipes](https://gitlab.com/tango-controls/PANIC/tree/documentation/doc/recipes)  
Latest release: [https://gitlab.com/tango-controls/PANIC/releases](https://github.com/tango-controls/PANIC/releases)  

## Other Project Pages

- [http://www.tango-controls.org/community/projects/panic-alarm-system](http://www.tango-controls.org/community/projects/panic-alarm-system)  
- [https://gitlab.com/tango-controls/panic](https://github.com/tango-controls/panic)  
- [https://pypi.python.org/pypi/panic](https://pypi.python.org/pypi/panic)  

## PyAlarm Device Server

`panic.ds.PyAlarm` Device Class

PyAlarm is the alarm device server used by the ALBA Alarm System. It requires the `PyTango` and `Fandango` modules, 
both available from [https://gitlab.com/tango-controls](https://gitlab.com/tango-controls) and [https://pypi.python.org/pypi].

Some configuration panels in the GUI require `PyAlarm` to be available in the `PYTHONPATH`. To do so, you can:

- Add the `PyAlarm.py` folder to the `PYTHONPATH` variable, or  
- Copy the `PyAlarm.py` file within the `panic` folder so it can be loaded as part of the module.  

## Panic GUI

`panic.gui.AlarmGUI` Class

Panic is an application for controlling and managing alarms. It depends on the `panic` and `taurus` libraries.

It allows users to:

- Visualize existing alarms  
- Add, edit, or delete alarms  
- Edit alarm names, descriptions, devices, and formulas  
- View alarm history  
- Edit the phonebook  
- Manipulate device settings  

## Authors

Sergi Rubio  
ALBA Synchrotron (2006–2025)

## License and Warranty

See the [LICENSE file](https://gitlab.com/tango-controls/fandango/blob/documentation/LICENSE)