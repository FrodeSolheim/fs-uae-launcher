import fsgs
import fsui
from fsbc.application import app
from fsui.extra.iconheader import IconHeader
from launcher.i18n import gettext
from launcher.ui.skin import LauncherTheme
from launcher.ui.widgets import CloseButton


class AboutDialog(fsui.Window):
    def __init__(self, parent):
        if fsgs.product == "OpenRetro":
            app_name = "OpenRetro Launcher"
        else:
            app_name = "FS-UAE Launcher"
        title = "{} - {}".format(gettext("About"), app_name)
        super().__init__(parent, title, minimizable=False, maximizable=False)
        self.theme = LauncherTheme.get()
        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20)

        self.icon_header = IconHeader(
            self,
            fsui.Icon("fs-uae-launcher", "pkg:launcher"),
            "{name} {version}".format(name=app_name, version=app.version),
            "Copyright © 2012-2017 Frode Solheim",
        )
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        self.text_area = fsui.TextArea(
            self, about_message, read_only=True, font_family="monospace"
        )
        self.text_area.scroll_to_start()
        self.text_area.set_min_width(760)
        self.text_area.set_min_height(340)
        self.layout.add(self.text_area, fill=True, expand=True)

        CloseButton.add_to_layout(self, self.layout, margin_top=20)


about_message = """\n
This package is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This package is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this package; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

The following people have translated FS-UAE Launcher into several languages: 
Cédric "Foul" Monféfoul (French), nexusle (German), Speedvicio (Italian),
grimi (Polish), Milanchez (Serbian), albconde (Spanish), Treco (Portuguese),
GoingDown (Finish), spajdr (Czech), Decypher (Turkisk).

A big thanks to everyone who have tested the software and provided valuable
feedback! Especially the encouraging members of the English Amiga Board, and
all you who have commented on the official FS-UAE web site.

FS-UAE Launcher includes icons from GNOME icon theme from the GNOME Project
(http://www.gnome.org). The GNOME icon theme is distributed under the terms
of either GNU LGPL v.3 or Creative Commons BY-SA 3.0 license.

FS-UAE Launcher includes icons from humanity-icon-theme, licensed under the
terms of the GNU General Public license.

FS-UAE includes icons from oxygen-icon-theme, licensed under the terms of the
GNU Lesser General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

The Amiga Forever icon is (probably) copyright Cloanto Italia srl.

FS-UAE Launcher includes the oyoyo library, Copyright (c) 2008 Duncan Fordyce,
The license for this library is contained in the following paragraph:
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED
"AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

FS-UAE Launcher may include lhafile, Copyright (c) 2010 Hidekazu Ohnishi.
All rights reserved. Redistribution and use in source and binary forms,
with or without modification, are permitted provided that the following
conditions are met:
* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the author nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

FS-UAE Launcher depends on several open source third party software packages,
including but not limited to, Python and PyQt/Pyside.
"""
