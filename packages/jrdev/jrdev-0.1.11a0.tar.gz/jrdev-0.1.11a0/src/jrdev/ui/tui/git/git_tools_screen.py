import os

from jrdev.ui.tui.command_request import CommandRequest
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, Static, MarkdownViewer, LoadingIndicator, ListView, Select
from textual import on, work
from textual.worker import Worker, WorkerState
from typing import Any, Dict, Optional
import logging

from jrdev.commands.git_config import get_git_config, save_git_config, DEFAULT_GIT_CONFIG
from jrdev.services.git_pr_service import generate_pr_analysis, GitPRServiceError
from jrdev.file_operations.file_utils import JRDEV_ROOT_DIR
from jrdev.ui.tui.git.git_overview_widget import GitOverviewWidget
from jrdev.utils.git_utils import is_git_installed, get_all_branches_and_tags
from jrdev.ui.tui.model_listview import ModelListView
from jrdev.ui.tui.terminal.terminal_output_widget import TerminalOutputWidget

logger = logging.getLogger("jrdev")

class GitToolsScreen(ModalScreen):
    """Modal screen for managing Git tool settings and generating PR content."""

    DEFAULT_CSS = """
    GitToolsScreen {
        align: center middle;
    }

    #git-tools-container {
        width: 100%;
        height: 100%;
        background: $surface;
        border: round $accent;
        padding: 0;
        margin: 0;
        layout: vertical; /* Main layout is vertical */
    }

    #header {
        dock: top;
        height: 3;
        padding: 0 0;
        border-bottom: solid $accent;
    }

    #header-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }

    /* Container for sidebar and content */
    #main-content-horizontal {
        height: 100%;
        layout: horizontal;
        padding: 0;
    }

    #sidebar {
        width: 20;
        height: 100%;
        border-right: solid $panel;
        padding: 0 0;
        transition: width 0.2s out_expo;
    }

    #sidebar.collapsed {
        width: 3;
        min-width: 3;
    }

    #sidebar-title {
        height: 2;
        width: 1fr;
        padding: 0 1;
        content-align: center middle;
        text-style: bold;
        color: $text;
        border-bottom: solid $panel;
    }

    .sidebar-button {
        width: 100%;
        height: 3;
        margin: 1 0 0 0; /* Keep margin */
        border: none;
        /* background: $surface-darken-2; Use default or selected */
    }

    .sidebar-button:hover {
        background: $primary-darken-1; /* Match ModelProfileScreen hover */
    }

    .sidebar-button.selected {
        background: $primary; /* Match ModelProfileScreen selected */
        text-style: bold;
        /* color: $text; Use default */
    }

    #collapse-sidebar-btn {
        dock: bottom;
        border: none;
        width: 100%;
        min-width: 3;
        height: 1;
        background: $surface;
        margin: 0;
        padding: 0;
    }

    #collapse-sidebar-btn:hover {
        background: $primary-darken-1;
    }

    #content-area {
        width: 1fr;
        height: 100%;
        layout: vertical;
        padding: 0;
    }

    /* View Containers */
    #overview-view,
    #configure-view,
    #pr-summary-view,
    #pr-review-view,
    #help-view { /* Added help-view */
        height: 100%; /* Take available space */
        display: block; /* Initially visible, will be controlled */
        padding: 0;
        margin: 0;
        overflow-y: auto; /* Allow scrolling within view */
        overflow-x: hidden;
    }

    /* Configure View Specific */
    #git-config-grid {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-columns: 16 1fr; /* Label width and flexible input */
        margin-top: 1;
        height: auto;
    }
    #base-branch-label {
        height: 1;
        align-vertical: middle;
        text-align: right;
        margin-right: 1;
        text-style: bold;
        color: $accent;
    }
    #base-branch-select {
        height: 3;
        width: auto;
        max-width: 80;
        border: round #63f554;
        margin: 0;
        padding: 0;
        &:focus > SelectCurrent {
            border: none;
            background-tint: $foreground 5%;
        }
        & > SelectOverlay {
            width: 1fr;
            display: none;
            height: auto;
            max-height: 12;
            overlay: screen;
            constrain: none inside;
            color: $foreground;
            border: tall $border-blurred;
            background: $surface;
            &:focus {
                background-tint: $foreground 5%;
            }
            & > .option-list--option {
                padding: 0 1;
            }
        }
        &.-expanded {
            .down-arrow {
                display: none;
            }
            .up-arrow {
                display: block;
            }
            & > SelectOverlay {
                display: block;
            }
        }
    }
    #git-config-grid > Input {
        height: 1;
        border: none;
    }
    #config-buttons {
        margin-top: 1;
        height: auto;
        align-horizontal: left;
    }
    #config-buttons Button {
        margin-right: 1;
        border: none;
    }

    /* PR Summary / Review View Specific */
    .pr-view-container {
        layers: bottom top;
        height: 100%; /* Fill the view container */
        layout: vertical;
    }
    .pr-view-title {
        height: 1;
        text-style: bold;
        margin-bottom: 0;
        align-horizontal: left;
    }
    .pr-prompt-input {
        layer: bottom;
        height: 3;
        margin-bottom: 0;
        border: round $accent;
    }
    .pr-prompt-input:focus {
        border: round $accent; /* Keep the same border on focus */
    }
    /* Style the TerminalOutputWidget itself */
    #summary-output-widget,
    #review-output-widget {
        layer: bottom;
        height: 1fr; /* Take remaining space */
        margin: 0;
        padding: 0;
        border: round $accent;
    }
    /* Style the inner TerminalTextArea */
    #summary-output-widget > #terminal_output,
    #review-output-widget > #terminal_output {
        background: $surface-darken-1;
        border: round $surface-lighten-1;
    }
    .pr-buttons {
        layer: bottom;
        align-horizontal: left;
        /* Ensure container can hold button or indicator */
        height: 1; /* Match button height */
        align-vertical: middle;
    }
    #model-list-summary, #model-list-review {
        layer: top;
        width: auto;
        height: 10;
        border: round $accent;
    }
    .pr-buttons Button {
        margin-left: 1;
        border: none;
        height: 100%; /* Fill vertical space */
    }
    /* Style for the LoadingIndicator */
    .pr-buttons LoadingIndicator {
        color: $accent;
        margin-left: 1;
        height: 1; /* Keep it compact */
        width: auto;
        /* align: center middle; /* Align within its space */
    }

    /* Help View Specific */
    #help-view MarkdownViewer {
        height: 1fr; /* Fill the container */
        background: $surface-darken-1;
        border: round $surface-lighten-1;
        padding: 1;
    }

    #footer {
        dock: bottom;
        height: 3;
        padding: 0 1;
        border-top: solid $accent;
        align: left middle;
    }
    #footer Button {
        margin-right: 1; /* Add margin to the right */
        border: none;
    }
    """

    def __init__(self, core_app: Any) -> None:
        super().__init__()
        self.core_app = core_app
        self.current_config: Dict[str, Any] = {}
        self.active_view: str = "overview" # 'overview', 'configure', 'pr_summary', 'pr_review', 'help'
        self.pr_summary_vlayout = Vertical(id="pr-summary-view", classes="pr-view-container")

        # Not ideal, but we have to manage two model_list popups for this class
        self.model_btn_summary = Button(self.core_app.state.model, classes="select-model-btn", variant="primary", tooltip="Model used to generate summary")
        self.model_list_summary = ModelListView(id="model-list-summary", core_app=self.core_app, model_button=self.model_btn_summary, above_button=False)
        self.model_list_summary.visible = False
        self.model_btn_review = Button(self.core_app.state.model, classes="select-model-btn", variant="primary",
                                        tooltip="Model used to generate review")
        self.model_list_review = ModelListView(id="model-list-review", core_app=self.core_app,
                                                model_button=self.model_btn_review, above_button=False)
        self.model_list_review.visible = False

    def compose(self) -> ComposeResult:
        with Vertical(id="git-tools-container"):
            # Header
            with Horizontal(id="header"):
                yield Label("Git Tools Management", id="header-title")

            # Main content area (Sidebar + Content)
            with Horizontal(id="main-content-horizontal"):
                # Sidebar
                with Vertical(id="sidebar"):
                    yield Label("Tools", id="sidebar-title")
                    yield Button("Overview", id="btn-overview", classes="sidebar-button selected")
                    yield Button("Configure", id="btn-configure", classes="sidebar-button")
                    yield Button("PR Summary", id="btn-pr-summary", classes="sidebar-button")
                    yield Button("PR Review", id="btn-pr-review", classes="sidebar-button")
                    yield Button("Help", id="btn-help", classes="sidebar-button")
                    yield Button("\u25c3 Collapse", id="collapse-sidebar-btn")

                # Content Area
                with Vertical(id="content-area"):
                    # Overview View
                    with Vertical(id="overview-view"):
                        yield GitOverviewWidget(self.core_app)

                    # Configure View (Initially Hidden)
                    with Vertical(id="configure-view"):
                        yield Label("Git Configuration", classes="pr-view-title")
                        with Container(id="git-config-grid"):
                            yield Label("Base Branch:", id="base-branch-label")
                            yield Select(options=[("Loading...", "Loading...")], id="base-branch-select", allow_blank=False)
                        yield Static("Upstream branch used for 'git diff' in PR commands (default: 'origin/main')", classes="text-muted")
                        with Horizontal(id="config-buttons"):
                            yield Button("Save", id="save-config-btn", variant="success")

                    # PR Summary View (Initially Hidden)
                    with self.pr_summary_vlayout:
                        yield Label("Generate PR Summary", classes="pr-view-title")
                        yield Input(id="summary-prompt-input", placeholder="Optional: Add custom instructions...", classes="pr-prompt-input")
                        yield self.model_list_summary
                        with Horizontal(classes="pr-buttons", id="summary-buttons"):
                            yield Button("Generate Summary", id="generate-summary-btn", variant="primary")
                            yield self.model_btn_summary
                            # LoadingIndicator will be added here dynamically
                        yield TerminalOutputWidget(id="summary-output-widget", output_widget_mode=True)

                    # PR Review View (Initially Hidden)
                    with Vertical(id="pr-review-view", classes="pr-view-container"):
                        yield Label("Generate PR Review", classes="pr-view-title")
                        yield Input(id="review-prompt-input", placeholder="Optional: Add custom instructions...", classes="pr-prompt-input")
                        yield self.model_list_review
                        with Horizontal(classes="pr-buttons", id="review-buttons"):
                            yield Button("Generate Review", id="generate-review-btn", variant="primary")
                            yield self.model_btn_review
                            # LoadingIndicator will be added here dynamically
                        yield TerminalOutputWidget(id="review-output-widget", output_widget_mode=True)

                    # Help View (Initially Hidden)
                    with Vertical(id="help-view"):
                        yield MarkdownViewer(id="help-markdown-viewer", show_table_of_contents=False)

            # Footer (Common Close Button)
            with Horizontal(id="footer"): # Footer docked at the bottom of main container
                yield Button("Close", id="close-btn", variant="default")

    def on_mount(self) -> None:
        """Load config, help content, and set initial view."""
        self.load_config()
        self.load_help_content()
        self.update_view_visibility()
        if not is_git_installed():
            self.query_one("#btn-overview").disabled = True
            self.query_one("#btn-pr-summary").disabled = True
            self.query_one("#btn-pr-review").disabled = True
            overview_view = self.query_one("#overview-view", Vertical)
            for child in overview_view.children:
                child.remove()
            warning_text = (
                "[bold red]Git is not installed![/]\n\n"
                "Please install Git to use the Git tools.\n\n"
                "Installation instructions:\n"
                "- [bold]Mac[/]: Install via Homebrew: [code]brew install git[/]\n"
                "  Or download from https://git-scm.com/download/mac\n"
                "- [bold]Linux[/]: Use your package manager, e.g.,\n"
                "  Ubuntu: [code]sudo apt install git[/]\n"
                "  CentOS: [code]sudo yum install git[/]\n"
                "- [bold]Windows[/]: Download the installer from https://git-scm.com/download/win\n\n"
                "After installation, restart the application or reopen this screen."
            )
            overview_view.mount(MarkdownViewer(warning_text, show_table_of_contents=False))
        else:
            self.load_branches_worker()
            try:
                self.query_one("#unstaged-files-list", ListView).focus()
            except Exception as e:
                logger.error(f"Could not focus default element on mount: {e}")

    def load_config(self) -> None:
        """Load current git config."""
        self.current_config = get_git_config(self.core_app)

    def load_help_content(self) -> None:
        """Load the markdown content into the help viewer."""
        help_file_path = os.path.join(JRDEV_ROOT_DIR, "src", "jrdev", "docs", "git_explanation.md")
        markdown_viewer = self.query_one("#help-markdown-viewer", MarkdownViewer)
        try:
            with open(help_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Update the viewer's document asynchronously
            self.call_later(markdown_viewer.document.update, content)
        except FileNotFoundError:
            logger.error(f"Help file not found: {help_file_path}")
            self.call_later(markdown_viewer.document.update, f"# Error\n\nCould not load help file from: `{help_file_path}`")
        except Exception as e:
            logger.error(f"Error reading help file {help_file_path}: {e}")
            self.call_later(markdown_viewer.document.update, f"# Error\n\nAn error occurred while reading the help file: {e}")

    def update_view_visibility(self) -> None:
        """Show the active view and hide others."""
        views = {
            "overview": "#overview-view",
            "configure": "#configure-view",
            "pr_summary": "#pr-summary-view",
            "pr_review": "#pr-review-view",
            "help": "#help-view"
        }
        buttons = {
            "overview": "#btn-overview",
            "configure": "#btn-configure",
            "pr_summary": "#btn-pr-summary",
            "pr_review": "#btn-pr-review",
            "help": "#btn-help"
        }

        for view_name, view_id in views.items():
            try:
                view_widget = self.query_one(view_id)
                view_widget.styles.display = "block" if view_name == self.active_view else "none"
            except Exception as e:
                logger.error(f"Error finding view {view_id}: {e}")

        for btn_name, btn_id in buttons.items():
            try:
                btn_widget = self.query_one(btn_id, Button)
                if btn_name == self.active_view:
                    btn_widget.add_class("selected")
                else:
                    btn_widget.remove_class("selected")
            except Exception as e:
                logger.error(f"Error finding button {btn_id}: {e}")

    @on(Button.Pressed, ".sidebar-button")
    def handle_sidebar_button(self, event: Button.Pressed) -> None:
        """Switch the active view based on sidebar button press."""
        button_id = event.button.id
        if button_id == "btn-overview":
            self.active_view = "overview"
            try:
                overview_widget = self.query_one(GitOverviewWidget)
                overview_widget.refresh_git_status()
                self.query_one("#unstaged-files-list", ListView).focus()
            except Exception as e:
                logger.error(f"Could not refresh or focus overview widget: {e}")
        elif button_id == "btn-configure":
            self.active_view = "configure"
            self.query_one("#base-branch-select", Select).focus()
        elif button_id == "btn-pr-summary":
            self.active_view = "pr_summary"
            self.query_one("#summary-prompt-input", Input).focus()
            self.update_model_buttons(self.core_app.state.model)
        elif button_id == "btn-pr-review":
            self.active_view = "pr_review"
            self.query_one("#review-prompt-input", Input).focus()
            self.update_model_buttons(self.core_app.state.model)
        elif button_id == "btn-help": # Handle help button
            self.active_view = "help"
            # No specific focus needed for help view
        self.update_view_visibility()

    @on(Button.Pressed, "#collapse-sidebar-btn")
    def toggle_sidebar_collapse(self, event: Button.Pressed) -> None:
        """Toggle the collapsed state of the sidebar."""
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("collapsed")
        is_collapsed = sidebar.has_class("collapsed")
        if is_collapsed:
            event.button.label = "\u25b9"
        else:
            event.button.label = "\u25c3 Collapse"

    # --- Configure View Handler ---
    @on(Button.Pressed, "#save-config-btn")
    def handle_save_config(self) -> None:
        """Save the updated git configuration."""
        select_widget = self.query_one("#base-branch-select", Select)
        new_base_branch = select_widget.value

        if not new_base_branch:
            self.notify("Base branch cannot be empty.", severity="error")
            return

        self.current_config["base_branch"] = new_base_branch

        if save_git_config(self.core_app, self.current_config):
            logger.info(f"Git base branch updated to '{new_base_branch}'.")
            # Notify within the modal too
            self.notify(f"Git base branch updated to '{new_base_branch}'.", severity="information")
        else:
            logger.error("Failed to save Git configuration.")
            self.notify("Failed to save Git configuration.", severity="error")

    @work(group="git_tools", exclusive=True, name="load_branches", thread=True)
    def load_branches_worker(self) -> None:
        """Worker to load git branches into the Select widget."""
        branches_and_tags = get_all_branches_and_tags()
        if branches_and_tags:
            self.call_later(self.update_branch_options, branches_and_tags)

    def update_branch_options(self, branches_and_tags: list[str]) -> None:
        """Update the options of the branch select widget."""
        select_widget = self.query_one("#base-branch-select", Select)
        
        current_value = self.current_config.get("base_branch", DEFAULT_GIT_CONFIG["base_branch"])
        
        select_widget.set_options([(item, item) for item in branches_and_tags])
        
        # Restore the selection if it exists in the new options
        if current_value in branches_and_tags:
            select_widget.value = current_value
        elif branches_and_tags:
            # Fallback to the first available branch/tag if the saved one is not found
            select_widget.value = branches_and_tags[0]
        
        # If the value was "Loading...", it might not be in the new options, so we need to set it again.
        if select_widget.value == "Loading...":
            if current_value in branches_and_tags:
                select_widget.value = current_value
            elif branches_and_tags:
                select_widget.value = branches_and_tags[0]

    @on(Button.Pressed, ".select-model-btn")
    def handle_model_select(self, event: Button.Pressed) -> None:
        # popup the correct list
        if event.button == self.model_btn_summary:
            self.model_list_summary.set_visible(not self.model_list_summary.visible)
        else:
            self.model_list_review.set_visible(not self.model_list_review.visible)

    @on(ModelListView.ModelSelected, "#model-list-summary, #model-list-review")
    def handle_model_selection(self, selected: ModelListView.ModelSelected):
        # send model update request to core app
        model_name = selected.model
        self.post_message(CommandRequest(f"/model set {model_name}"))

        # hide any visible selection lists
        self.model_list_summary.set_visible(False)
        self.model_list_review.set_visible(False)

        # update model button labels
        self.update_model_buttons(model_name)

    def update_model_buttons(self, model_name: str) -> None:
        for btn in self.query(".select-model-btn"):
            btn.label = model_name
            btn.styles.max_width = len(model_name) + 2

    # --- PR Summary View Handler ---
    @on(Button.Pressed, "#generate-summary-btn")
    def handle_generate_summary(self) -> None:
        """Trigger the PR summary generation worker with loading indicator."""
        prompt_input = self.query_one("#summary-prompt-input", Input)
        custom_prompt = prompt_input.value.strip()
        output_widget = self.query_one("#summary-output-widget", TerminalOutputWidget)
        button = self.query_one("#generate-summary-btn", Button)
        button_container = self.query_one("#summary-buttons") # Use specific ID

        output_widget.terminal_output.load_text("") # Clear previous output
        button.styles.display = "none" # Hide button
        indicator = LoadingIndicator()
        button_container.mount(indicator) # Add indicator

        # Directly call the @work decorated method
        self.generate_pr_summary_worker(custom_prompt)

    # --- PR Review View Handler ---
    @on(Button.Pressed, "#generate-review-btn")
    def handle_generate_review(self) -> None:
        """Trigger the PR review generation worker with loading indicator."""
        prompt_input = self.query_one("#review-prompt-input", Input)
        custom_prompt = prompt_input.value.strip()
        output_widget = self.query_one("#review-output-widget", TerminalOutputWidget)
        button = self.query_one("#generate-review-btn", Button)
        button_container = self.query_one("#review-buttons") # Use specific ID

        output_widget.terminal_output.load_text("") # Clear previous output
        button.styles.display = "none" # Hide button
        indicator = LoadingIndicator()
        button_container.mount(indicator) # Add indicator

        # Directly call the @work decorated method
        self.generate_pr_review_worker(custom_prompt)

    # --- Worker Completion Handler ---
    async def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle the completion of background workers for PR generation."""
        worker = event.worker
        state = event.state

        # Only handle completion states for 'git_pr' group workers
        if worker.group == "git_pr" and state in (WorkerState.SUCCESS, WorkerState.ERROR):
            logger.info(f"Worker '{worker.name}' finished with state: {state}")

            # Determine which operation finished based on worker name
            button_id = None
            output_widget_id = None
            button_container_id = None
            operation_name = "unknown"

            if worker.name == "git_pr_summary":
                button_id = "#generate-summary-btn"
                output_widget_id = "#summary-output-widget"
                button_container_id = "#summary-buttons"
                operation_name = "PR Summary"
            elif worker.name == "git_pr_review":
                button_id = "#generate-review-btn"
                output_widget_id = "#review-output-widget"
                button_container_id = "#review-buttons"
                operation_name = "PR Review"

            if not button_id:
                logger.warning(f"Could not determine which PR operation finished for worker '{worker.name}'. UI might not update correctly.")
                # Fallback: Try to remove any indicators and show both buttons
                for container_id in ["#summary-buttons", "#review-buttons"]:
                    try:
                        container = self.query_one(container_id)
                        indicator = container.query_one(LoadingIndicator)
                        await indicator.remove()
                    except Exception:
                        pass
                try: self.query_one("#generate-summary-btn", Button).styles.display = "block"
                except Exception: pass
                try: self.query_one("#generate-review-btn", Button).styles.display = "block"
                except Exception: pass
                return

            try:
                # Query for the specific UI elements
                button = self.query_one(button_id, Button)
                output_widget = self.query_one(output_widget_id, TerminalOutputWidget)
                button_container = self.query_one(button_container_id)

                # Find and remove the loading indicator within the button's container
                try:
                    indicator = button_container.query_one(LoadingIndicator)
                    await indicator.remove() # Use await for async removal
                    logger.debug(f"Removed loading indicator for {operation_name}")
                except Exception as e:
                    logger.warning(f"Could not find or remove loading indicator for {operation_name}: {e}")

                # Show the button again
                button.styles.display = "block"
                logger.debug(f"Restored button visibility for {operation_name}")

                # Clear previous output and display result/error
                output_widget.terminal_output.load_text("") # Clear output
                if state == WorkerState.SUCCESS:
                    result = worker.result
                    if isinstance(result, str):
                        output_widget.append_text(result)
                        logger.info(f"Displayed success result for {operation_name}")
                    else:
                        output_widget.append_text("Generation finished, but no text output was received.")
                        logger.warning(f"Worker {operation_name} finished successfully but result was not a string: {type(result)}")
                elif state == WorkerState.ERROR:
                    error = worker.error
                    error_msg = f"An error occurred during {operation_name} generation:\n{error}\nCheck logs for details."
                    # Special handling for GitPRServiceError to show details
                    if isinstance(error, GitPRServiceError):
                        error_msg += f"\nDetails: {error.details}"
                    elif isinstance(error, RuntimeError) and error.args and isinstance(error.args[0], str) and "GitPRServiceError" in error.args[0]:
                        # Attempt to extract details if wrapped in RuntimeError
                        try:
                            # This is fragile, depends on the exact wrapping format
                            detail_str = error.args[0].split("Details: ", 1)[1]
                            error_msg += f"\nDetails: {detail_str}"
                        except IndexError:
                            pass # Couldn't parse details

                    output_widget.append_text(error_msg)
                    logger.error(f"Displayed error for {operation_name}: {error}")

            except Exception as e:
                logger.exception(f"Error updating UI after {operation_name} worker completed: {e}")
                self.notify(f"Error updating UI for {operation_name}. Check logs.", severity="error")

    # --- Worker Methods ---

    @work(group="git_pr", exclusive=True, name="git_pr_summary")
    async def generate_pr_summary_worker(self, custom_prompt: str) -> Optional[str]:
        """Worker method to generate PR summary content."""
        return await self._generate_pr_content_base("summary", custom_prompt)

    @work(group="git_pr", exclusive=True, name="git_pr_review")
    async def generate_pr_review_worker(self, custom_prompt: str) -> Optional[str]:
        """Worker method to generate PR review content."""
        return await self._generate_pr_content_base("review", custom_prompt)

    async def _generate_pr_content_base(self, pr_type: str, custom_prompt: str) -> Optional[str]:
        """Base coroutine logic for generating PR content (summary or review)."""
        args = ["/git", "pr", pr_type] # Base args

        prompt_path = f"git/pr_{pr_type}"
        add_project_files = (pr_type == "review")
        base_branch = self.current_config.get("base_branch", DEFAULT_GIT_CONFIG["base_branch"])

        try:
            # generate_pr_analysis might print intermediate steps via app.ui.print_text
            # We capture the final result or error here.
            response, error = await generate_pr_analysis(
                app=self.core_app,
                base_branch=base_branch,
                prompt_path=prompt_path,
                user_prompt=custom_prompt,
                add_project_files=add_project_files,
                worker_id=None # Worker ID might be useful if generate_pr_analysis needs it
            )

            if error:
                # Raise an exception that the callback can catch
                # Ensure the original error type (GitPRServiceError) is preserved
                raise error
            elif response:
                return f"{response}\n`Generated by JrDev AI using {self.core_app.state.model}`"
            else:
                # No response and no error (e.g., no diff)
                return "No changes detected or no output generated."

        except GitPRServiceError as e:
            logger.error(f"Handled error during PR {pr_type} generation: {e}")
            return f"Generation failed: {e.details}. Check branch configuration and that git is installed."
        except ValueError as e: # From shlex.split or potentially other issues
            logger.error(f"Value error during PR {pr_type} generation: {e}.")
            return f"Generation failed: {e}. Check branch configuration and that git is installed."
        except Exception as e:
            logger.exception(f"Unexpected error during PR {pr_type} generation")
            # Wrap unexpected errors for better context in the callback
            return f"An unexpected error occurred during PR {pr_type} generation: {e}. Check branch configuration and that git is installed."

    # --- Footer Handler ---
    @on(Button.Pressed, "#close-btn")
    def handle_close(self) -> None:
        """Close the screen."""
        self.dismiss(None)
