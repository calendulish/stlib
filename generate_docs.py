#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2023
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#
import shutil
from pathlib import Path

from pdoc import doc, render, extract

import stlib

stlib_modules = [
    'webapi',
    'community',
    'internals',
    'login',
    'universe',
    'client',
    'plugins',
    'steamworks',
    'utils',
]

if __name__ == "__main__":
    all_modules = {}

    render.configure(
        logo_link='https://lara.monster/stlib',
        footer_text='dev@lara.monster',
    )

    html_path = Path('html')
    shutil.rmtree(html_path)
    html_path.mkdir()

    stlib.__all__ = stlib_modules
    for module_name in extract.walk_specs(['stlib']):
        all_modules[module_name] = doc.Module.from_name(module_name)

    for module in all_modules.values():
        html = render.html_module(module, all_modules=all_modules)
        file = html_path / f"{module.fullname.replace('.', '/')}.html"
        file.parent.mkdir(exist_ok=True)
        file.write_bytes(html.encode())

    index = render.html_index(all_modules)
    index_path = html_path / "index.html"
    index_path.write_bytes(index.encode())

    search = render.search_index(all_modules)
    search_path = html_path / "search.js"
    search_path.write_bytes(search.encode())
