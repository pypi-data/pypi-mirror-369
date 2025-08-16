"""Minimal HTML/JS viewer for ``HLSFState`` snapshots.

The viewer connects to the ``/state/stream`` endpoint exposed by
``server.py`` and renders geometry and gating scores using Plotly.  It is
served by including :data:`router` in a FastAPI application::

    from hlsf_module.web_viewer import router
    app.include_router(router)

The static assets are entirely self contained in this module to keep the
example light‑weight.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Client page served at ``/viewer``.  It uses Plotly via a CDN and listens to
# the server-sent event stream at ``/state/stream``.

_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>HLSF Web Viewer</title>
  <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
</head>
<body>
  <select id=\"mod\" style=\"position:absolute;top:5px;left:5px;z-index:10;\"></select>
  <div id=\"geom\" style=\"width:50%;display:inline-block;\"></div>
  <div id=\"gate\" style=\"width:45%;display:inline-block;\"></div>
<script>
  const es = new EventSource('/state/stream');
  const sel = document.getElementById('mod');
  let current = null;
  es.onmessage = function(evt) {
    const payload = JSON.parse(evt.data);
    const geom = payload.state || {};
    const tris = geom.triangles || [];
    const cols = geom.colors || [];
    const traces = [];
    for (let i = 0; i < tris.length; i++) {
      const tri = tris[i];
      const col = cols[i] || [0,0,0,0.5];
      const xs = [tri[0][0], tri[1][0], tri[2][0], tri[0][0]];
      const ys = [tri[0][1], tri[1][1], tri[2][1], tri[0][1]];
      const rgba = 'rgba(' + Math.round(col[0]*255) + ',' + Math.round(col[1]*255) + ',' + Math.round(col[2]*255) + ',' + col[3] + ')';
      traces.push({x:xs, y:ys, type:'scatter', mode:'lines', fill:'toself', fillcolor:rgba, line:{color:'black'}});
    }
    Plotly.react('geom', traces, {xaxis:{scaleanchor:'y'}, yaxis:{}, showlegend:false});
    const allScores = payload.scores || (payload.gating ? payload.gating.scores : {}) || {};
    const mods = Object.keys(allScores);
    sel.innerHTML = '';
    mods.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m; opt.textContent = m;
      if (m === current) opt.selected = true;
      sel.appendChild(opt);
    });
    if (!current || !mods.includes(current)) current = mods[0] || null;
    const scores = current ? allScores[current] || {} : {};
    const xs2 = Object.keys(scores);
    const ys2 = xs2.map(k => scores[k]);
    Plotly.react('gate', [{x: xs2, y: ys2, type:'bar'}], {yaxis:{title:'Gating score'}});
  };
  sel.onchange = () => { current = sel.value; };
</script>
</body>
</html>"""

@router.get("/viewer", response_class=HTMLResponse)
async def viewer() -> str:
    """Return the HTML page for the live web viewer."""
    return _HTML
