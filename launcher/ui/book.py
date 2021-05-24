from fsui import Panel, VerticalLayout
from fswidgets.widget import Widget


class Book(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = VerticalLayout()

        self.page_titles = []
        self.pages = []
        self.current_page = None

    def add_page(self, function, title=""):
        self.page_titles.append(title)
        self.pages.append(function)

    def set_page(self, page: Widget):
        print("Book.set_page", page)
        try:
            index = page + 0
        except TypeError:
            for i, p in enumerate(self.pages):
                if page == p:
                    index = i
                    break
            else:
                raise Exception("page not found")
        if self.current_page:
            self.current_page.hide()
            self.layout.remove(self.current_page)
        if callable(self.pages[index]):
            page = self.pages[index](self)
            self.pages[index] = page
        else:
            page = self.pages[index]
        self.layout.add(page, fill=True, expand=True)
        self.current_page = page
        page.show()
        if hasattr(page, "on_show"):
            page.on_show()

        print("Book, about to call self.layout.update, size =", self.size())
        # self.layout.set_size((1000, 100))
        # self.layout.update()

        # self.layout.set_size(self.size())
        self.layout.update()
        # self.layout.update()
        # self.layout.update()
        # if hasattr(page, "layout"):
        #     page.layout.set_size(self.size())
        #     page.layout.update()
