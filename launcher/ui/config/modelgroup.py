import fsui
from fsbc import settings
from fsbc.util import unused
from fsgs import openretro
from fsgs.amiga.amiga import Amiga
from fsgs.context import fsgs
from launcher.cd_manager import CDManager
from launcher.floppy_manager import FloppyManager
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.option import Option
from launcher.panels.additionalconfigpanel import CustomConfigButton
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import (
    AMIGA_PLATFORMS,
    AmigaShowBehavior,
)
from launcher.ui.config.ConfigCheckBox import ConfigCheckBox
from launcher.ui.options import ConfigWidgetFactory


class ModelGroup(fsui.Group):
    # FIXME: remove with_more_button=True
    def __init__(self, parent, with_more_button=True):
        unused(with_more_button)
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.model_ids = [x["id"] for x in Amiga.models if "/" not in x["id"]]
        self.model_titles = [
            x["title"] for x in Amiga.models if "/" not in x["id"]
        ]

        self.sub_model_ids = []
        self.sub_model_titles = []
        self.sub_model_updating = False

        self.model_choice = fsui.Choice(self, self.model_titles)
        # AmigaEnableBehavior(self.model_choice)
        self.sub_model_choice = fsui.Choice(self, self.sub_model_titles)
        # AmigaEnableBehavior(self.sub_model_choice)
        self.accuracy_label = fsui.Label(self, gettext("Accuracy:"))
        self.accuracy_choice = fsui.Choice(
            self, [gettext("High"), gettext("Medium"), gettext("Low")]
        )
        # AmigaEnableBehavior(self.accuracy_choice)
        self.ntsc_checkbox = ConfigCheckBox(self, "NTSC", Option.NTSC_MODE)

        AmigaShowBehavior(self.accuracy_label)
        AmigaShowBehavior(self.accuracy_choice)
        AmigaShowBehavior(self.ntsc_checkbox)

        # if fs_uae_launcher.ui.get_screen_size()[1] > 768:
        # self.layout.add(heading_label, margin=10)
        # self.layout.add_spacer(0)

        self.model_title_layout = fsui.HorizontalLayout()
        self.layout.add(self.model_title_layout, fill=True)

        if openretro or settings.get(Option.PLATFORMS_FEATURE) == "1":
            heading_label = fsui.HeadingLabel(
                self, gettext("Platform & Model")
            )
            self.model_title_layout.add(heading_label, margin=10)
            # platform_group = ConfigWidgetFactory(
            #     check=False, label=False).create(self, Option.PLATFORM)
            # self.model_title_layout.add(platform_group, margin_left=20)
            # Adding label to get the vertical spacing correct.
            # heading_label = fsui.HeadingLabel(self, "")
            # self.model_title_layout.add(heading_label, margin=10)
        else:
            heading_label = fsui.HeadingLabel(self, gettext("Amiga Model"))
            self.model_title_layout.add(heading_label, margin=10)

        self.model_title_layout.add_spacer(0, expand=True)
        self.model_title_layout.add(
            self.ntsc_checkbox, expand=False, margin_left=10, margin_right=10
        )
        self.model_title_layout.add_spacer(20)

        self.model_title_layout.add(self.accuracy_label, margin_right=10)
        self.model_title_layout.add(self.accuracy_choice, margin_right=10)
        self.model_title_layout.add(CustomConfigButton(self), margin_right=10)

        self.model_layout = fsui.HorizontalLayout()

        def dummy_min_width():
            return 0

        # Not sure why this is needed, but on startup, the min width
        # seems to be set too large due to something in the model layout.
        self.model_layout.get_min_width = dummy_min_width
        self.layout.add(self.model_layout, fill=True)

        if openretro or settings.get(Option.PLATFORMS_FEATURE) == "1":
            platform_group = ConfigWidgetFactory(
                check=False, label=False
            ).create(self, Option.PLATFORM)
            self.model_layout.add(platform_group, margin=10)
            pass

        self.other_model_choice = ModelChoice(self)
        self.model_layout.add(self.other_model_choice, expand=True, margin=10)

        self.model_layout.add(self.model_choice, expand=False, margin=10)
        AmigaShowBehavior(self.model_choice)
        self.model_layout.add(self.sub_model_choice, expand=True, margin=10)
        AmigaShowBehavior(self.sub_model_choice)

        ConfigBehavior(
            self, [Option.ACCURACY, Option.AMIGA_MODEL, Option.PLATFORM]
        )

        self.model_choice.on_changed = self.on_model_changed
        self.sub_model_choice.on_changed = self.on_sub_model_changed
        self.accuracy_choice.on_changed = self.on_accuracy_changed

    def on_platform_config(self, _):
        # Update layout after widgets have been shown/hidden.
        self.model_title_layout.update()
        self.model_layout.update()

    def on_model_changed(self):
        print("ModelGroup.on_model_change\n")
        index = self.model_choice.get_index()
        model = self.model_ids[index]
        if model == "A500":
            # The default model (A500) can be specified with the empty string
            model = ""
        LauncherConfig.set("amiga_model", model)
        # Config.update_kickstart()
        # if Amiga.is_cd_based(Config):
        #     FloppyManager.clear_all()
        # else:
        #     CDManager.clear_all()

    def on_sub_model_changed(self):
        print("ModelGroup.on_sub_model_change\n")
        if self.sub_model_updating:
            print("sub model list is currently updating")
            return
        index = self.sub_model_choice.get_index()
        # if index == 0:
        #     # The default model (A500) can be specified with the empty string
        #     model = ""
        # else:
        model = self.model_ids[self.model_choice.get_index()]
        sub_model = self.sub_model_ids[index]
        if sub_model:
            LauncherConfig.set("amiga_model", model + "/" + sub_model)
        else:
            LauncherConfig.set("amiga_model", model)

        if Amiga.is_cd_based(LauncherConfig):
            FloppyManager.clear_all()
        else:
            CDManager.clear_all()

    def on_accuracy_changed(self):
        index = self.accuracy_choice.get_index()
        if index == 0:
            LauncherConfig.set("accuracy", "")
        else:
            LauncherConfig.set("accuracy", str(1 - index))

    def update_sub_models(self, model_id, sub_model_id):
        sub_model_index = 0
        model_id_s = model_id + "/"
        self.sub_model_ids.clear()
        self.sub_model_titles.clear()

        for i, config in enumerate(Amiga.models):
            if config["id"] == model_id:
                self.sub_model_ids.append("")
                self.sub_model_titles.append(config["subtitle"])
            elif config["id"].startswith(model_id_s):
                self.sub_model_ids.append(config["id"].split("/", 1)[1])
                self.sub_model_titles.append(config["subtitle"])
            else:
                continue
            if sub_model_id == self.sub_model_ids[-1]:
                sub_model_index = len(self.sub_model_ids) - 1

        self.sub_model_choice.clear()
        for title in self.sub_model_titles:
            self.sub_model_choice.add_item(title)
        self.sub_model_choice.enable(
            LauncherConfig.get(Option.PLATFORM) in AMIGA_PLATFORMS
            and len(self.sub_model_ids) > 1
        )
        return sub_model_index

    def on_amiga_model_config(self, value):
        if value == "":
            value = "A500"

        if "/" in value:
            model_id, sub_model_id = value.split("/", 1)
        else:
            model_id = value
            sub_model_id = ""

        model_index = 0
        sub_model_index = 0
        self.sub_model_updating = True
        for i, config in enumerate(Amiga.models_config):
            if config == value:
                # self.model_choice.set_index(i)
                # find main model index
                model_index = self.model_ids.index(model_id)
                sub_model_index = self.update_sub_models(
                    model_id, sub_model_id
                )
                # model_index = i
                break
        # else:
        #    print("FIXME: could not set model")
        self.model_choice.set_index(model_index)
        self.sub_model_choice.set_index(sub_model_index)
        self.sub_model_updating = False

    def on_accuracy_config(self, value):
        if not value:
            index = 0
        else:
            index = 1 - int(value)
        self.accuracy_choice.set_index(index)


