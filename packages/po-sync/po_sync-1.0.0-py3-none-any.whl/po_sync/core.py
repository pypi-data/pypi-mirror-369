import logging
import os
from logging import Logger
from pathlib import Path

import polib
from polib import POEntry
from tabulate import tabulate


class PoSync:
    file_path: str = None
    folder_path: str = None

    yes: bool = False
    clear: bool = False
    verbose: bool = False
    dry_run: bool = False
    logger: Logger = None

    occurrences_process_count = 0
    occurrences_skip_count = 0
    occurrences_not_found_count = 0
    occurrences_total_count = 0

    skip_count = 0
    clear_count = 0
    process_count = 0
    total_count = 0

    files: dict[str, dict] = {}

    def __init__(self, file_path: str, folder_path: str = None, dry_run: bool = False, verbose: bool = False,
                 yes: bool = False, clear: bool = False) -> None:
        self.yes = yes
        self.clear = clear

        self.verbose = verbose
        self.dry_run = dry_run
        self.file_path = file_path
        self.folder_path = folder_path

        self.init_logger()
        self.logger.setLevel(logging.DEBUG)

    def init_logger(self):
        class CustomFormatter(logging.Formatter):
            grey = "\x1b[38;20m"
            blue = "\x1b[36m"
            yellow = "\x1b[33;20m"
            red = "\x1b[31;20m"
            bold_red = "\x1b[31;1m"
            reset = "\x1b[0m"
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

            FORMATS = {
                logging.DEBUG: grey + format + reset,
                logging.INFO: blue + format + reset,
                logging.WARNING: yellow + format + reset,
                logging.ERROR: red + format + reset,
                logging.CRITICAL: bold_red + format + reset
            }

            def format(self, record):
                log_fmt = self.FORMATS.get(record.levelno)
                custom_formatter = logging.Formatter(log_fmt)
                return custom_formatter.format(record)

        self.logger = logging.getLogger('po-sync')
        self.logger.setLevel("DEBUG" if self.verbose else "INFO")

        console_handler = logging.StreamHandler()
        console_handler.setLevel("DEBUG" if self.verbose else "INFO")
        console_handler.setFormatter(CustomFormatter())

        self.logger.addHandler(console_handler)

    def clear_entry(self, entry: POEntry) -> None:
        self.clear_count += 1
        entry.msgstr = ""

    def process_entry_occurrences(self, entry: POEntry) -> None:
        self.process_count += 1
        for filename, line_no in entry.occurrences:
            idx = int(line_no) - 1
            self.occurrences_total_count += 1

            full_path = os.path.join(self.folder_path, filename)
            if full_path not in self.files:
                file_path = Path(full_path)
                if not file_path.exists():
                    self.logger.warning(f"File {full_path} does not exist")
                    self.occurrences_not_found_count += 1
                    continue

                file_content = file_path.read_text(encoding="utf-8")
                self.files[full_path] = {
                    'lines': file_content.splitlines(),
                    'endWithBreak': file_content.endswith("\n"),
                }

            if idx > len(self.files[full_path]['lines']):
                self.logger.warning(f"File {filename}:{idx} does not contain {entry.msgid}")
                self.occurrences_not_found_count += 1
                continue

            if entry.msgid not in self.files[full_path]['lines'][idx]:
                idx = idx + 1
                if entry.msgid in self.files[full_path]['lines'][idx]:
                    self.logger.warning(f"File {filename}:{idx} does not contain {entry.msgid}")
                    self.occurrences_not_found_count += 1
                    continue

            self.occurrences_process_count += 1
            if self.dry_run:
                self.logger.info(f"[DRY-RUN] {filename}:{line_no} — {entry.msgid} -> {entry.msgstr}")
            else:
                self.logger.debug(f"{filename}:{line_no} — {entry.msgid} -> {entry.msgstr}")

            self.files[full_path]['lines'][idx] = self.files[full_path]['lines'][idx].replace(entry.msgid, entry.msgstr)

    def apply_replacement(self) -> None:
        for full_path, file_data in self.files.items():
            self.logger.debug(f"Apply replacement for {full_path}")

            file_path = Path(full_path)

            file_path.write_text(
                "\n".join(file_data['lines']) + ("\n" if file_data['endWithBreak'] else ''),
                encoding="utf-8")

    def process_entry(self, entry: POEntry) -> None:
        self.logger.debug(f"Check entry [{entry.msgid}]")

        if not entry.msgstr:
            self.skip_count += 1
            self.logger.debug(f"Skip entry [{entry.msgid}] : empty")
            return

        if entry.msgid == entry.msgstr:
            self.skip_count += 1
            self.logger.debug(f"Skip entry [{entry.msgid}] : not changed")

            if self.clear:
                self.clear_entry(entry)
            return

        self.process_entry_occurrences(entry)

        entry.msgid = entry.msgstr
        if self.clear:
            self.clear_entry(entry)

    def run(self):
        self.logger.info("Starting sync [%(mode)s]" % {
            'mode': 'dry-ryn' if self.dry_run else ('directly' if self.yes else 'with-confirmation')
        })
        po = polib.pofile(self.file_path)

        for entry in po:
            self.process_entry(entry)
            self.total_count += 1

        table = [
            [
                self.file_path.split('/')[-1],
                self.total_count,
                self.skip_count,
                "nan",
                self.process_count,
                self.clear_count,
            ],
            [
                '%s (Occurrences)' % (self.file_path.split('/')[-1],),
                self.occurrences_total_count,
                self.occurrences_skip_count,
                self.occurrences_not_found_count,
                self.occurrences_process_count,
                "Nan"
            ]
        ]
        print('')
        print(tabulate(table, headers=["", "Entries", "Skipped", "Not found", "Processed", "Cleared"],
                       tablefmt="simple_grid"))
        print('')

        if self.dry_run:
            return

        if not self.yes:
            value = input("Are you sure to apply remplacement ? [y/N]")
            if value.lower() not in ('y', 'yes'):
                self.logger.info("Aborted")
                return

        self.logger.info("Applying remplacement ...")

        self.apply_replacement()
        po.save(self.file_path)
