import traceback

import fsui
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.option import Option
from launcher.ui.HelpButton import HelpButton
from launcher.ui.behaviors import OptionsBehavior


class OptionWidgetFactory(object):
    """Factory for creating user interface groups for options."""

    # noinspection PyShadowingBuiltins
    def __init__(self, check=False, help=False, settings=False):
        self.check = check
        self.help = help
        self.label_spacing = 10
        if settings:
            self.options = LauncherSettings
        else:
            self.options = LauncherConfig

    # noinspection PyShadowingBuiltins
    def create(self, parent, name, text=None, check=None, help=None):
        option = Option.get(name)
        return create_option_group(
            parent, self.options, option, name, option["type"].lower(),
            text if text is not None else gettext(option["description"]),
            check if check is not None else self.check,
            help if help is not None else self.help,
            self.label_spacing)


def create_option_group(
        parent, options, option, key, option_type, option_text,
        use_checkbox, use_help_button, label_spacing):
    group = fsui.Group(parent)
    group.layout = fsui.HorizontalLayout()

    if use_checkbox:
        group.layout.add(
            OptionCheckBox(group, option_text + ":", options, key),
            margin_right=label_spacing)
    else:
        group.layout.add(
            fsui.Label(group, option_text + ":"),
            margin_right=label_spacing)

    choice_values = []

    if option_type == "boolean":
        group.layout.add_spacer(0, expand=True)
        group.layout.add(BooleanChoiceControl(
            group, options, key, use_checkbox=use_checkbox))

    elif option_type == "choice":
        group.layout.add_spacer(0, expand=True)
        choices = option["values"]
        # if use_checkbox:
        #     choices,insert(("", gettext("Auto")))
        group.layout.add(ChoiceControl(
            group, options, key, choices, use_checkbox=use_checkbox))

    elif option_type == "string":

        def on_changed():
            val = text_field.get_text()
            LauncherConfig.set(key, val.strip())

        text_field = fsui.TextField(group)
        # text_field.set_min_width(400)
        text_field.set_text(LauncherConfig.get(key))
        text_field.on_changed = on_changed
        group.layout.add(text_field, expand=True)

    elif option["type"].lower() == "integer" and "min" in option \
            and "max" in option:
        assert use_checkbox

        spin_ctrl = SpinValueControl(
            group, options, key, option["min"], option["max"])

        # current = LauncherConfig.get(key)
        # current_int = int(option["default"])
        # if current:
        #     try:
        #         current_int = int(current)
        #     except ValueError:
        #         pass
        # current_int = max(option["min"], min(option["max"], current_int))
        # check_box = fsui.CheckBox(group, gettext("Default"))
        # spin_ctrl = fsui.SpinCtrl(group, option["min"],
        #                           option["max"], current_int)
        # if current == "":
        #     check_box.check()
        #     spin_ctrl.disable()

        # def on_checkbox():
        #     if check_box.is_checked():
        #         spin_ctrl.set_value(int(option["default"]))
        #         spin_ctrl.disable()
        #         LauncherConfig.set(key, "")
        #     else:
        #         spin_ctrl.enable()
        #
        # check_box.on_changed = on_checkbox
        #
        # def on_spin():
        #     val = spin_ctrl.get_value()
        #     val = max(option["min"], min(option["max"], val))
        #     LauncherConfig.set(key, str(val))

        # spin_ctrl.on_changed = on_spin
        # group.layout.add(check_box)
        group.layout.add_spacer(0, expand=True)
        group.layout.add(spin_ctrl, margin_left=10)

    if choice_values:

        def on_changed():
            index = choice.get_index()
            LauncherConfig.set(key, choice_values[index][0])

        choice_labels = [x[1] for x in choice_values]
        choice = fsui.Choice(group, choice_labels)
        current = LauncherConfig.get(key)
        for i, value in enumerate(choice_values):
            if current == value[0]:
                choice.set_index(i)
                break
        choice.on_changed = on_changed
        group.layout.add_spacer(0, expand=True)
        group.layout.add(choice)
        group.widget = choice

    if use_help_button:
        help_button = HelpButton(
            parent, "https://fs-uae.net/options#" + key)
        group.layout.add(help_button, margin_left=10)

    return group