class ModelChoice(fsui.Choice):
    def __init__(self, parent):
        self._choice_values = []
        self._choice_labels = []
        super().__init__(parent, self._choice_labels)
        self._platform = ""
        self._model_key = ""
        fsgs.signal.connect("config", self.on_config)
        self.on_config(Option.PLATFORM, fsgs.config.get(Option.PLATFORM))
        self.changed.connect(self.__changed)
        self.set_min_width(100)

    def on_destroy(self):
        fsgs.signal.disconnect("config", self.on_config)

    def __changed(self):
        fsgs.config.set(self._model_key, self._choice_values[self.get_index()])

    def on_config(self, key, value):
        if key == Option.PLATFORM:
            self._platform = value
            self._model_key = value + "_model"
            self.update_options()
            self.update_index(fsgs.config.get(self._model_key))
            self.update_enabled()
        elif key == self._model_key:
            self.update_index(value)

    def update_enabled(self):
        self.set_visible(self._platform not in AMIGA_PLATFORMS)
        self.set_enabled(self._choice_labels != ["N/A"])

    def update_index(self, value):
        try:
            index = self._choice_values.index(value)
        except ValueError:
            index = 0
        with self.changed.inhibit:
            self.set_index(index)

    def update_options(self):
        try:
            option = Option.get(self._model_key)
        except KeyError:
            self._choice_values = ["0"]
            self._choice_labels = ["N/A"]
        else:
            choices = option["values"]
            self._choice_values = [x[0] for x in choices]
            self._choice_labels = [x[1] for x in choices]
        with self.changed.inhibit:
            self.clear()
            for label in self._choice_labels:
                self.add_item(label)
