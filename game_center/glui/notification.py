from game_center.notification import Notification
from game_center.glui.opengl import *
from game_center.glui.render import Render


# noinspection PyAttributeOutsideInit
class NotificationRender(object):

    font = None
    y = 0

    @classmethod
    def init(cls):
        pass
        # import pygame.font
        # font_path = resources.resource_filename(
        #     "LiberationSans-Bold.ttf")
        # cls.font = pygame.font.Font(
        #     font_path, int(0.022 * Render.display_height))
        # #Notification("New device connected:\nLogitech Gamepad F310", duration=60)
        # #Notification("Test 2", duration=10)
        # #Notification("Test 3")

    @classmethod
    def update(cls):
        pass
        # if Notification.new:
        #     Notification.new = False
        #     Render.dirty = True
        #     # post wake-up event
        #     pygame.event.post(pygame.event.Event(pygame.NUMEVENTS - 1))

    @classmethod
    def render(cls):
        notifications = Notification.all()
        if len(notifications) == 0:
            return
        Render.hd_perspective() 
        cls.y = 0
        for i, notification in enumerate(notifications):
            cls.render_one(notification)
            Render.dirty = True
            # showing max two notifications
            if i == 1:
                break

    @classmethod
    def render_one(cls, notification):
        notification.show()
        w = 500
        h = 100
        x = 1920 - w
        y = cls.y
        z = 0.9
        fs_emu_texturing(False)
        fs_emu_blending(True)
        glBegin(GL_QUADS)
        glColor(1.0, 1.0, 0.5, 0.8)
        glVertex3f(x, y, z)
        glVertex3f(x + w, y, z)
        glVertex3f(x + w, y + h, z)
        glVertex3f(x, y + h, z)
        glEnd()

        lines = notification.text.split("\n")
        y += h - 23
        for line in lines:
            tw, th = Render.measure_text(line, cls.font)
            y -= th
            Render.text(line, cls.font, x + 23, y, color=(0.2, 0.2, 0.0, 1.0))
            y -= 2
        cls.y += h + 15