class ConfigWidgetFactory(OptionWidgetFactory):
    """Factory for creating user interface groups for config options."""

    # noinspection PyShadowingBuiltins
    def __init__(self, check=True, help=False):
        super().__init__(check=check, help=help)


class SettingsWidgetFactory(OptionWidgetFactory):
    """Factory for creating user interface groups for settings."""

    # noinspection PyShadowingBuiltins
    def __init__(self, check=False, help=True):
        super().__init__(check=check, help=help, settings=True)


def default_value(key):
    option = Option.get(key)
    return option["default"]


class OptionCheckBox(fsui.CheckBox):
    def __init__(self, parent, text, options, key):
        super().__init__(parent, text)
        self.implicit_value = ""
        self.options = options
        self.key = key
        setattr(self, "on_{}_option".format(key), self.on_explicit_option)
        setattr(self, "on___implicit_{}_option".format(key),
                self.on_implicit_option)
        OptionsBehavior(self, options, [key, "__implicit_" + key])

    def on_explicit_option(self, value):
        if value:
            if not self.is_checked():
                with self.changed.inhibit:
                    self.check(True)
        else:
            if self.is_checked():
                with self.changed.inhibit:
                    self.check(False)

    def on_implicit_option(self, value):
        self.implicit_value = value

    def on_changed(self):
        if self.is_checked():
            if self.options.get(self.key) == "":
                print("-- setting option to default value")
                value = self.implicit_value
                if not value:
                    value = default_value(self.key)
                self.options.set(self.key, value)
        else:
            self.options.set(self.key, "")


class ChoiceControl(fsui.Choice):
    def __init__(self, parent, options, key, choices, use_checkbox=False):
        if not use_checkbox:
            choices.insert(0, ("", gettext("Auto")))
        self.choice_values = [x[0] for x in choices]
        self.choice_labels = [x[1] for x in choices]
        super().__init__(parent, self.choice_labels)
        self.implicit_value = ""
        self.options = options
        self.key = key
        self.use_checkbox = use_checkbox
        self.invalid_index = None

        setattr(self, "on_{}_option".format(key), self.on_explicit_option)
        setattr(self, "on___implicit_{}_option".format(key),
                self.on_implicit_option)
        OptionsBehavior(self, options, [key, "__implicit_" + key])

    def on_explicit_option(self, value):
        print("ChoiceControl", self.key, value)
        self.set_from_value(value)
        if self.use_checkbox:
            self.set_enabled(bool(value))

    def on_implicit_option(self, value):
        self.implicit_value = value
        if self.use_checkbox:
            self.set_from_value()
        else:
            self.update_auto_item()

    def set_from_value(self, value=None):
        if value is None:
            value = self.options.get(self.key)
        if self.use_checkbox:
            if value == "":
                value = self.implicit_value
                # FIXME: This can be removed if/when implicit value always
                # takes into account the default value.
                if not value:
                    value = default_value(self.key)
        for i, v in enumerate(self.choice_values):
            if v == value:
                with self.changed.inhibit:
                    self.set_index(i)
                if self.invalid_index is not None and i != self.invalid_index:
                    self.remove_invalid_item()
                break
        else:
            print("WARNING: Could not find value", value)
            self.set_invalid_item(value)

    def set_invalid_item(self, value):
        text = "???"
        if self.invalid_index is None:
            self.invalid_index = self.add_item(text)
            self.choice_values.append("")
            self.choice_labels.append("")
        self.choice_values[-1] = value
        self.choice_labels[-1] = text
        with self.changed.inhibit:
            self.set_index(self.invalid_index)

    def remove_invalid_item(self):
        assert self.invalid_index is not None
        self.remove_item(self.invalid_index)
        del self.choice_values[-1]
        del self.choice_labels[-1]
        self.invalid_index = None

    def on_changed(self):
        index = self.get_index()
        self.options.set(self.key, self.choice_values[index])
        if not self.use_checkbox:
            self.update_auto_item()

    def update_auto_item(self):
        # if self.use_checkbox:
        #     # Checkboxes are used, so there isn't an auto entry!
        #     # return
        #     # if self.options.get(self.key):
        #     #     self.set_from_value(self.implicit_value)
        #     pass
        # else:
        if self.get_index() == 0 and self.implicit_value:
            text = gettext("Auto - {}".format(self.implicit_value))
        else:
            text = gettext("Auto")
        self.set_item_text(0, text)


