from launcher.launcher_signal import LauncherSignal
import fsui as fsui
from ...i18n import gettext
from ...launcher_config import LauncherConfig
from ...options import Options
from ..HelpButton import HelpButton


class ChoiceConfigControl(fsui.Choice):

    def __init__(self, parent, option_name, choices):
        self.option_name = option_name
        # choices = [
        #     ("", gettext("Auto")),
        #     ("1", gettext("On")),
        #     ("0", gettext("Off"))]
        self.choice_values = [x[0] for x in choices]
        self.choice_labels = [x[1] for x in choices]
        super().__init__(parent, self.choice_labels)

        self.on_config(self.option_name, LauncherConfig.get(self.option_name))
        LauncherConfig.add_listener(self)

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        if key == self.option_name:
            print(key, self.option_name, value)
            for i, v in enumerate(self.choice_values):
                if v == value:
                    self.set_index(i)
                    break

        # FIXME: listen to implicit config also

    def on_changed(self):
        index = self.get_index()
        LauncherConfig.set(self.option_name, self.choice_values[index])


class BooleanConfigControl(ChoiceConfigControl):

    def __init__(self, parent, option_name):
        # choices =
        # self.choice_values = [x[0] for x in choices]
        # self.choice_labels = [x[1] for x in choices]

        super().__init__(parent, option_name, choices=[
            ("", gettext("Auto")),
            ("1", gettext("Enabled")),
            ("0", gettext("Disabled"))
        ])

        # self.on_config(self.option_name, Config.get(self.option_name))
        # Config.add_listener(self)
    #
    # def on_destroy(self):
    #     Config.remove_listener(self)
    #
    # def on_config(self, key, value):
    #     if key == self.option_name:
    #         print(key, self.option_name, value)
    #         for i, v in enumerate(self.choice_values):
    #             if v == value:
    #                 self.set_index(i)
    #                 break
    #
    #     # FIXME: listen to implicit config also
    #
    # def on_change(self):
    #     index = self.get_index()
    #     Config.set(self.option_name, self.choice_values[index])


class ConfigOptionUI(object):

    @classmethod
    def create_group(cls, parent, name):
        group = fsui.Group(parent)
        group.layout = fsui.HorizontalLayout()
        option = Options.get(name)
        group.label = fsui.Label(group, gettext(option["description"]) + ":")
        group.layout.add(group.label, margin_right=20)
        choice_values = []

        if option["type"].lower() == "boolean":
            # if option["default"] == "1":
            #     default_desc = gettext("Default ({0})").format(gettext("On"))
            # elif option["default"] == "0":
            #     default_desc = gettext("Default ({0})").format(gettext("Off"))
            # else:
            #     default_desc = gettext("Default")
            # choice_values.append(("", default_desc))
            # choice_values.append(("1", gettext("On")))
            # choice_values.append(("0", gettext("Off")))
            group.layout.add_spacer(0, expand=True)
            group.layout.add(BooleanConfigControl(group, name))

        elif option["type"].lower() == "choice":
            # for i, value in enumerate(option["values"]):
            #     if option["default"] == value[0]:
            #         default_desc = gettext("Default ({0})").format(
            #             gettext(value[1]))
            #         break
            # else:
            #     default_desc = gettext("Default")
            # choice_values.append(("", default_desc))
            # for option in option["values"]:
            #     choice_values.append((option[0], gettext(option[1])))

            group.layout.add_spacer(0, expand=True)
            choices = [("", gettext("Auto"))] + option["values"]
            group.layout.add(ChoiceConfigControl(group, name, choices))

        elif option["type"].lower() == "string":

            def on_changed():
                val = text_field.get_text()
                LauncherConfig.set(name, val.strip())

            text_field = fsui.TextField(group)
            # text_field.set_min_width(400)
            text_field.set_text(LauncherConfig.get(name))
            text_field.on_change = on_changed
            group.layout.add(text_field, expand=True)

        elif option["type"].lower() == "integer" and "min" in option \
                and "max" in option:
            current = LauncherConfig.get(name)
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
                    LauncherConfig.set(name, "")
                else:
                    spin_ctrl.enable()

            check_box.on_change = on_checkbox

            def on_spin():
                val = spin_ctrl.get_value()
                val = max(option["min"], min(option["max"], val))
                LauncherConfig.set(name, str(val))

            spin_ctrl.on_change = on_spin
            group.layout.add_spacer(0, expand=True)
            group.layout.add(check_box)
            group.layout.add(spin_ctrl, margin_left=10)

        if choice_values:

            def on_changed():
                index = choice.get_index()
                LauncherConfig.set(name, choice_values[index][0])

            choice_labels = [x[1] for x in choice_values]
            choice = fsui.Choice(group, choice_labels)
            current = LauncherConfig.get(name)
            for i, value in enumerate(choice_values):
                if current == value[0]:
                    choice.set_index(i)
                    break
            choice.on_change = on_changed
            group.layout.add_spacer(0, expand=True)
            group.layout.add(choice)
            group.widget = choice

        # group.help_button = HelpButton(
        #     parent, "http://fs-uae.net/doc/options#" + name)
        # group.layout.add(group.help_button, margin_left=10)

        return group
