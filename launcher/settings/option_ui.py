import fsui
from fsbc.application import app
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.option import Option
from launcher.settings.override_warning import OverrideWarning
from launcher.ui.HelpButton import HelpButton


class OptionUI(object):
    @classmethod
    def create_group(cls, parent, name, description=None, help_button=True,
                     thin=False):
        group = fsui.Group(parent)
        group.layout = fsui.HorizontalLayout()
        if thin:
            thin_layout = fsui.VerticalLayout()
            thin_layout.add(group.layout, fill=True)
        option = Option.get(name)
        if description == "":
            description = gettext(option["description"])
        if description:
            group.label = fsui.Label(group, description + ":")
            group.layout.add(group.label, margin_right=10)
            group.layout.add(OverrideWarning(group, name), margin_right=10)

        if thin:
            group.layout = fsui.HorizontalLayout()
            if description:
                thin_layout.add(group.layout, fill=True, margin_top=6)
            else:
                thin_layout.add(group.layout, fill=True, margin_top=0)

        choice_values = []

        if description:
            default_tmpl = "{0} (*)"
            # default_tmpl = "Default - {0}"
        else:
            default_tmpl = "{0} (*)"
            # default_tmpl = "Default - {0}"

        if option["type"].lower() == "boolean":
            if option["default"] == "1":
                default_desc = gettext(default_tmpl).format(gettext("On"))
            elif option["default"] == "0":
                default_desc = gettext(default_tmpl).format(gettext("Off"))
            else:
                default_desc = gettext("Default")
            choice_values.append(("", default_desc))
            choice_values.append(("1", gettext("On")))
            choice_values.append(("0", gettext("Off")))

        elif option["type"].lower() == "choice":
            for i, value in enumerate(option["values"]):
                if option["default"] == value[0]:
                    default_desc = gettext(default_tmpl).format(
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
                Option.get(Option.LAUNCHER_FONT_SIZE)["default"] = \
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

            check_box.on_changed = on_checkbox

            def on_spin():
                val = spin_ctrl.get_value()
                val = max(option["min"], min(option["max"], val))
                LauncherSettings.set(name, str(val))

            spin_ctrl.on_changed = on_spin
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
            choice.on_changed = on_changed
            if thin:
                group.layout.add(choice, expand=True)
            else:
                group.layout.add_spacer(0, expand=True)
                group.layout.add(choice)
            group.widget = choice

        if help_button:
            option_url = (
                "https://fs-uae.net/docs/options/" + name.replace("_", "-"))
            group.help_button = HelpButton(
                parent, option_url)
            group.layout.add(group.help_button, margin_left=10)

        if thin:
            group.layout = thin_layout
        return group
