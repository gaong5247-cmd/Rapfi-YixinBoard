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
text = text.replace(win_old, 'gchar *argv[] = {"rapfi.exe", NULL};')
text = text.replace(unix_old, 'gchar *argv[] = {"./rapfi", NULL};')
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
