"""
This file belongs to the PANIC Alarm Suite, 
developed by ALBA Synchrotron for Tango Control System
GPL Licensed 
"""

from fandango.functional import *
from fandango import Catched
from panic.properties import SEVERITIES
# from panic.gui.utils import *
from panic.gui.utils import iValidatedWidget, getThemeIcon, SNAP_ALLOWED, \
    get_snap_api, AlarmPreview, get_user, trace
from panic.gui.utils import WindowManager  # Order of imports matters!
from panic.gui.alarmhistory import ahWidget
from panic.gui.devattrchange import dacWidget

from taurus.external.qt import Qt
from taurus.external.qt.QtGui import (
    QMenu, QMessageBox, QInputDialog, QLineEdit)
import traceback


class QAlarmManager(iValidatedWidget, object):

    def setCurrentAlarm(self, alarm):
        self._selected = [alarm]

    def getCurrentAlarm(self):
        return self._selected[0]

    def getSelectedAlarms(self, extend=False):
        return self._selected

    def connectContextMenu(self, 
            widget, 
            signal = 'customContextMenuRequested',
            expert = None):
        """ Connects the alarm actions context menu to the widget """
        
        if expert is not None:
            self.expert = expert
        self._manager = widget
        obj = getattr(widget, signal)
        obj.connect(self.onContextMenu)

    def contextMenuEvent(self, event):
        """ This method is called when the user right-clicks on the widget """
        # print('In contextMenuEvent(%s)' % str(event))
        if hasattr(self, '_manager'):
            self._manager.customContextMenuRequested.emit(event.pos())
        else:
            self.onContextMenu(event.pos())

    @Catched
    def onContextMenu(self, point):
        self.popMenu = QMenu(self)
        items = self.getSelectedAlarms(extend=False)
        print('In onContextMenu(%s)' % str([a.tag for a in items]))
        alarm = self.getCurrentAlarm()
        # self.popMenu.addAction(getThemeIcon("face-glasses"),
        # "Preview Attr. Values",self.onSelectAll)

        act = self.popMenu.addAction(getThemeIcon("face-glasses"),
                                     "See Alarm Details", self.onView)
        act.setEnabled(len(items) == 1)
        act = self.popMenu.addAction(getThemeIcon("accessories-calculator"),
            "Preview Formula/Values",
            lambda s=self: WindowManager.addWindow(s.showAlarmPreview())
            )
        act.setEnabled(len(items) == 1)
        # self.popMenu.addAction(getThemeIcon("view-refresh"),
        # "Sort/Update List",self.onSevFilter)

        act = self.popMenu.addAction(getThemeIcon("office-calendar"),
                                     "View History", self.viewHistory)
        act.setEnabled(SNAP_ALLOWED and len(items) == 1)

        sevMenu = self.popMenu.addMenu('Change Priority')
        for S in SEVERITIES:
            action = sevMenu.addAction(S)
            action.triggered.connect(lambda ks=items, sev=S, o=self: ChangeSeverity(parent=o, severity=sev))

        # Reset / Acknowledge options
        act = self.popMenu.addAction(getThemeIcon("edit-undo"),
                                     "Reset Alarm(s)", lambda s=self: ResetAlarm(s))
        act.setEnabled(any(i.active for i in items))

        if len([i.acknowledged for i in items]) in (len(items), 0):
            # if len(items)==1:
            self.popMenu.addAction(getThemeIcon("media-playback-pause"),
                                   "Acknowledge/Renounce Alarm(s)",
                                   lambda s=self: AcknowledgeAlarm(s))

        if len([i.disabled for i in items]) in (len(items), 0):
            # if len(items)==1:
            self.popMenu.addAction(getThemeIcon("dialog-error"),
                                   "Disable/Enable Alarm(s)",
                                   lambda s=self: ChangeDisabled(s))

        # Edit options
        if getattr(self, 'expert', None):
            self.popMenu.addSeparator()
            act = self.popMenu.addAction(
                getThemeIcon("accessories-text-editor"),
                "Edit Alarm", self.onEdit)
            act.setEnabled(len(items) == 1)
            act = self.popMenu.addAction(getThemeIcon("edit-copy"),
                                         "Clone Alarm", self.onClone)
            act.setEnabled(len(items) == 1)
            act = self.popMenu.addAction(getThemeIcon("edit-clear"),
                                         "Delete Alarm", self.onDelete)
            act.setEnabled(len(items) == 1)
            self.popMenu.addAction(getThemeIcon("applications-system"),
                                   "Advanced Config", lambda s=self: ShowConfig(s))
            self.popMenu.addSeparator()
            act = self.popMenu.addAction(
                getThemeIcon("accessories-text-editor"), "TestDevice",
                lambda d=alarm.device: testDevice(d))
            
            act = self.popMenu.addAction(
                getThemeIcon("applications-system"), "Restart Server",
                lambda d=alarm.device: restartServer(d))            

            act.setEnabled(len(items) == 1)

        # self.popMenu.addSeparator()
        # self.popMenu.addAction(getThemeIcon("process-stop"), "close App",self.close)

        if getattr(self, '_manager', None):
            self.popMenu.exec_(self._manager.mapToGlobal(point))
        else:
            self.popMenu.exec_(point)

    def onEdit(self, edit=True):
        from panic.gui.editor import AlarmForm
        alarm = self.getCurrentAlarm()
        print("AlarmGUI.onEdit(%s)" % alarm)
        forms = [f for f in WindowManager.WINDOWS
                 if isinstance(f, AlarmForm) 
                 and f.getCurrentAlarm().tag == alarm.tag]

        if forms:  # Bring existing forms to focus
            form = forms[0]
            form.enableEditForm(edit)
            form.hide()
            form.show()
        else:  # Create a new form
            form = WindowManager.addWindow(AlarmForm(self.parent()))
            # form.connect(form,Qt.SIGNAL('valueChanged'),self.hurry)
            if edit:
                form.onEdit(alarm)
            else:
                form.setAlarmData(alarm)
        form.show()
        return form

    def onView(self):
        return self.onEdit(edit=False)

    def onNew(self):
        try:
            trace('onNew()')
            if not self.api.devices:
                v = QMessageBox.warning(self, 'Warning',
                    'You should create a PyAlarm device first\n'
                    '(using jive or tools:AdvancedConfig)!', 
                    QMessageBox.Ok)
                return
            try:
                for item in self._manager.selectedItems():
                    item.setSelected(False)
            except:
                pass
            from panic.gui.editor import AlarmForm
            form = AlarmForm(self.parent())
            trace('form')
            # form.connect(form,Qt.SIGNAL('valueChanged'),self.hurry)
            form.onNew()
            form.show()
            return form
        except:
            traceback.print_exc()

    def onClone(self):
        alarm = self.getCurrentAlarm().tag
        trace("onClone(%s)" % alarm)
        new_tag, ok = QInputDialog.getText(self, 'Input dialog',
                                           'Please provide tag name for cloned alarm.',
                                           QLineEdit.Normal, alarm)
        if (ok and len(str(new_tag)) > 3):
            try:
                obj = self.api[alarm]
                self.api.add(str(new_tag), obj.device, formula=obj.formula,
                             description=obj.description,
                             receivers=obj.receivers,
                             severity=obj.severity)
                self.onReload()
            except Exception as e:
                QMessageBox.critical(self, "Error!", str(e),
                    QtGui.QMessageBox.Ok)
                trace(traceback.format_exc())

    def onDelete(self, tag=None, ask=True):
        tags = tag and [tag] or [getattr(r, 'tag', r)
                                 for r in self.getSelectedAlarms(extend=False)]
        if ask:
            v = QMessageBox.warning(None, 'Pending Changes',
                                    'The following alarms will be deleted:\n\t' + '\n\t'.join(tags),
                                    QMessageBox.Ok | QMessageBox.Cancel)
            if v == QMessageBox.Cancel:
                return

            self.setAllowedUsers(self.api.get_admins_for_alarm(
                len(tags) == 1 and tags[0]))
            if not self.validate('onDelete(%s)' % ([a for a in tags])):
                return

        if len(tags) > 1:
            print('-' * 80)
            [self.onDelete(tag, ask=False) for tag in tags]
        else:
            try:
                tag = tags[0]
                trace('onDelete(%s)' % tag)

                view = getattr(self, 'view', None)
                if view:
                    view.api.remove(tag)
                    view.apply_filters()
                    view.disconnect(tag)

                # removal from view must go first
                if self.api.has_tag(tag):
                    self.api.remove(tag)
                    self.changed = True                            

                from panic.gui.editor import AlarmForm
                [f.close() for f in WindowManager.WINDOWS
                 if isinstance(f, AlarmForm)
                 and f.getCurrentAlarm().tag == tag]

                self.onReload(clear_selection=True)
                trace('onDelete(%s): done' % tag)
            except:
                traceback.print_exc()

    def onReload(self, clear_selection=False):
        """ method to be implemented in subclasses"""
        trace('onReload():NotImplemented!', level=2)

    ###########################################################################

    def viewHistory(self):
        alarm = self.getCurrentAlarm().tag
        print('viewHistory(%s)' % str(alarm))

        if SNAP_ALLOWED and not self.snaps:
            self.snaps = get_snap_api()

        if self.snaps and self.snaps.get_context(alarm):
            self.ahApp = ahWidget()
            self.ahApp.show()
            # self.ahApp.setAlarmCombo(alarm=str(self._ui.listWidget.\
            # currentItem().text().split('|')[0]).strip(' '))
            self.ahApp.setAlarmCombo(alarm=alarm)
        else:
            v = QMessageBox.warning(None, 'Not Archived',
                                    'This alarm has not recorded history', QMessageBox.Ok)
            return

    def showAlarmPreview(self):
        form = AlarmPreview(tag=self.getCurrentAlarm(), parent=self.parent())
        form.show()
        return form


