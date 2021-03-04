import traceback

import fsui
from launcher.ui.config.model import create_model


class ConfigBrowser(fsui.VerticalItemView):
    def __init__(self, parent):
        # fsui.VerticalItemView.__init__(self, parent, border=(not Skin.fws()))
        fsui.VerticalItemView.__init__(self, parent, border=False)
        self.items = []
        self.game_icon = fsui.Image("launcher:/data/16x16/controller.png")
        self.config_icon = fsui.Image("launcher:/data/fsuae_config_16.png")

        self.manual_download_icon = fsui.Image(
            "launcher:/data/16x16/arrow_down_yellow.png"
        )
        self.auto_download_icon = fsui.Image(
            "launcher:/data/16x16/arrow_down_green.png"
        )
        self.blank_icon = fsui.Image("launcher:/data/16x16/blank.png")
        self.missing_color = fsui.Color(0xA8, 0xA8, 0xA8)
        self.platform_icons = {}

        from workspace.ui.theme import WorkspaceTheme

        theme = WorkspaceTheme.instance()
        self.set_row_height(28)
        # self.list_view.set_background_color(fsui.Color(0xeb, 0xeb, 0xeb))
        self.setStyleSheet(
            """
        QListView {{
            background-color: {0};
            outline: none;
        }}
        QListView::item {{
            padding-left: 6px;
            border: 0px;
        }}
        QListView::item:selected {{
            background-color: {1};
        }}
        """.format(
                theme.sidebar_background.to_hex(),
                theme.selection_background.to_hex(),
            )
        )

    def update_from_implicit(self, implicit):
        def flatten(item_list, level):

            for model_item in item_list:
                if model_item.active:
                    # text = "    " * level + str(model_item.text)
                    text = str(model_item.text)
                    if model_item.extra:
                        text += " [" + model_item.extra + "]"
                    items.append(text)
                if model_item.children:
                    flatten(model_item.children, level + 1)

        items = []
        try:
            model = create_model(implicit, show_all=False)
        except Exception:
            traceback.print_exc()
            print("create_model failed")
        else:
            flatten(model.items, 0)
        self.set_items(items)

    def on_select_item(self, index):
        if index is None:
            return
        pass

    def on_activate_item(self, index):
        pass

    def set_items(self, items):
        self.items = items
        self.update()

    def get_item_count(self):
        return len(self.items)

    def get_item_text(self, index):
        item = self.items[index]
        return item
        # return ""

    # def get_item_search_text(self, index):
    #     # return self.items[index][3]
    #     # FIXME: lower-case search string?
    #     return self.items[index][str("sort_key")]
    #
    # def get_item_text_color(self, index):
    #     have = self.items[index][str("have")]
    #     if not have:
    #         return self.missing_color

    def get_item_icon(self, index):
        # item = self.items[index]
        # platform_id = (item[str("platform")] or "").lower()
        # if item[str("have")] == 1:
        #     return self.manual_download_icon
        # elif item[str("have")] == 0:
        #     return self.blank_icon
        # elif item[str("have")] == 2:
        #     return self.auto_download_icon
        # elif item[str("have")] == 4:
        #     if platform_id not in self.platform_icons:
        #         try:
        #             icon = fsui.Image("launcher:/data/16x16/{0}.png".format(
        #                 platform_id))
        #         except Exception:
        #             icon = self.game_icon
        #         self.platform_icons[platform_id] = icon
        #     return self.platform_icons[platform_id]
        # else:
        return self.config_icon

    # def on_get_item_tooltip(self, row, column):
    #     return ""
