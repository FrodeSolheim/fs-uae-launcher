import fsui
from fscore.observable import Disposer, isObservable
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style

# from weakref import WeakMethod


# class MethodObserver:
#     def __init__(self, onNext):
#         self.onNext = WeakMethod(onNext)

#     def next(self, value):
#         onNext = self.onNext()
#         if onNext is not None:
#             onNext(value)


class Label(fsui.Label):
    def __init__(self, label="", *, parent=None, style=None):
        parent = parent or ParentStack.top()
        super().__init__(parent)
        if isObservable(label):
            self.addEventListener(
                "destroy", Disposer(label.subscribe(self.set_text))
            )
        else:
            self.set_text(label)

        # print("parent of button is", parent)

        # if hasattr(label, "subscribe"):
        #     # label.subscribe(MethodObserver(self.onLabelObservableChanged))
        #     label.subscribe(self.onLabelObservableChanged)
        # if hasattr(label, "current"):
        #     label_value = label.current
        # else:
        #     label_value = label

        # self.label = label
        # self.__super_called = False
        # if hasattr(label, "subscribe"):
        #     self.label_value =""
        #     print("\n\nSUBSCRIBING TO", label)
        #     disposable = label.subscribe(self.onLabelObservableChanged)
        #     # self.destroyed.connect(lambda: disposable.dispose())
        # else:
        #     self.label_value = label
        #     disposable = None

        # self.__super_called = True

        # if disposable is not None:
        #     def dispose():
        #         print("dispose")
        #         disposable.dispose()
        #     # self.destroyed.connect(lambda: disposable.dispose())
        #     self.destroyed.connect(dispose)

        # if isObservable(label):
        #     disposable = label.subscribe(self.set_text)
        #     self.addEventListener("destroy", lambda: disposable.dispose())

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        fontWeight = self.style.get("fontWeight")
        if fontWeight:
            font = self.get_font()
            font.set_weight(fontWeight)
            self.set_font(font)

        fill = True
        parent.layout.add(self, fill=fill)

    def setText(self, text):
        self.set_text(text)

    def addEventListener(self, eventName, listener):
        if eventName == "destroy":
            self.destroyed.connect(listener)

    # def __del__(self):
    #     pass

    # def onLabelObservableChanged(self, value):
    #     print("onLabelObservableChanged", value)
    #     if self.__super_called:
    #         self.set_text(value)
    #     else:
    #         self.label_value = value
