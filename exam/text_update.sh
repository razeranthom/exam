#!/bin/bash

xgettext -d base -o locales/base.pot exam_v2.py

msgmerge --update locales/en/LC_MESSAGES/base.po locales/base.pot
msgmerge --update locales/pt_BR/LC_MESSAGES/base.po locales/base.pot
msgmerge --update locales/es/LC_MESSAGES/base.po locales/base.pot

# msgfmt -o locales/pt_BR/LC_MESSAGES/base.mo locales/pt_BR/LC_MESSAGES/base
# msgfmt -o locales/es/LC_MESSAGES/base.mo locales/es/LC_MESSAGES/base