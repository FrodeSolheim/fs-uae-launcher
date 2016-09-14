from arcade.glui.opengl import gl, fs_emu_blending
from arcade.glui.render import Render
from .state import State


class Dialog(object):
    @classmethod
    def get_current(cls):
        return State.get().dialog

    def __init__(self):
        self.width = 1.6
        self.height = 1.0
        self.background_texture = None
        self.background_texture_offset = [0, 0]
        self.background_color = (0.4, 0.4, 0.4, 1.0)
        # make sure that the dialog is rendered at least once
        # after being created
        Render.get().dirty = True

    def show(self):
        State.get().dialog = self
        State.get().dialog_time = State.get().time

    def render(self):
        Render.get().ortho_perspective()
        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_blending(True)
        gl.glPushMatrix()
        gl.glTranslatef(-self.width / 2, -self.height / 2, 0.0)
        self.render_background()
        self.render_content()
        gl.glPopMatrix()
        gl.glEnable(gl.GL_DEPTH_TEST)
        pass

    def render_background(self):
        if self.background_texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.background_texture)
            gl.glColor3f(1.0, 1.0, 1.0)
        else:
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            # r, g, b a = self.background_color
            gl.glColor4f(*self.background_color)
        gl.glBegin(gl.GL_QUADS)
        bgx, bgy = self.background_texture_offset
        gl.glTexCoord(bgx + 0.0, bgy + 1.0)
        gl.glVertex2f(0, 0)
        gl.glTexCoord(bgx + 1.0, bgy + 1.0)
        gl.glVertex2f(self.width, 0)
        gl.glTexCoord(bgx + 1.0, bgy + 0.0)
        gl.glVertex2f(self.width, self.height)
        gl.glTexCoord(bgx + 0.0, bgy + 0.0)
        gl.glVertex2f(0, self.height)
        gl.glEnd()

    def render_content(self):
        pass

    def destroy(self):
        pass

    def close(self):
        if self == State.get().dialog:
            self.destroy()
            State.get().dialog = None
        else:
            print("WARNING: close called on non-active dialog")
