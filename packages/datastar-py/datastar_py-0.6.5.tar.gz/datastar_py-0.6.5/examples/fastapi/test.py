from pathlib import Path

import fastapi_cli.cli
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from datastar_py.fastapi import ReadSignals, datastar_response
from datastar_py.fastapi import ServerSentEventGenerator as SSE

app = FastAPI()
# language=html
HTML = """\
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js"></script>
        </head>
        <body>
            <button id="btn" data-signals="{'foo': 1}" data-on-click="@get('/clear/')" data-on-datastar-fetch='console.log(evt.detail)'>Clear Signal</button>
            <pre data-json-signals></pre>
        </body>
    </html>
"""


@app.get("/")
async def read_root():
    return HTMLResponse(HTML)


@app.get("/clear")
@datastar_response
def clear(signals: ReadSignals):
    print("Clear Signals:", signals)
    # language=html
    yield SSE.patch_elements(
        """<button id="btn" data-on-click="@get('/check')">Check Signal</button>"""
    )
    yield SSE.patch_signals({"foo": None})


@app.get("/check")
@datastar_response
async def check(signals: ReadSignals):
    print("Check Signals:", signals)
    yield SSE.patch_signals({"boo": 2, "foo": None})


if __name__ == "__main__":
    fastapi_cli.cli.run(Path("./test.py"))
