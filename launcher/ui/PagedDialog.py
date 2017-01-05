import fsui
from fsui.qt import Signal
from .skin import Skin


class PagedDialog(fsui.Window):

    page_changed = Signal()

    def __init__(self, parent, title):
        super().__init__(parent, title, minimizable=False, maximizable=False)
        # buttons, layout = fsui.DialogButtons.create_with_layout(self)
        # buttons.create_close_button()
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20)
        layout = self.layout

        hor_layout = fsui.HorizontalLayout()
        layout.add(hor_layout, fill=True, expand=True)

        layout_2 = fsui.VerticalLayout()
        # layout_2.padding_top = 20
        # layout_2.padding_bottom = 20
        # layout_2.padding_left = 20

        self.list_view = fsui.ListView(self, border=False)
        self.list_view.set_min_width(240)
        self.list_view.item_selected.connect(self.on_select_item)
        if Skin.fws():
            from workspace.ui.theme import Theme
            theme = Theme.instance()
            self.list_view.set_row_height(28)
            # self.list_view.set_background_color(fsui.Color(0xeb, 0xeb, 0xeb))
            self.list_view.setStyleSheet("""
            QListView {{
                padding-top: 20px;
                background-color: {0};
                outline: none;
            }}
            QListView::item {{
                padding-left: 20px;
                border: 0px;
            }}
            QListView::item:selected {{
                background-color: {1};
            }}
            """.format(theme.sidebar_background.to_hex(),
                       theme.selection_background.to_hex()))
            layout_2.add(self.list_view, fill=True, expand=True)
        else:
            self.list_view.set_row_height(28)
            from fsui.qt import QPalette
            palette = self._real_widget.palette()
            base = fsui.Color(palette.color(QPalette.Base))
            bg = fsui.Color(palette.color(QPalette.Highlight))
            fg = fsui.Color(palette.color(QPalette.HighlightedText))
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
                background-color: {highlight_bg};
                color: {highlight_fg};
            }}
            """.format(highlight_fg=fg.to_hex(), highlight_bg=bg.to_hex(),
                       base=base.to_hex()))
            layout_2.add(self.list_view, fill=True, expand=True)
        hor_layout.add(layout_2, fill=True)

        # hor_layout.add_spacer(20)

        use_scrolling = False
        if use_scrolling:
            # FIXME: Problems with page height
            scroll_area = fsui.VerticalScrollArea(self)
            self.page_container = fsui.Panel(scroll_area)
            self.page_container.layout = fsui.VerticalLayout()
            hor_layout.add(scroll_area, fill=True, expand=True)
            scroll_area.set_widget(self.page_container)
        else:
            self.page_container = fsui.Panel(self)
            self.page_container.layout = fsui.VerticalLayout()
            hor_layout.add(self.page_container, fill=True, expand=True)

        # self.layout.add_spacer(20)

        hor_layout = fsui.HorizontalLayout()
        layout.add(hor_layout, fill=True)

        self.page_titles = []
        self.pages = []

        # self.add_page(_("Hardware"), HardwarePage)
        # self.add_page(_("Hard Drives"), HardDrivesPage)
        # elf.add_page(_("Custom Options"), CustomOptionsPage)

        self.current_page = None
        self.set_size((840, 640))
        self.center_on_parent()

    # def on_close_button(self):
    #     self.end_modal(0)

    def on_select_item(self, index):
        self.set_page(index)

    def get_index(self):
        return self.list_view.get_index()

    def get_page_title(self, index):
        return self.page_titles[index][0]

    def get_page_index_by_title(self, title):
        for index, t in enumerate(self.page_titles):
            if t[0] == title:
                return index
        return None

    def add_page(self, title, function, icon=None):
        self.page_titles.append((title, icon))
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
