from game_center.glui.opengl import *


MAX_LINE = 30


def main(main_window):
    from game_center.glui.settings import Settings

    # for arg in sys.argv:
    #     print("arg -->", arg)
    #     Settings.fullscreen_game = True
    #     if arg == "--fullscreen":
    #         Settings.fullscreen_menu = True
    #     if arg == "--window":
    #         if not "--no-decorations" in sys.argv:
    #             Settings.window_decorations = True
    #         Settings.fullscreen_menu = False
    #         Settings.fullscreen_game = False
    #         # Settings.windowed_size = (1024, 576)
    #     elif arg.startswith("--window="):
    #         Settings.fullscreen_menu = False
    #         Settings.fullscreen_game = False
    #         w, h = arg[9:].split("x")
    #         w = int(w)
    #         h = int(h)
    #         Settings.windowed_size = (w, h)
    #     elif arg == "--maximize":
    #         if not "--no-decorations" in sys.argv:
    #             Settings.window_decorations = True
    #         Settings.fullscreen_menu = False
    #         Settings.fullscreen_game = True
    #         Settings.windowed_size = None
    #     elif arg == "--no-decorations":
    #         Settings.window_decorations = False
    #     elif arg == "--decorations":
    #         Settings.window_decorations = True

    try:
        import game_center.glui.window
        game_center.glui.window.main_window = main_window
        game_center.glui.window.show()
    except Exception as e:
        import traceback
        print("\n" + "-" * 79 + "\n" + "EXCEPTION")
        traceback.print_exc()
        show_error(repr(e), traceback.format_exc(e))

    print(" --- game_center.glui.main is done ---")


# import pygame
# from game_center.glui.render import Render
#
#
# def show_error(message, backtrace):
#     width = 16 / 9 * 2
#     height = 2.0
#     message = message
#     backtrace = backtrace
#     splitted = backtrace.split("\n")
#     if not splitted[-1]:
#         splitted = splitted[:-1]
#
#     #background_color = (0.0, 0.0, 0.0, 1.0)
#     liberation_mono_bold = resources.resource_filename(
#         "LiberationMono-Regular.ttf")
#     print(liberation_mono_bold)
#     detail_font = pygame.font.Font(
#         liberation_mono_bold, int(0.021 * Render.display_height))
#     guru_font = pygame.font.Font(
#         liberation_mono_bold, int(0.03 * Render.display_height))
#     start_time = time.time()
#     while True:
#         events = pygame.event.get()
#         stop = False
#         for event in events:
#             if event.type == pygame.QUIT:
#                 stop = True
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_RETURN:
#                     stop = True
#                 if event.key == pygame.K_ESCAPE:
#                     stop = True
#         if stop:
#             pygame.display.quit()
#             sys.exit(1)
#
#         glClearColor(0.0, 0.0, 0.0, 0.0)
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         Render.ortho_perspective()
#         glPushMatrix()
#         glTranslatef(-width / 2, -height / 2, 0.0)
#         x1 = 0
#         x2 = width
#         y1 = 1.7
#         y2 = 2.0
#         w = 0.03
#
#         glDisable(GL_DEPTH_TEST)
#         fs_emu_texturing(False)
#         fs_emu_blending(True)
#         alert_color = (1.0, 0.0, 0.0)
#         t = int((time.time() - start_time) * 1.6)
#         if t % 2 == 0:
#             glBegin(GL_QUADS)
#             glColor3f(*alert_color)
#             glVertex2f(x1, y1)
#             glVertex2f(x2, y1)
#             glVertex2f(x2, y2)
#             glVertex2f(x1, y2)
#             glColor3f(0.0, 0.0, 0.0)
#             glVertex2f(x1 + w, y1 + w)
#             glVertex2f(x2 - w, y1 + w)
#             glVertex2f(x2 - w, y2 - w)
#             glVertex2f(x1 + w, y2 - w)
#             glEnd()
#         fs_emu_texturing(True)
#         glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
#
#         text = "Software Failure.  Press ENTER or ESCAPE key to quit."
#         Render.text(text, guru_font, 0.2, 1.85, color=alert_color)
#         text = splitted[-1]
#         text = "Guru Meditation #{0}".format(text)
#         Render.text(text, guru_font, 0.2, 1.77, color=alert_color)
#
#         x = 0.2
#         y = 0.15
#
#         tw, th = Render.measure_text("M", detail_font)
#         y += th
#         lines = []
#         max_line_size = 129
#         for line in splitted:
#             line = line.rstrip()
#             while len(line) > max_line_size:
#                 lines.append(line[:max_line_size])
#                 line = line[max_line_size:]
#             lines.append(line)
#
#         for i, line in enumerate(reversed(lines)):
#             if i == MAX_LINE:
#                 break
#             s = (MAX_LINE - i) / MAX_LINE
#             tw, th = Render.text(
#                 line, detail_font, x, y, color=(s, s, s, 1.0))
#             y += th
#         glPopMatrix()
#         pygame.display.flip()
