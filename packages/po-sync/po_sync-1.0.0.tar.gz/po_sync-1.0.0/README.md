# PoSync

**PoSync** is an open-source command-line tool designed to automatically synchronize `.po` file keys (`msgid`) with
applied corrections and update your source code accordingly.  
It is ideal for projects using React, Vue, Angular, or any framework that leverages `.po` files for
internationalization (i18n).

## 🚀 Why PoSync?

When using `.po` files for translations, the original language is often repeated in the `msgid`.  
If you fix a typo or update text, you normally need to **manually update all references** in your codebase — a tedious
and error-prone process.

**PoSync** automates this workflow by:

- Detecting modified `msgid`s based on the corrected `msgstr`
- Updating the source code automatically at the exact lines indicated in the `.po` file
- Updating the `msgid` in the `.po` file itself to keep everything in sync
- Working seamlessly on Mac and Linux

## ✨ Features

- 🔍 **Smart `.po` analysis** using occurrence information (`#: file:line`)
- 🔄 **Automatic source code replacement** at the precise lines
- 🗂 **Direct update** of `msgid` in the `.po` file
- 🛠 **No approximate regex** — only replaces where necessary
- 📦 Easy installation via **pip** or **Homebrew** (Mac/Linux)

## 📥 Installation

Install via pip:

```bash
pip install po_sync
```

## 💡Basic Usage

```bash
po_sync path/to/messages.po
````

* `path/to/messages.po` — Path to the `.po` file containing corrections.

### Optional Arguments

| Flag                                             | Description                                                               | Default                   |
|--------------------------------------------------|:--------------------------------------------------------------------------|---------------------------|
| `-h, --help`                                     | Show the help message                                                     |                           |
| `-d [FOLDER_PATH], --base-project [FOLDER_PATH]` | Path to the base project folder                                           | current working directory |
| `-c, --clear`                                    | Clear msgstr after processing                                             |                           |
| `-t, --dry-run`                                  | Perform a dry run without modifying any files; useful to preview changes  |                           |
| `-v, --verbose`                                  | Enable verbose output for detailed information about what will be updated |                           |
| `-y, --yes`                                      | Skip confirmation prompts and apply changes automatically                 |                           |

### Examples

* **Default run** (apply corrections from `.po` file to source code):

```bash
po_sync messages.po
```

* **Dry run** (preview changes without modifying files):

```bash
po_sync messages.po --dry-run
```

* **Specify project folder**:

```bash
po_sync messages.po --base-project dist/ message.po
```

* **Verbose output with automatic confirmation**:

```bash
po_sync messages.po --verbose --yes
```
