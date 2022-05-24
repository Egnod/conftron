from art import art, decor
from click import ClickException, Context
from typer.core import TyperGroup

from conftron.exceptions import AppException


class Command(TyperGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        try:
            return super().invoke(*args, **kwargs)
        except KeyboardInterrupt:
            ctx = next(iter(args), None)

            if isinstance(ctx, Context) and ctx.obj:
                with ctx.obj.spinner.hidden():
                    print(f"Bye! {art('hug me')}")
        except (ClickException, EOFError) as e:
            raise e
        except Exception as e:
            raise AppException(f"{decor('depressed')}\nUnexcepted error description: {repr(e)}") from e
