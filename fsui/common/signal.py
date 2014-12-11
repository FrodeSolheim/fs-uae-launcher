# from __future__ import division
# from __future__ import print_function
# from __future__ import absolute_import
# from __future__ import unicode_literals
#
# from weakref import ref
#
#
# class Signal(object):
#
#     def __init__(self):
#         self.listeners = []
#
#     def connect(self, listener):
#         print("connecting", listener)
#         self.listeners.append(ref(listener))
#
#     def notify(self, *args, **kwargs):
#         print("notify", self.listeners)
#         dead_refs = []
#         for listener_ref in self.listeners:
#             listener = listener_ref()
#             if listener is None:
#                 dead_refs.append(listener_ref)
#                 continue
#             print(listener, args, kwargs)
#             listener(*args, **kwargs)
#         for r in dead_refs:
#             self.listeners.remove(r)