##############################################################################

def getTargetAlarms(obj, alarms=None, active=False):
    if alarms is None:
        from panic.gui.editor import AlarmForm
        if isinstance(obj, AlarmForm):
            alarms = [obj.getCurrentAlarm()]
        elif hasattr(obj, 'getSelectedAlarms'):
            alarms = [t for t in obj.getSelectedAlarms()
                      if (not active or t.active)]
    elif not isSequence(alarms):
        alarms = [alarms]
    return alarms


def testDevice(device):
    import os
    os.system('tg_devtest %s &' % device)

def restartServer(device):
    astor = fn.Astor(device) 
    devs = astor.get_all_devices()
    v = QMessageBox.warning(self, 'Warning',
                            'Following devices will be affected: \n%s'
                                % '\n'.join(devs),
                            QMessageBox.Ok | QMessageBox.Cancel)
    if v == QMessageBox.Cancel:
        return    
    astor.restart_servers()

def emitValueChanged(self):
    if hasattr(self, 'emitValueChanged'):
        self.emitValueChanged()
    elif hasattr(self, 'valueChanged'):
        self.valueChanged()
        # [o.get_acknowledged(force=True) for o in items]
    # [f.setAlarmData() for f in WindowManager.WINDOWS
    # if isinstance(f,AlarmForm)]
    # self.onFilter()


