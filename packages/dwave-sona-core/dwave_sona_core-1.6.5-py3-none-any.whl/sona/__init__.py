import typer
from sona.core.commands import app as inferencer_app
from sona.sidecar.commands import app as sidecar_app
from sona.web.commands import app as web_app
from sona.worker.commands import app as worker_app

app = typer.Typer()
app.add_typer(inferencer_app, name="inferencer")
app.add_typer(worker_app, name="worker")
app.add_typer(web_app, name="web")
app.add_typer(sidecar_app, name="sidecar")
