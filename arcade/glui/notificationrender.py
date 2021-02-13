from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing, gl
from arcade.glui.render import Render
from arcade.notification import Notification

START_X = 20
START_Y = 1080 - 60 - 20


# noinspection PyAttributeOutsideInit
class NotificationRender(object):
    font = None
    y = START_Y

    @classmethod
    def init(cls):
        pass
        # import pygame.font
        # font_path = resources.resource_filename(
        #     "LiberationSans-Bold.ttf")
        # cls.font = pygame.font.Font(
        #     font_path, int(0.022 * Render.get().display_height))
        # #Notification("New device connected:\nLogitech Gamepad F310",
        # duration=60)
        # #Notification("Test 2", duration=10)
        # #Notification("Test 3")

    @classmethod
    def update(cls):
        pass
        # if Notification.new:
        #     Notification.new = False
        #     Render.get().dirty = True
        #     # post wake-up event
        #     pygame.event.post(pygame.event.Event(pygame.NUMEVENTS - 1))

    @classmethod
    def render(cls):
        notifications = Notification.all()
        if len(notifications) == 0:
            return
        Render.get().hd_perspective()
        cls.y = START_Y
        for i, notification in enumerate(notifications):
            cls.render_one(notification)
            Render.get().dirty = True
            # showing max four notifications
            if i > 4:
                break

    @classmethod
    def render_one(cls, notification):
        notification.show()
        w = 500
        h = 100
        x = START_X
        y = cls.y
        z = 0.9

        y -= h

        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_texturing(False)
        fs_emu_blending(True)
        gl.glBegin(gl.GL_QUADS)
        gl.glColor(1.0, 1.0, 0.5, 0.8)
        gl.glVertex3f(x, y, z)
        gl.glVertex3f(x + w, y, z)
        gl.glVertex3f(x + w, y + h, z)
        gl.glVertex3f(x, y + h, z)
        gl.glEnd()

        lines = notification.text.split("\n")
        y += h - 23
        for line in lines:
            tw, th = Render.get().measure_text(line, cls.font)
            y -= th
            Render.get().text(
                line, cls.font, x + 23, y, color=(0.2, 0.2, 0.0, 1.0)
            )
            y -= 2
        # cls.y += h + 15
        cls.y -= h + 20
        gl.glEnable(gl.GL_DEPTH_TEST)
