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

# Display the GUI before opening Rapfi and sending setup/database commands.
# Defer on the GTK main thread (never touch Gtk widgets from a worker).
old_main = '''    load_engine();
    init_engine();
    gtk_window_set_default_icon(
        gdk_pixbuf_new_from_file("icon.ico", NULL)); /* set the default icon for all windows */
    create_windowclock();
    create_windowmain();
    show_welcome();
    show_database();
    gtk_main();'''
new_main = '''    startup_mark("gtk-ready");
    gtk_window_set_default_icon(
        gdk_pixbuf_new_from_file("icon.ico", NULL)); /* set the default icon for all windows */
    create_windowclock();
    create_windowmain();
    startup_mark("gui-created");
    show_welcome();
    /* Allow GTK to paint the first frame before spawning/loading the engine. */
    g_timeout_add(250, startup_engine_callback, NULL);
    gtk_main();'''
assert text.count(old_main) == 1, "Upstream startup sequence changed"
text = text.replace(old_main, new_main)
# A timestamped log permits distinguishing GTK creation vs engine startup.
marker = 'int main(int argc, char **argv)'
assert text.count(marker) == 1
helpers = '''
static gint64 rapfi_start_monotonic = 0;
static void startup_mark(const char *stage)
{
    gint64 now = g_get_monotonic_time();
    if (!rapfi_start_monotonic) rapfi_start_monotonic = now;
    FILE *log = fopen("startup-timing.log", "a");
    if (log) {
        fprintf(log, "%s: %.3f seconds\\n", stage,
                (now - rapfi_start_monotonic) / 1000000.0);
        fclose(log);
    }
}
static gboolean startup_engine_callback(gpointer data)
{
    (void)data;
    startup_mark("engine-start");
    load_engine();
    startup_mark("engine-spawned");
    init_engine();
    startup_mark("engine-initialized");
    show_database();
    startup_mark("database-requested");
    return G_SOURCE_REMOVE;
}

'''
text = text.replace(marker, helpers + marker)

main.write_text(text, encoding="utf-8")
print("Patched Rapfi startup, timing diagnostics, engine discovery and BMP loading.")
