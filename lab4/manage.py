#!/usr/bin/env python
"""Django жобасын басқару құралы."""
import os
import sys


def main():
    # Windows консолінде қазақ әріптері дұрыс шығуы үшін UTF-8 қолданамыз.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm_lab.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
