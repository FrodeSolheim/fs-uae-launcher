import fsui
from fsbc.application import app
from fsui.context import get_theme
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.option import Option
from launcher.settings.override_warning import OptionWarning, OverrideWarning
from system.classes.optionhelpbutton import OptionHelpButton


class OptionUI(object):
    @staticmethod
    def create_option_label(parent, label):
        label = fsui.HeadingLabel(parent, label)
        theme = get_theme(parent)
        label.set_min_height(theme.widget_height())
        # label.set_background_color(fsui.Color(0xFF0000))
        return label

    @staticmethod
    def add_divider(parent, layout, top_margin=12, bottom_margin=12):
        # return
        import fsui

        panel = fsui.Panel(parent)
        panel.set_background_color(fsui.Color(0xA2A2A2))
        panel.set_min_height(1)
        layout.add(
            panel,
            fill=True,
            margin_top=top_margin,
            margin_bottom=bottom_margin,
        )

    @classmethod
    def create_group(
        cls,
        parent,
        name,
        description=None,
        help_button=True,
        thin=False,
        warnings=None,
    ):
        group = fsui.Panel(parent)
        group.layout = fsui.HorizontalLayout()
        if thin:
            thin_layout = fsui.VerticalLayout()
            thin_layout.add(group.layout, fill=True)
        option = Option.get(name)
        if not description:
            description = gettext(option["description"])
        if description:
            # group.label = fsui.HeadingLabel(group, description + ":")
            group.label = cls.create_option_label(group, description)
            group.layout.add(group.label, margin_right=10)
            group.layout.add(OverrideWarning(group, name), margin_right=10)
        if warnings is not None:
            for warning in warnings:
                group.layout.add(
                    OptionWarning(group, warning), margin_right=10
                )

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
                        gettext(value[1])
                    )
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

        elif (
            option["type"].lower() == "integer"
            and "min" in option
            and "max" in option
        ):
            current = LauncherSettings.get(name)

            if name == Option.LAUNCHER_FONT_SIZE:
                font = app.qapplication.font()
                Option.get(Option.LAUNCHER_FONT_SIZE)[
                    "default"
                ] = font.pointSize()

            current_int = int(option["default"])
            if current:
                try:
                    current_int = int(current)
                except ValueError:
                    pass
            current_int = max(option["min"], min(option["max"], current_int))
            check_box = fsui.CheckBox(group, gettext("Default"))
            spin_ctrl = fsui.SpinCtrl(
                group, option["min"], option["max"], current_int
            )
            if current == "":
                check_box.check()
                spin_ctrl.set_enabled(False)

            def on_checkbox():
                if check_box.checked():
                    spin_ctrl.set_value(int(option["default"]))
                    spin_ctrl.set_enabled(False)
                    LauncherSettings.set(name, "")
                else:
                    spin_ctrl.set_enabled()

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
                index = choice.index()
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
            # group.widget = choice

        if help_button:
            # group.help_button = OptionHelpButton(parent, name)
            group.help_button = OptionHelpButton(group, name)
            # option_url = "https://fs-uae.net/docs/options/" + name.replace(
            #     "_", "-"
            # )
            # group.help_button = HelpButton(parent, option_url)
            group.layout.add(group.help_button, fill=True, margin_left=10)

        if thin:
            group.layout = thin_layout
        return group
