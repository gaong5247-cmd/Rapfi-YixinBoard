#!/usr/bin/env python3
"""Minimal upstream-preserving patch for Rapfi-YixinBoard."""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("upstream")
main = root / "main.c"
text = main.read_text(encoding="utf-8")
win_old = 'gchar *argv[] = {"engine.exe", "--force-utf8", NULL};'
unix_old = 'gchar *argv[] = {"./engine", NULL};'
assert text.count(win_old) == 1, "Upstream Windows engine launcher changed"
assert text.count(unix_old) == 1, "Upstream Unix engine launcher changed"
text = text.replace(win_old, 'gchar *argv[] = {"./rapfi.exe", NULL};')
text = text.replace(unix_old, 'gchar *argv[] = {"./rapfi", NULL};')
# Ensure relative engine, configuration and BMP paths resolve next to the GUI,
# even when the GUI is launched by a shortcut or another working directory.
win_include = '#include <time.h>'
assert text.count(win_include) == 1
text = text.replace(win_include, win_include + '''
#ifdef G_OS_WIN32
#include <windows.h>
#include <wchar.h>
#endif
''')
entry = '    srand((unsigned)time(NULL));'
assert text.count(entry) == 1
text = text.replace(entry, '''
#ifdef G_OS_WIN32
    {
        wchar_t executable_path[32768];
        DWORD n = GetModuleFileNameW(NULL, executable_path, 32768);
        if (n > 0 && n < 32768) {
            wchar_t *slash = wcsrchr(executable_path, L'\\\\');
            if (slash) {
                *slash = L'\\0';
                SetCurrentDirectoryW(executable_path);
            }
        }
    }
#endif
''' + entry)
# Avoid generic spawn error: state exactly where the engine should be installed.
spawn_anchor = '    ret = g_spawn_async_with_pipes(NULL,'
assert text.count(spawn_anchor) == 1
text = text.replace(spawn_anchor, '''
#ifdef G_OS_WIN32
    if (!g_file_test("rapfi.exe", G_FILE_TEST_IS_REGULAR))
        panic("rapfi.exe was not found beside Rapfi-YixinBoard.exe. Extract the ZIP first, then copy rapfi.exe into the same folder.");
#endif
''' + spawn_anchor)

# Fail with a useful diagnostic instead of dereferencing a missing sprite image.
sprite = '    pixbuf            = gdk_pixbuf_new_from_file(piecepicname, NULL);'
assert text.count(sprite) == 1, "Upstream bitmap loading changed"
text = text.replace(sprite, sprite + '''
    if (!pixbuf) {
        gchar *message = g_strdup_printf(
            "Cannot load %s from the GUI folder. Required sprite sheet: piece.bmp (or piece_dark.bmp in dark mode).",
            piecepicname);
        panic(message);
    }
''')

# A GTK style provider changes presentation only, preserving every original control.
anchor = '    gtk_init_with_args(&argc, &argv, NULL, options, NULL, &error);'
assert text.count(anchor) == 1, "Upstream GTK initialization changed"
css = '''
    /* Rapfi-YixinBoard: optional GTK3 visual refresh. */
    {
        GtkCssProvider *modern_css = gtk_css_provider_new();
        GFile *modern_file = g_file_new_for_path("modern.css");
        if (g_file_query_exists(modern_file, NULL)) {
            gtk_css_provider_load_from_file(modern_css, modern_file, NULL);
            gtk_style_context_add_provider_for_screen(
                gdk_screen_get_default(), GTK_STYLE_PROVIDER(modern_css),
                GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
        }
        g_object_unref(modern_file);
        g_object_unref(modern_css);
    }
'''
text = text.replace(anchor, anchor + "\n" + css)
main.write_text(text, encoding="utf-8")
print("Patched Rapfi engine discovery and optional modern CSS; retained all GUI commands.")
