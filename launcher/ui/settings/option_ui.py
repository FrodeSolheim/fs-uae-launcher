import fsui as fsui
from ...i18n import gettext
from ...launcher_settings import LauncherSettings
from ...options import Options, Option
from ..HelpButton import HelpButton
from .override_warning import OverrideWarning
from fsbc.application import app


class OptionUI(object):

    @classmethod
    def create_group(cls, parent, name):
        group = fsui.Group(parent)
        group.layout = fsui.HorizontalLayout()
        option = Options.get(name)
        group.label = fsui.Label(group, gettext(option["description"]) + ":")
        group.layout.add(group.label, margin_right=10)
        group.layout.add(OverrideWarning(group, name), margin_right=10)
        choice_values = []

        if option["type"].lower() == "boolean":
            if option["default"] == "1":
                default_desc = gettext("Default - {0}").format(gettext("On"))
            elif option["default"] == "0":
                default_desc = gettext("Default - {0}").format(gettext("Off"))
            else:
                default_desc = gettext("Default")
            choice_values.append(("", default_desc))
            choice_values.append(("1", gettext("On")))
            choice_values.append(("0", gettext("Off")))

        elif option["type"].lower() == "choice":
            for i, value in enumerate(option["values"]):
                if option["default"] == value[0]:
                    default_desc = gettext("Default - {0}").format(
                        gettext(value[1]))
                    break
            else:
                default_desc = gettext("Default")
            choice_values.append(("", default_desc))
            for option in option["values"]:
                choice_values.append((option[0], gettext(option[1])))

        elif option["type"].lower() == "string":

            def on_changed():
                val = text_field.get_text()
                LauncherSettings.set(name, val.strip())

            text_field = fsui.TextField(group)
            # text_field.set_min_width(400)
            text_field.set_text(LauncherSettings.get(name))
            text_field.on_changed = on_changed
            group.layout.add(text_field, expand=True)

        elif option["type"].lower() == "integer" and "min" in option \
                and "max" in option:
            current = LauncherSettings.get(name)

            if name == Option.LAUNCHER_FONT_SIZE:
                font = app.qapplication.font()
                Options.get(Option.LAUNCHER_FONT_SIZE)["default"] = \
                    font.pointSize()

            current_int = int(option["default"])
            if current:
                try:
                    current_int = int(current)
                except ValueError:
                    pass
            current_int = max(option["min"], min(option["max"], current_int))
            check_box = fsui.CheckBox(group, gettext("Default"))
            spin_ctrl = fsui.SpinCtrl(group, option["min"],
                                      option["max"], current_int)
            if current == "":
                check_box.check()
                spin_ctrl.disable()

            def on_checkbox():
                if check_box.is_checked():
                    spin_ctrl.set_value(int(option["default"]))
                    spin_ctrl.disable()
                    LauncherSettings.set(name, "")
                else:
                    spin_ctrl.enable()

            check_box.on_change = on_checkbox

            def on_spin():
                val = spin_ctrl.get_value()
                val = max(option["min"], min(option["max"], val))
                LauncherSettings.set(name, str(val))

            spin_ctrl.on_change = on_spin
            group.layout.add_spacer(0, expand=True)
            group.layout.add(check_box)
            group.layout.add(spin_ctrl, margin_left=10)

        if choice_values:

            def on_changed():
                index = choice.get_index()
                LauncherSettings.set(name, choice_values[index][0])

            choice_labels = [x[1] for x in choice_values]
            choice = fsui.Choice(group, choice_labels)
            current = LauncherSettings.get(name)
            for i, value in enumerate(choice_values):
                if current == value[0]:
                    choice.set_index(i)
                    break
            choice.on_change = on_changed
            group.layout.add_spacer(0, expand=True)
            group.layout.add(choice)
            group.widget = choice

        group.help_button = HelpButton(
            parent, "http://fs-uae.net/doc/options#" + name)
        group.layout.add(group.help_button, margin_left=10)

        return group
