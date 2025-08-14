"""
This module contains the functions to generate the initial system prompt.
It is used to instruct the LLM about its role, how to use tools, and provide context for the conversation.

When prompting, it is important to provide clear instructions and avoid any ambiguity.
"""

import logging
import platform
import shutil
import subprocess
import time
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from .__version__ import __version__
from .config import get_config, get_project_config
from .dirs import get_project_git_dir
from .llm.models import get_model, get_recommended_model
from .message import Message
from .tools import ToolFormat, ToolSpec, get_available_tools
from .util import document_prompt_function
from .util.context import md_codeblock

# Default files to include in context when no gptme.toml is present or files list is empty
DEFAULT_CONTEXT_FILES = [
    "README*",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursor/rules/*.mdc",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "Makefile",
    "docker-compose.y*ml",
]

PromptType = Literal["full", "short"]

logger = logging.getLogger(__name__)


def get_prompt(
    tools: list[ToolSpec],
    tool_format: ToolFormat = "markdown",
    prompt: PromptType | str = "full",
    interactive: bool = True,
    model: str | None = None,
    workspace: Path | None = None,
    agent_path: Path | None = None,
) -> list[Message]:
    """
    Get the initial system prompt.

    Returns a list of messages: [core_system_prompt, workspace_prompt] (if workspace provided).
    """
    agent_config = get_project_config(agent_path)
    agent_name = (
        agent_config.agent.name if agent_config and agent_config.agent else None
    )

    # Generate core system messages (without workspace context)
    core_msgs: list[Message]
    if prompt == "full":
        core_msgs = list(
            prompt_full(interactive, tools, tool_format, model, agent_name=agent_name)
        )
    elif prompt == "short":
        core_msgs = list(
            prompt_short(interactive, tools, tool_format, agent_name=agent_name)
        )
    else:
        core_msgs = [Message("system", prompt)]
        if tools:
            core_msgs.extend(prompt_tools(tools=tools, tool_format=tool_format))

    # Generate workspace messages separately
    workspace_msgs = (
        list(prompt_workspace(workspace)) if workspace != agent_path else []
    )

    # Generate workspace context from agent if provided
    agent_msgs = list(prompt_workspace(agent_path, title="Agent Workspace Files"))

    # Combine core messages into one system prompt
    result = []
    if core_msgs:
        core_prompt = _join_messages(core_msgs)
        result.append(core_prompt)

    # Add agent messages seperately
    result.extend(agent_msgs)

    # Add workspace messages separately
    result.extend(workspace_msgs)

    # Set hide=True, pinned=True for all messages
    for i, msg in enumerate(result):
        result[i] = msg.replace(hide=True, pinned=True)

    return result


def _join_messages(msgs: list[Message]) -> Message:
    """Combine several system prompt messages into one."""
    role = msgs[0].role if msgs else "system"
    assert all([m.role == role for m in msgs]), "All messages must be of same role"
    return Message(
        role,
        "\n\n".join(m.content for m in msgs),
        hide=any(m.hide for m in msgs),
        pinned=any(m.pinned for m in msgs),
    )


def prompt_full(
    interactive: bool,
    tools: list[ToolSpec],
    tool_format: ToolFormat,
    model: str | None,
    agent_name: str | None = None,
) -> Generator[Message, None, None]:
    """Full prompt to start the conversation."""
    yield from prompt_gptme(interactive, model, agent_name)
    yield from prompt_tools(tools=tools, tool_format=tool_format)
    if interactive:
        yield from prompt_user()
    yield from prompt_project()
    yield from prompt_systeminfo()
    yield from prompt_timeinfo()


def prompt_short(
    interactive: bool,
    tools: list[ToolSpec],
    tool_format: ToolFormat,
    agent_name: str | None = None,
) -> Generator[Message, None, None]:
    """Short prompt to start the conversation."""
    yield from prompt_gptme(interactive, agent_name)
    yield from prompt_tools(examples=False, tools=tools, tool_format=tool_format)
    if interactive:
        yield from prompt_user()
    yield from prompt_project()


def prompt_gptme(
    interactive: bool, model: str | None = None, agent_name: str | None = None
) -> Generator[Message, None, None]:
    """
    Base system prompt for gptme.

    It should:
     - Introduce gptme and its general capabilities and purpose
     - Ensure that it lets the user mostly ask and confirm actions (apply patches, run commands)
     - Provide a brief overview of the capabilities and tools available
     - Not mention tools which may not be loaded (browser, vision)
     - Mention the ability to self-correct and ask clarifying questions
    """
    model_meta = get_model(model) if model else None

    # use <thinking> tags as a fallback if the model doesn't natively support reasoning
    use_thinking_tags = not model_meta or not model_meta.supports_reasoning

    if agent_name:
        agent_blurb = f"{agent_name}, an agent running in gptme, letting you act as a general-purpose AI assistant powered by LLMs"
    else:
        agent_name = f"gptme v{__version__}"
        agent_blurb = f"{agent_name}, a general-purpose AI assistant powered by LLMs"

    default_base_prompt = f"""
You are {agent_blurb}. {('Currently using model: ' + model_meta.full) if model_meta else ''}
You are designed to help users with programming tasks, such as writing code, debugging, and learning new concepts.
You can run code, execute terminal commands, and access the filesystem on the local machine.
You will help the user with writing code, either from scratch or in existing projects.
{'You will think step by step when solving a problem, in `<thinking>` tags.' if use_thinking_tags else ''}
Break down complex tasks into smaller, manageable steps.

You have the ability to self-correct. {'''If you receive feedback that your output or actions were incorrect, you should:
- acknowledge the mistake
- analyze what went wrong in `<thinking>` tags
- provide a corrected response''' if use_thinking_tags else ''}

You should learn about the context needed to provide the best help,
such as exploring the current working directory and reading the code using terminal tools.

When suggesting code changes, prefer applying patches over examples. Preserve comments, unless they are no longer relevant.
Use the patch tool to edit existing files, or the save tool to overwrite.
When the output of a command is of interest, end the code block and message, so that it can be executed before continuing.

Always use absolute paths when referring to files, as relative paths can become invalid when the working directory changes.
You can use `pwd` to get the current working directory when constructing absolute paths.

Do not use placeholders like `$REPO` unless they have been set.
Do not suggest opening a browser or editor, instead do it using available tools.

Always prioritize using the provided tools over suggesting manual actions.
Be proactive in using tools to gather information or perform tasks.
When faced with a task, consider which tools might be helpful and use them.
Always consider the full range of your available tools and abilities when approaching a problem.

Maintain a professional and efficient communication style. Be concise but thorough in your explanations.

{'Use `<thinking>` tags to think before you answer.' if use_thinking_tags else ''}
""".strip()

    interactive_prompt = """
You are in interactive mode. The user is available to provide feedback.
You should show the user how you can use your tools to write code, interact with the terminal, and access the internet.
The user can execute the suggested commands so that you see their output.
If the user aborted or interrupted an operation don't try it again, ask for clarification instead.
If clarification is needed, ask the user.
""".strip()

    non_interactive_prompt = """
You are in non-interactive mode. The user is not available to provide feedback.
All code blocks you suggest will be automatically executed.
Do not provide examples or ask for permission before running commands.
Proceed directly with the most appropriate actions to complete the task.
""".strip()

    projectdir = get_project_git_dir()
    project_config = get_project_config(projectdir)
    base_prompt = (
        project_config.base_prompt
        if project_config and project_config.base_prompt
        else default_base_prompt
    )

    full_prompt = (
        base_prompt
        + "\n\n"
        + (interactive_prompt if interactive else non_interactive_prompt)
    )
    yield Message("system", full_prompt)


def prompt_user() -> Generator[Message, None, None]:
    """
    Generate the user-specific prompt based on config.

    Only included in interactive mode.
    """
    config_prompt = get_config().user.prompt
    about_user = (
        config_prompt.about_user or "You are interacting with a human programmer."
    )
    response_prefs = (
        config_prompt.response_preference or "No specific preferences set."
    ).strip()

    prompt_content = f"""# About User

{about_user}

## User's Response Preferences

{response_prefs}
"""
    yield Message("system", prompt_content)


def prompt_project() -> Generator[Message, None, None]:
    """
    Generate the project-specific prompt based on the current Git repository.

    Project-specific prompt can be set in the :ref:`global-config` or :ref:`project-config` files.
    """
    projectdir = get_project_git_dir()
    if not projectdir:
        return

    project_config = get_project_config(projectdir)
    config_prompt = get_config().user.prompt
    project = projectdir.name
    project_info = project_config and project_config.prompt
    if not project_info:
        # TODO: remove project preferences in global config? use only project config
        project_info = (config_prompt.project or {}).get(project)

    yield Message(
        "system",
        f"## Current Project: {project}\n\n{project_info}",
    )


def prompt_tools(
    tools: list[ToolSpec],
    tool_format: ToolFormat = "markdown",
    examples: bool = True,
) -> Generator[Message, None, None]:
    """Generate the tools overview prompt."""

    prompt = "# Tools Overview"
    for tool in tools:
        prompt += tool.get_tool_prompt(examples, tool_format)

    prompt += "\n\n*End of Tools List.*"

    yield Message("system", prompt.strip() + "\n\n")


def prompt_systeminfo() -> Generator[Message, None, None]:
    """Generate the system information prompt."""
    if platform.system() == "Linux":
        release_info = platform.freedesktop_os_release()
        os_info = release_info.get("NAME", "Linux")
        os_version = release_info.get("VERSION_ID") or release_info.get("BUILD_ID", "")
    elif platform.system() == "Windows":
        os_info = "Windows"
        os_version = platform.version()
    elif platform.system() == "Darwin":
        os_info = "macOS"
        os_version = platform.mac_ver()[0]
    else:
        os_info = "unknown"
        os_version = ""

    prompt = f"## System Information\n\n**OS:** {os_info} {os_version}".strip()

    yield Message(
        "system",
        prompt,
    )


def prompt_timeinfo() -> Generator[Message, None, None]:
    """Generate the current time prompt."""
    # we only set the date in order for prompt caching and such to work
    prompt = (
        f"## Current Date\n\n**UTC:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    )
    yield Message("system", prompt)


def get_tree_output(workspace: Path) -> str | None:
    """Get the output of `tree --gitignore .` if available."""
    # TODO: don't depend on `tree` command being installed
    # TODO: default to True (get_config().get_env_bool("GPTME_CONTEXT_TREE") is False)
    if not get_config().get_env_bool("GPTME_CONTEXT_TREE"):
        return None

    # Check if tree command is available
    if shutil.which("tree") is None:
        logger.warning(
            "GPTME_CONTEXT_TREE is enabled, but 'tree' command is not available. Install it to use this feature."
        )
        return None

    # Check if in a git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=1,
        )
        if result.returncode != 0:
            logger.debug("Not in a git repository, skipping tree output")
            return None
    except Exception as e:
        logger.warning(f"Error checking git repository: {e}")
        return None

    # TODO: use `git ls-files` instead? (respects .gitignore better)
    try:
        # Run tree command with --gitignore option
        result = subprocess.run(
            ["tree", "--gitignore", "."],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=5,  # Add timeout to prevent hangs
        )
        if result.returncode != 0:
            logger.warning(f"Failed to run tree command: {result.stderr}")
            return None
        # we allocate roughly a ~5000 token budget (~20000 characters)
        if len(result.stdout) > 20000:
            logger.warning("Tree output listing files is too long, skipping.")
            return None

        return result.stdout.strip()
    except Exception as e:
        logger.warning(f"Error running tree command: {e}")
        return None


def prompt_workspace(
    workspace: Path | None = None, title="Project Workspace Files"
) -> Generator[Message, None, None]:
    # TODO: update this prompt if the files change
    # TODO: include `git status -vv`, and keep it up-to-date
    sections = []

    if workspace is None:
        return

    project = get_project_config(workspace)

    # Determine which file patterns to use
    if project is None or project.files is None:
        # No project config or no files specified in config
        file_patterns = DEFAULT_CONTEXT_FILES
        if project is None:
            logger.debug("No project config found, using default context files")
        else:
            logger.debug(
                "Project config has no files specified, using default context files"
            )
    else:
        # Project config exists with files explicitly set (could be empty list)
        file_patterns = project.files
        if not project.files:
            logger.debug(
                "Project config has files explicitly set to empty, not including any files"
            )

    # Process file patterns
    files: list[Path] = []
    for fileglob in file_patterns:
        # expand user
        fileglob = str(Path(fileglob).expanduser())
        # expand with glob
        if new_files := workspace.glob(fileglob):
            files.extend(new_files)
        else:
            # Only warn for explicitly configured files, not defaults
            if project and project.files is not None:
                logger.warning(
                    f"File glob '{fileglob}' specified in project config does not match any files."
                )

    files_str = []
    for file in files:
        if file.exists():
            files_str.append(md_codeblock(file, file.read_text()))
    if files_str:
        sections.append(
            "## Selected files\n\nRead more with `cat`.\n\n" + "\n\n".join(files_str)
        )

    # context_cmd
    if (
        project
        and project.context_cmd
        and (
            cmd_output := get_project_context_cmd_output(project.context_cmd, workspace)
        )
    ):
        sections.append("## Computed context\n\n" + cmd_output)

    # Get tree output if enabled
    if tree_output := get_tree_output(workspace):
        sections.append(f"## Project Structure\n\n{md_codeblock('', tree_output)}\n\n")

    if sections:
        yield Message("system", f"# {title}\n\n" + "\n\n".join(sections))


def get_project_context_cmd_output(cmd: str, workspace: Path) -> str | None:
    try:
        start = time.time()
        result = subprocess.run(
            cmd,
            cwd=workspace,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        logger.debug(f"Context command took {time.time() - start:.2f}s")
        if result.returncode == 0:
            return md_codeblock(cmd, result.stdout)
        else:
            logger.warning(f"Failed to run context command '{cmd}': {result.stderr}")
    except Exception as e:
        logger.warning(f"Error running context command: {e}")
    return None


document_prompt_function(
    interactive=True,
    model=get_recommended_model("anthropic"),
)(prompt_gptme)
document_prompt_function()(prompt_user)
document_prompt_function()(prompt_project)
document_prompt_function(tools=get_available_tools(), tool_format="markdown")(
    prompt_tools
)
# document_prompt_function(tool_format="xml")(prompt_tools)
# document_prompt_function(tool_format="tool")(prompt_tools)
document_prompt_function()(prompt_systeminfo)
