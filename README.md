# Dependencies

1. Python
2. Latex
3. gettext


# Install


# Creating questions


# Executing

1. To create a new exam configuration file (examname.yaml)

```
$ python3 ./exam_v2.py init examname
```

2. Edit your exam to your needs
3. To generate exam files

```
$ python3 ./exam_v2.py generate examname
```

# Translations

Based on python gettext.

If you want to update translation or add a new locale, see next subsessions.

## How we made locales support

All strings in script that can be translated are marked with function _()

xgettext generated an base.pot file with the sintax:

```
\#: arq.py:116
msgid "Unknown system error"
msgstr ""
```

Where msgid is the original message and msgstr is the translated message.

After that, in locales folder, all supported locales have a folder structure, like:

```
locales/pt_BR/LC_MESSAGES
```

Inside LC_MESSAGES the base.pot file is copied as base.po and all messages needs to be translated (msgstr).

Then, running:

```
msgfmt -o locales/XX/LC_MESSAGES/base.mo locales/XX/LC_MESSAGES/base
```

Compile base.po in base.mo and now the script is translated.


## Adding new locales

1. Create folder locales/XX/LC_MESSAGES, where XX is your locale
2. Copy locales/base.pot to locales/XX/LC_MESSAGES/base.po
3. Open locales/XX/LC_MESSAGES/base.po and translate texts to your language
4. Run: msgfmt -o locales/XX/LC_MESSAGES/base.mo locales/XX/LC_MESSAGES/base to compile base.po to base.mo
5. Update config.yaml, session config subsession locale, to use XX as your locale
6. Now the EXAM is updated

## Updating locale texts

1. Update texts inside .py file
2. Run text_update.sh script to generate new locales/base.pot and merge new base.pot to old base.po on each language
3. For each language file base.po:
	1. Translate new texts
	2. Update old translations marked as ", fuzzy"
	3. Remove ", fuzzy" flag
4. Run text_complile.sh script to compile new translations to base.mo 
5. Now the EXAM is updated