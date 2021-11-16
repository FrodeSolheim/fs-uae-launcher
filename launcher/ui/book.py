from typing import Callable, List, Optional, Union

from fsui import Panel, VerticalLayout
from fswidgets.widget import Widget


class Book(Panel):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        self.layout = VerticalLayout()

        self.page_titles: List[str] = []
        self.pages: List[Union[Widget, Callable[[], Widget]]] = []
        self.current_page: Optional[Widget] = None

    def add_page(
        self, function: Union[Widget, Callable[[], Widget]], title: str = ""
    ):
        self.page_titles.append(title)
        self.pages.append(function)

    def set_page(self, page: Union[int, Widget]):
        print("Book.set_page", page)
        index: int
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
