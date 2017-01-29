import fsui
from launcher.ui.widgets import CloseButton
from .skin import LauncherTheme


class PagedDialog(fsui.Window):
    page_changed = fsui.Signal()

    def __init__(self, parent, title):
        super().__init__(parent, title, minimizable=False, maximizable=False)
        self.theme = LauncherTheme.get()
        self.layout = fsui.VerticalLayout()

        # self.layout.set_padding(20)
        layout = self.layout

        h_layout = fsui.HorizontalLayout()
        layout.add(h_layout, fill=True, expand=True)

        layout_2 = fsui.VerticalLayout()
        # layout_2.padding_top = 20
        # layout_2.padding_bottom = 20
        # layout_2.padding_left = 20

        self.list_view = fsui.ListView(self, border=False)
        self.list_view.set_min_width(240)
        self.list_view.item_selected.connect(self.on_select_item)

        self.list_view.set_row_height(
            self.window.theme.sidebar_list_row_height)
        self.list_view.setStyleSheet("""
        QListView {{
            padding-top: 20px;
            background-color: {base};
            outline: none;
        }}
        QListView::item {{
            padding-left: 20px;
            border: 0px;
        }}
        QListView::item:selected {{
            background-color: {row_bg};
            color: {row_fg};
        }}
        """.format(
            row_fg=self.window.theme.sidebar_list_row_text.to_hex(),
            row_bg=self.window.theme.sidebar_list_row_background.to_hex(),
            base=self.window.theme.sidebar_list_background.to_hex()))
        layout_2.add(self.list_view, fill=True, expand=True)
        h_layout.add(layout_2, fill=True)

        # h_layout.add_spacer(20)

        v_layout = fsui.VerticalLayout()
        h_layout.add(v_layout, fill=True, expand=True)

        use_scrolling = False
        if use_scrolling:
            # FIXME: Problems with page height
            scroll_area = fsui.VerticalScrollArea(self)
            self.page_container = fsui.Panel(scroll_area)
            self.page_container.layout = fsui.VerticalLayout()
            scroll_area.set_widget(self.page_container)
            v_layout.add(scroll_area, fill=True, expand=True)
        else:
            self.page_container = fsui.Panel(self)
            self.page_container.layout = fsui.VerticalLayout()
            v_layout.add(self.page_container, fill=True, expand=True)

        # self.layout.add_spacer(20)

        # h_layout = fsui.HorizontalLayout()
        # layout.add(h_layout, fill=True)

        self.page_titles = []
        self.pages = []

        # self.add_page(_("Hardware"), HardwarePage)
        # self.add_page(_("Hard Drives"), HardDrivesPage)
        # elf.add_page(_("Custom Options"), CustomOptionsPage)

        self.button_layout = fsui.HorizontalLayout()
        v_layout.add(self.button_layout, fill=True, margin=20, margin_top=0)
        if self.window.theme.has_close_buttons:
            self.button_layout.add_spacer(expand=True)
            self.close_button = CloseButton(self)
            self.button_layout.add(
                self.close_button, fill=True, margin_left=10)

        self.current_page = None

        # self.page_container.set_min_width(600)
        # self.page_container.set_min_height(640)
        # self.set_size_from_layout()
        self.set_size((840, 640))
        self.center_on_parent()

    # def on_close_button(self):
    #     self.end_modal(0)

    def on_select_item(self, index):
        self.set_page(index)

    @property
    def index(self):
        return self.list_view.get_index()

    @property
    def page(self):
        return self.current_page

    def get_index(self):
        return self.list_view.get_index()

    def get_page_title(self, index):
        # return self.page_titles[index][0]
        return self.page_titles[index]["label"]

    def get_page_index_by_title(self, title):
        # for index, t in enumerate(self.page_titles):
        #     if t[0] == title:
        for i, item in enumerate(self.page_titles):
            if item["label"] == title:
                return i
        return None

    def add_page(self, title, function, icon=None, bold=False):
        self.page_titles.append({"label": title, "icon": icon, "bold": bold})
        self.pages.append(function)
        self.list_view.set_items(self.page_titles)

    def set_page(self, index):
        if self.current_page:
            self.current_page.hide()
            self.page_container.layout.remove(self.current_page)
        if callable(self.pages[index]):
            page = self.pages[index](self.page_container)
            self.pages[index] = page
        else:
            page = self.pages[index]
        self.page_container.layout.add(page, fill=True, expand=True)
        self.current_page = page
        page.show()
        # print("calling self.layout.update")
        self.page_container.layout.update()
        self.layout.update()

        self.page_changed.emit()

    def set_page_by_title(self, title):
        index = self.get_page_index_by_title(title)
        if index is not None:
            # self.set_page(index)
            self.list_view.set_index(index)
        return index