def ShowConfig(parent=None):
    dac = dacWidget(device=parent.getCurrentAlarm().device)
    WindowManager.addWindow(dac)
    dac.show()


def ResetAlarm(parent=None, alarm=None):
    try:
        self = parent
        alarms = getTargetAlarms(parent, alarm, active=True)
        action = 'RESET'
        text = 'The following alarms will be %s:\n\t' % action \
               + '\n\t'.join([t.tag for t in alarms])
        trace('In ResetAlarm(): %s' % text)
        text += '\n\n' + 'Must type a comment to continue:'

        for a in alarms:
            try:
                r = parent.api.evaluate(a.formula)
                if r:
                    v = QMessageBox.warning(self, 'Warning',
                                            '%s condition is still active' % a.tag
                                            + '. Do you want to reset it anyway?',
                                            QMessageBox.Ok | QMessageBox.Cancel)
                    if v == QMessageBox.Cancel:
                        return
                    else:
                        break
            except:
                traceback.print_exc()

        self.setAllowedUsers(self.api.get_admins_for_alarm(len(alarms) == 1
                                                           and alarms[0].tag))
        if not self.validate('%s(%s)' % (action, [a.tag for a in alarms])):
            raise Exception('Invalid login or password!')

        comment, ok = QInputDialog.getText(self, 'Input dialog', text)
        if not ok:
            return
        elif ok and len(str(comment)) < 4:
            raise Exception('comment was too short')
        comment = get_user() + ': ' + str(comment)
        for alarm in alarms:
            print('ResetAlarm(%s):%s' % (alarm.tag, comment))
            alarm.reset(comment)

        emitValueChanged(self)
    except:
        msg = traceback.format_exc()
        v = QMessageBox.warning(self, 'Warning', msg, QMessageBox.Ok)


