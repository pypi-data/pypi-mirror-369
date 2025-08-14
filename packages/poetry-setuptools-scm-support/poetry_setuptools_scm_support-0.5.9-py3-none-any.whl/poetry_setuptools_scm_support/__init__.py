import tomlkit
from cleo.commands.command import Command
from cleo.io.inputs.argument import Argument
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.factory import Factory
from poetry.poetry import Poetry

from setuptools_scm import Configuration, get_version
from setuptools_scm.version import calver_by_date, release_branch_semver_version

import warnings

from tomlkit.exceptions import NonExistentKey


def _do_scm(c: Configuration) -> str:
    return get_version(root=c.root, relative_to=c.relative_to)


def _do_date_and_dirty(c: Configuration) -> str:
    return get_version(root=c.root, relative_to=c.relative_to, version_scheme=calver_by_date)


def _do_semver_branch(c: Configuration) -> str:
    return get_version(root=c.root, relative_to=c.relative_to, version_scheme=release_branch_semver_version)


class CalculateVersion(Command):
    """
    Calculates the version of the package.

    command:name {version-calculate : Controls output format}
    """

    name = "version-calculate"
    description = "Calculates the version of the project relying on setuptools_scm"

    args_description = """
        scm: Formats according to setuptools_scm <info>get_version</info> default behavior. e.g. <info>0.1.dev1+g1e0ede4</info>.
        date: Formats current date and distance, e.g. <info>2025.4.1.1.dev1+g9d4edec</info> . Scheme used is <info>calver_by_date</info> function
        branch: Use branch based versioning of library. Scheme used is <info>release_branch_semver_version</info> function
        default: Use project plugin configuration (see documentation) or scm if not defined.
    """
    arguments = [
        Argument(name="format", description=args_description, default="default", required=False),
    ]


    def _prepare(self, poetry: Poetry):

        ok_tool_section = True
        ok_tool_section_setuptools_scm = True

        try:
            _ = poetry.pyproject.data.item('tool')
            if poetry.pyproject.data.item('tool').get('setuptools_scm') is None:
                ok_tool_section_setuptools_scm = False

        except (NonExistentKey, KeyError):
            ok_tool_section = False

        if ok_tool_section_setuptools_scm and ok_tool_section:
            pass
        else:
            ok = self.ask(
                'No tool.setuptools_scm entry found in <info>pyproject.toml</info>. Would you like to add it? [Y/n]',
                'Y')
            if ok == 'Y':
                if not ok_tool_section:
                    self.line("Adding section to <info>pyproject.toml</info>.")
                    poetry.pyproject.data.add('tool', tomlkit.item({}))
                self.line("Updating section <info>pyproject.toml</info>.")
                poetry.pyproject.data.item('tool').update(setuptools_scm={})

                poetry.pyproject.file.write(poetry.pyproject.data)
                self.line("Done")

            else:
                self.line("Aborting")
                return 0

    def _get_format_to_use(self, poetry: Poetry):

        format_to_use = self.argument("format")

        if format_to_use == "default":
            option = poetry.pyproject.data.get("tool", {}).get("poetry-setuptools-scm-support", {})
            format_to_use = option.get("default-format", "scm")

        return format_to_use

    def handle(self) -> int:

        poetry = Factory().create_poetry()
        self._prepare(poetry)


        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            format_to_use = self._get_format_to_use(poetry)
            project_configuration = Configuration.from_file(str(poetry.file))

            if format_to_use == "scm":
                v = _do_scm(project_configuration)
            elif format_to_use == "date":
                v = _do_date_and_dirty(project_configuration)
            elif format_to_use == "branch":
                v = _do_semver_branch(project_configuration)
            else:
                self.line_error(f"Unknown format: {format_to_use}")
                return 0

            confirm = self.ask(f'Bumping version "{v}" [Y/n]', 'Y')
            if confirm == "Y":
                poetry.pyproject.data.item('project').update(version=v)
                poetry.pyproject.file.write(poetry.pyproject.data)
                self.line(f"Version changed to {v}")

        return 0

def factory():
    return CalculateVersion()

class ScmPlugin(ApplicationPlugin):
    @property
    def commands(self) -> list[type[Command]]:
        return [CalculateVersion]

    def activate(self, application):
        application.command_loader.register_factory("version-calculate", factory)