class BooleanChoiceControl(ChoiceControl):
    def __init__(self, parent, options, key, use_checkbox=False):
        choices = [
            ("1", gettext("Enabled")),
            ("0", gettext("Disabled"))
        ]
        # if not use_checkbox:
        #     choices.insert(0, ("", gettext("Auto")))
        super().__init__(
            parent, options, key, choices, use_checkbox=use_checkbox)


class SpinValueControl(fsui.SpinCtrl):
    # noinspection PyShadowingBuiltins
    def __init__(self, parent, options, key, min, max):
        # value = self.int_value(options.get(key))
        # try:
        #     int_value = int(value)
        # except ValueError:
        #     int_value = self.min

        super().__init__(parent, min, max, min)
        self.min = min
        self.max = max
        self.implicit_value = ""
        self.options = options
        self.key = key

        setattr(self, "on_{}_option".format(key), self.on_explicit_option)
        setattr(self, "on___implicit_{}_option".format(key),
                self.on_implicit_option)
        OptionsBehavior(self, options, [key, "__implicit_" + key])

    def on_changed(self):
        val = self.get_value()
        val = max(self.min, min(self.max, val))
        self.options.set(self.key, str(val))

    def on_explicit_option(self, value):
        print("SpinValueControl", self.key, value)
        self.set_from_value(value)
        # if self.use_checkbox:
        self.set_enabled(bool(value))

    def on_implicit_option(self, value):
        print("SpinValueControl implicit value", value)
        self.implicit_value = value
        self.set_from_value()

    def int_value(self, value):
        try:
            int_value = int(value)
        except ValueError:
            traceback.print_exc()
            int_value = self.min
        # FIXME: Check range?
        return int_value

    def set_from_value(self, value=None):
        if value is None:
            value = self.options.get(self.key)
        if value == "":
            value = self.implicit_value
            # FIXME: This can be removed if/when implicit value always
            # takes into account the default value.
            if not value:
                value = default_value(self.key)
        with self.changed.inhibit:
            self.set_value(self.int_value(value))

# current = LauncherConfig.get(key)
# current_int = int(option["default"])
# if current:
#     try:
#         current_int = int(current)
#     except ValueError:
#         pass
# current_int = max(option["min"], min(option["max"], current_int))
# check_box = fsui.CheckBox(group, gettext("Default"))
# spin_ctrl = fsui.SpinCtrl(group, option["min"],
#                           option["max"], current_int)
#
# if current == "":
#     check_box.check()
#     spin_ctrl.disable()
#
#
# def on_checkbox():
#     if check_box.is_checked():
#         spin_ctrl.set_value(int(option["default"]))
#         spin_ctrl.disable()
#         LauncherConfig.set(key, "")
#     else:
#         spin_ctrl.enable()
#
#
# check_box.on_changed = on_checkbox
#
#
# def on_spin():
#     val = spin_ctrl.get_value()
#     val = max(option["min"], min(option["max"], val))
#     LauncherConfig.set(key, str(val))
