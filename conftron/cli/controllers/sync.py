import typer

from conftron.cli.context import Context
from conftron.cli.enums.sync import SyncCheckAction
from conftron.cli.utils.echo_shortcuts import get_binary_styled_word, get_metadata_message
from conftron.cli.utils.synchronizator import get_synchronizator
from conftron.config.config_manager import ConfigManager
from conftron.sync.utils.metadata_manager import MetadataManager

__all__ = ("app",)

app = typer.Typer()


@app.callback()
def main(
    ctx: Context,
    healthcheck: bool = typer.Option(False, "--healthcheck", "-H", is_flag=True),
):
    ctx.obj.synchronizator = get_synchronizator(
        healthcheck=healthcheck,
        config=ctx.obj.config,  # type: ignore
        metadata_path=ctx.obj.metadata_path,
    )

    ctx.obj.config.set_config_obj(ctx.obj.synchronizator.__class__)


@app.command()
def check(
    ctx: Context,
):
    status = ctx.obj.synchronizator.is_healthy()

    status_word = get_binary_styled_word(status)

    metadata_status_message: list[str] = []

    for sync_action in SyncCheckAction.keys():
        metadata_status = ctx.obj.synchronizator.validate_metadata(action=sync_action)

        metadata_status_word = get_binary_styled_word(metadata_status)

        metadata_status_message.append(f"  => {sync_action}: {metadata_status_word}")

    metadata_actions_status = "\n".join(metadata_status_message)

    targets_status_message: list[str] = []

    for target in ctx.obj.synchronizator.targets:
        target_local_status = target.check_local_availability()

        target_local_status_word = get_binary_styled_word(target_local_status)

        target_remote_status = ctx.obj.synchronizator.check_target_available(target)

        target_remote_status_word = get_binary_styled_word(target_remote_status)

        targets_status_message.append(
            f"  => {target.get_target_name()}:\n"
            f"       local_status: {target_local_status_word}\n"
            f"       remote_status: {target_remote_status_word}\n"
            f"       path: {target.path}\n"
            f"       content_type: {target.content_type}"
        )

    targets_status = "\n".join(targets_status_message)

    local_metadata = (
        get_metadata_message(ctx.obj.synchronizator.local_metadata, line_before="       ")
        if ctx.obj.synchronizator.local_metadata
        else None
    )
    remote_metadata = (
        get_metadata_message(ctx.obj.synchronizator.remote_metadata, line_before="       ")
        if ctx.obj.synchronizator.remote_metadata
        else None
    )

    with ctx.obj.spinner.hidden():
        typer.echo(
            "Synchronization provider:"
            f" {ctx.obj.config.obj.sync.provider} ({str(ctx.obj.synchronizator.__class__.__name__)})\nStatus:"
            f" {status_word}\nMetadata: {metadata_status_word}\n  => local:\n"
            f" {local_metadata}\n"
            "  =>"
            f" remote:\n{remote_metadata}\nMetadata"
            f" valid for synchronization actions:\n{metadata_actions_status}\nTargets:\n{targets_status}"
        )


@app.command()
def upload(ctx: Context):
    upload_status = False
    targets_status = {}

    status = ctx.obj.synchronizator.upload()
    upload_status = status["possibility_upload_status"]
    targets_status = status["targets_status"]

    status_word = get_binary_styled_word(upload_status)

    targets_status_message: list[str] = []

    if upload_status and targets_status:
        for target_name, target_status in targets_status.items():
            target_status_word = get_binary_styled_word(target_status)

            targets_status_message.append(f"  {target_name}: {target_status_word}")

    targets_sections = ""

    if upload_status:
        targets_sections = "\n".join(["Targets:", *targets_status_message])

    with ctx.obj.spinner.hidden():
        typer.echo(
            "Current"
            f" metadata:\n{get_metadata_message(MetadataManager.read(ctx.obj.metadata_path), line_before='  ')}\nUpload"
            f" status: {status_word}\n{targets_sections}"
        )


@app.command()
def download(ctx: Context):
    download_status = False
    targets_status = {}

    status = ctx.obj.synchronizator.download()
    download_status = status["possibility_download_status"]
    targets_status = status["targets_status"]

    status_word = get_binary_styled_word(download_status)

    targets_status_message: list[str] = []

    if download_status and targets_status:
        for target_name, target_status in targets_status.items():
            target_status_word = get_binary_styled_word(target_status)

            targets_status_message.append(f"  {target_name}: {target_status_word}")

    targets_sections = ""

    if download_status:
        targets_sections = "\n".join(["Targets:", *targets_status_message])

        config_data = ConfigManager.prepare_config_data(ctx.obj.config.get_validated(ctx.obj.synchronizator.__class__))
        config_data["sync"]["targets"] = status["targets_config"]

        ConfigManager.write(config_path=str(ctx.obj.config_path), config_data=config_data)

    with ctx.obj.spinner.hidden():
        typer.echo(
            "Current"
            f" metadata:\n{get_metadata_message(MetadataManager.read(ctx.obj.metadata_path), line_before='  ')}\nDownload"
            f" status: {status_word}\n{targets_sections}"
        )
