from typing import Literal, TypeAlias
import os
import pwd
import grp

from rich.text import Text
from textual import work
from textual.widget import Widget
from textual.containers import Vertical
from textual.widgets import DataTable, Label

from mudus.database import MudusDatabase, DirectorySizes
from .mudus_loading_indicator import MudusLoadingIndicator

IdOrAll: TypeAlias = int | Literal["all"]


class MudusTable(Widget):
    def __init__(self, mudus_db: MudusDatabase, user_id: int):
        super().__init__()

        self.mudus_db: MudusDatabase = mudus_db
        self.parent_dir: str | None = None
        self.highlighted_row: str | None = None
        self.set_user_and_group(user_id=user_id, group_id="all")

    def set_user_and_group(self, user_id: int, group_id: IdOrAll):
        """
        Set the user ID and group ID for which to show the disk usage.
        """
        self.user_id: int = user_id
        self.group_id: IdOrAll = group_id

        if self.user_id != "all":
            try:
                self.user_name = pwd.getpwuid(self.user_id).pw_name
            except KeyError:
                self.user_name = "**UNKNOWN USER**"
        else:
            self.user_name = "**ALL USERS**"

        if self.group_id != "all":
            try:
                self.group_name = grp.getgrgid(self.group_id).gr_name
            except KeyError:
                self.group_name = "**UNKNOWN GROUP**"
        else:
            self.group_name = "**ALL GROUPS**"

        self.show_what_message: str = (
            f"disk usage for user [bold]{self.user_name}[/] and group [bold]{self.group_name}[/]"
        )

    def compose(self):
        yield Vertical(
            Label("", id="mudus_table_title"),
            Label("", id="mudus_db_message"),
            MudusLoadingIndicator(f"Loading {self.show_what_message}"),
            DataTable(cursor_type="row", id="mudus_table"),
            Label("", id="mudus_debug"),
        )
        self.call_later(self.load_directory_sizes)

    def set_db_message(self, error: str = ""):
        """
        Update the label that contains the database status message
        (by default it shows when the database was last updated)
        """
        msg = f"[dim italic]{self.mudus_db.message}[/]"
        if error:
            msg += f"\n[red][bold]Error:[/bold] {error}[/red]"
        self.query_one("#mudus_db_message").update(Text.from_markup(msg))

    @work(thread=True, exclusive=True, group="load_directory_sizes")
    def load_directory_sizes(self) -> DirectorySizes:
        """
        Load the directory size db for the current user and group(s)
        This is done async in a thread since it can take 1-5 seconds
        """
        # Update the main thread that we are about to load
        self.app.call_from_thread(lambda: self.query_one(MudusLoadingIndicator).show(True))
        self.app.call_from_thread(self.set_db_message, "")

        # Load the data
        dir_sizes, reason_for_error = self.mudus_db.lookup_directory_sizes(
            uid=self.user_id, gid=self.group_id
        )

        # Update the main thread that we are done loading
        self.app.call_from_thread(lambda: self.query_one(MudusLoadingIndicator).show(False))
        if reason_for_error:
            self.app.call_from_thread(self.set_db_message, reason_for_error)

        # Show the newly loaded data
        self.app.call_from_thread(self.show_disk_usage, dir_sizes)

    def show_disk_usage(self, dir_sizes: DirectorySizes):
        """
        Setup the initial view of the disk-usage table
        """
        # Update text above the table
        self.query_one("#mudus_table_title").update(
            Text.from_markup(f"Showing {self.show_what_message}")
        )

        # Update the table contents
        self.directory_sizes: DirectorySizes = dir_sizes
        self.update_dir_size_table(directory_path=self.directory_sizes.top_level_dir)

    def update_dir_size_table(self, directory_path: str):
        """
        Show the directory size information in the table for the given directory path.
        """
        table: DataTable = self.query_one("#mudus_table")

        # Update the table header
        table: DataTable = self.query_one("#mudus_table")
        table.clear(columns=True)
        table.add_column(Text("Directory", justify="left"), key="Directory")
        table.add_column(Text("Cumulative Size [GB]", justify="right"), key="Size")
        table.add_column(Text("Cumulative Num. Files", justify="right"), key="NumFiles")
        table.cursor_type = "row"

        # Update the table contents from this DirectorySizes object
        dir_sizes: DirectorySizes = self.directory_sizes

        # Show link to the parent directory
        if directory_path != dir_sizes.top_level_dir:
            parent_dir = os.path.dirname(directory_path)
            size_parent = dir_sizes.dir_sizes.get(parent_dir, 0)
            numfiles_parent = dir_sizes.num_files.get(parent_dir, 0)
            table.add_row(
                Text.from_markup("[italic]..    (parent directory)[/]"),
                Text.from_markup(f"[italic]{size_parent / 1024**3:.2f}[/]", justify="right"),
                Text.from_markup(f"[italic]{numfiles_parent:,d}[/]", justify="right"),
                key=parent_dir,
            )
            self.parent_dir = parent_dir
        else:
            self.parent_dir = None

        def style_main_row_text(text: str, justify: str) -> Text:
            return Text(text, justify=justify, style=str(self.app.current_theme.accent))

        # Show the sizes of the subdirectories in the current directory
        child_dir_size_total: int = 0
        child_dir_numfiles_total: int = 0
        for size, child in dir_sizes.children(directory_path):
            if directory_path == dir_sizes.top_level_dir:
                # Show full path for the top-level directory
                child_name = child
            else:
                # Show relative path for subdirectories
                child_name = os.path.relpath(child, directory_path)
                # self.query_one("#mudus_debug").update(
                #    f"Showing sub-directories of {directory_path}",
                # )
            numfiles = dir_sizes.num_files.get(child, 0)
            table.add_row(
                style_main_row_text(child_name, justify="left"),
                style_main_row_text(f"{size / 1024**3:.2f}", justify="right"),
                style_main_row_text(f"{numfiles:,d}", justify="right"),
                key=child,  # Use the full path as the key
            )
            child_dir_size_total += size
            child_dir_numfiles_total += numfiles

        # Show totals as the last two rows
        size_this_dir = dir_sizes.dir_sizes.get(directory_path, 0)
        numfiles_this_dir = dir_sizes.num_files.get(directory_path, 0)
        size_files_in_this_dir = size_this_dir - child_dir_size_total
        numfiles_in_this_dir = numfiles_this_dir - child_dir_numfiles_total
        size_overall = dir_sizes.total_size
        table.add_row(
            Text.from_markup("[italic]TOTAL here (files)[/]"),
            Text.from_markup(f"[italic]{size_files_in_this_dir / 1024**3:.2f}[/]", justify="right"),
            Text.from_markup(f"[italic]{numfiles_in_this_dir:,d}[/]", justify="right"),
            key="TOTAL_THIS_DIR_FILES",
        )
        table.add_row(
            Text.from_markup("[italic]TOTAL here (recursive)[/]"),
            Text.from_markup(f"[italic]{size_this_dir / 1024**3:.2f}[/]", justify="right"),
            Text.from_markup(f"[italic]{numfiles_this_dir:,d}[/]", justify="right"),
            key="TOTAL_THIS_DIR_CUMULATIVE",
        )
        table.add_row(
            Text.from_markup("[italic]TOTAL[/]"),
            Text.from_markup(f"[italic]{size_overall / 1024**3:.2f}[/]", justify="right"),
            "",
            key="TOTAL_OVERALL_USER",
        )
        table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        self.highlighted_row = event.row_key.value

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """
        The user selected a row in the directory size table.
        If the row is a directory, update the table to show its contents.
        If the row is a total row, do not allow to select it.
        """
        dir_path = event.row_key.value
        event.stop()
        if dir_path in ("TOTAL_THIS_DIR_FILES", "TOTAL_THIS_DIR_CUMULATIVE", "TOTAL_OVERALL_USER"):
            # Do not allow to select the total rows
            return
        else:
            self.update_dir_size_table(directory_path=dir_path)

    def key_left(self):
        """
        Go to the parent directory if available.
        """
        if self.parent_dir is not None:
            # Go to the parent directory
            self.update_dir_size_table(directory_path=self.parent_dir)

    def key_right(self):
        """
        Go to the currently selected directory if available
        """
        if self.highlighted_row is not None:
            # Enter the currently selected directory
            self.update_dir_size_table(directory_path=self.highlighted_row)
