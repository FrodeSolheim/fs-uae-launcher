'''GLU extension EXT.nurbs_tessellator
'''
from OpenGL import extensions
from OpenGL.raw.GLU import constants

GLU_NURBS_BEGIN_EXT = _types.GLU_NURBS_BEGIN_EXT
GLU_NURBS_VERTEX_EXT = _types.GLU_NURBS_VERTEX_EXT
GLU_NURBS_COLOR_EXT = _types.GLU_NURBS_COLOR_EXT
GLU_NURBS_TEX_COORD_EXT = _types.GLU_NURBS_TEX_COORD_EXT
GLU_NURBS_END_EXT = _types.GLU_NURBS_END_EXT
GLU_NURBS_BEGIN_DATA_EXT = _types.GLU_NURBS_BEGIN_DATA_EXT
GLU_NURBS_VERTEX_DATA_EXT = _types.GLU_NURBS_VERTEX_DATA_EXT
GLU_NURBS_NORMAL_DATA_EXT = _types.GLU_NURBS_NORMAL_DATA_EXT
GLU_NURBS_COLOR_DATA_EXT = _types.GLU_NURBS_COLOR_DATA_EXT
GLU_NURBS_TEX_COORD_DATA_EXT = _types.GLU_NURBS_TEX_COORD_DATA_EXT
GLU_NURBS_END_DATA_EXT = _types.GLU_NURBS_END_DATA_EXT
GLU_NURBS_MODE_EXT = _types.GLU_NURBS_MODE_EXT
GLU_NURBS_TESSELLATOR_EXT = _types.GLU_NURBS_TESSELLATOR_EXT
GLU_NURBS_RENDERER_EXT = _types.GLU_NURBS_RENDERER_EXT

def gluInitNurbsTessellatorEXT():
    '''Return boolean indicating whether this module is available'''
    return extensions.hasGLUExtension( 'GLU_EXT_nurbs_tessellator' )