def AcknowledgeAlarm(parent, alarm=None):
    try:
        self = parent
        min_comment, comment_error = 4, 'Comment too short!'
        login_error = 'Invalid login or password!'

        alarms = getTargetAlarms(parent, alarm, active=True)
        acks = len([a for a in alarms if a.acknowledged])
        action = 'ACKNOWLEDGED' if acks != len(alarms) else 'RENOUNCED'
        text = 'The following alarms will be %s,\n\t' % action \
               + '\n\t'.join([t.tag for t in alarms])
        trace('In %s(): %s' % (action, text))
        text += '\n\n' + 'Must type a comment to continue:'

        self.setAllowedUsers(self.api.get_admins_for_alarm(len(alarms) == 1
                                                           and alarms[0].tag))
        if not self.validate('%s(%s)' % (action, [a.tag for a in alarms])):
            raise Exception(login_error)

        comment, ok = QInputDialog.getText(self, 'Input dialog', text)
        if not ok:
            return
        elif ok and len(str(comment)) < min_comment:
            raise Exception(comment_error)

        comment = str(get_user() + ': ' + str(comment))

        for alarm in alarms:
            if not alarm.acknowledged and action == 'ACKNOWLEDGED':
                alarm.acknowledge(comment)
            elif alarm.acknowledged:
                alarm.renounce(comment)

        emitValueChanged(self)
    except Exception as e:
        if any(s in e.args for s in (login_error, comment_error)):
            msg = e.args[0]
        else:
            msg = traceback.format_exc()

        v = QMessageBox.warning(self, 'Warning', msg, QMessageBox.Ok)
        if comment_error in e.args:
            AcknowledgeAlarm(parent, alarm)


def ChangeDisabled(parent, alarm=None):
    try:
        self = parent
        min_comment, comment_error = 4, 'Comment too short!'
        alarms = getTargetAlarms(parent, alarm, active=False)
        check = len([a for a in alarms if not a.disabled])
        action = 'ENABLED' if check != len(alarms) else 'DISABLED'
        text = 'The following alarms will be %s,\n\t' % action \
               + '\n\t'.join([t.tag for t in alarms])
        trace('In %s(): %s' % (action, text))
        text += '\n\n' + 'Must type a comment to continue:'

        self.setAllowedUsers(self.api.get_admins_for_alarm(len(alarms) == 1
                                                           and alarms[0].tag))
        if not self.validate('%s(%s)' % (action, [a.tag for a in alarms])):
            raise Exception('Invalid login or password!')

        comment, ok = QInputDialog.getText(self, 'Input dialog', text)
        if not ok:
            return
        elif ok and len(str(comment)) < min_comment:
            raise Exception(comment_error)
        comment = get_user() + ': ' + str(comment)

        for alarm in alarms:
            if not alarm.disabled and action == 'DISABLED':
                print('Disabling %s' % alarm.tag)
                alarm.disable(comment)
            elif alarm.disabled:
                print('Enabling %s' % alarm.tag)
                alarm.enable(comment)

        emitValueChanged(self)
    except Exception as e:
        msg = traceback.format_exc() if comment_error not in e.args else e.args[0]
        v = QMessageBox.warning(self, 'Warning', msg, QMessageBox.Ok)
        
        if comment_error in e.args:
            ChangeDisabled(parent, alarm)


def ChangeSeverity(parent, severity, alarm=None):
    try:
        alarms = getTargetAlarms(parent, alarm, active=False)
        assert severity in SEVERITIES
        parent.setAllowedUsers(parent.api.get_admins_for_alarm(len(alarms) == 1
                                                               and alarms[0].tag))
        if not parent.validate('%s(%s)' % (
                'ChangePriority', [a.tag for a in alarms])):
            raise Exception('Invalid login or password!')

        for alarm in alarms:
            alarm.setup(severity=severity.upper(), write=True)
            from panic.gui.editor import AlarmForm
            [f.setAlarmData() for f in WindowManager.WINDOWS
             if isinstance(f, AlarmForm)]
        emitValueChanged(parent)

    except Exception:
        msg = traceback.format_exc()
        v = QMessageBox.warning(parent, 'Warning',
                                msg, QMessageBox.Ok)
        
