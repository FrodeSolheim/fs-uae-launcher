from launcher.ui.behaviors.amigaenablebehavior import AmigaEnableBehavior
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.config.ConfigCheckBox import ConfigCheckBox
from fsbc.util import unused
import fsui
from ...launcher_config import LauncherConfig
from fsgs.amiga.Amiga import Amiga
from ...floppy_manager import FloppyManager
from ...cd_manager import CDManager
from ...i18n import gettext
# from .ConfigCheckBox import ConfigCheckBox


class ModelGroup(fsui.Group):

    # FIXME: remove with_more_button=True
    def __init__(self, parent, with_more_button=True):
        unused(with_more_button)
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.model_ids = [
            x["id"] for x in Amiga.models if "/" not in x["id"]]
        self.model_titles = [
            x["title"] for x in Amiga.models if "/" not in x["id"]]

        self.sub_model_ids = []
        self.sub_model_titles = []
        self.sub_model_updating = False

        self.model_choice = fsui.Choice(self, self.model_titles)
        AmigaEnableBehavior(self.model_choice)
        self.sub_model_choice = fsui.Choice(self, self.sub_model_titles)
        AmigaEnableBehavior(self.sub_model_choice)
        self.accuracy_label = fsui.Label(self, gettext("Accuracy:"))
        self.accuracy_choice = fsui.Choice(self, [
            gettext("High"),
            gettext("Medium"),
            gettext("Low")])
        AmigaEnableBehavior(self.accuracy_choice)
        self.ntsc_checkbox = ConfigCheckBox(self, "NTSC", "ntsc_mode")
        AmigaEnableBehavior(self.ntsc_checkbox)

        # if fs_uae_launcher.ui.get_screen_size()[1] > 768:
        # self.layout.add(heading_label, margin=10)
        # self.layout.add_spacer(0)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        heading_label = fsui.HeadingLabel(self, gettext("Amiga Model"))
        hori_layout.add(heading_label, margin=10)
        hori_layout.add_spacer(10)
        hori_layout.add(self.ntsc_checkbox, expand=False,
                        margin_left=10, margin_right=10)
        hori_layout.add_spacer(0, expand=True)

        hori_layout.add(self.accuracy_label, margin_right=10)
        hori_layout.add(self.accuracy_choice, margin_right=10)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        hori_layout.add(self.model_choice, expand=False, margin=10)
        hori_layout.add(self.sub_model_choice, expand=True, margin=10)

        ConfigBehavior(self, ["accuracy", "amiga_model"])

        self.model_choice.on_changed = self.on_model_changed
        self.sub_model_choice.on_changed = self.on_sub_model_changed
        self.accuracy_choice.on_changed = self.on_accuracy_changed

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
        self.sub_model_choice.enable(len(self.sub_model_ids) > 1)
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
                sub_model_index = self.update_sub_models(model_id, sub_model_id)
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
