import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#ffffff">
<meta name="description" content="Smart Search Engine">
<title>{{ q if q else 'SMART SEARCH ENGINE' }}</title>

<style>
*{box-sizing:border-box}
body{
    margin:0;background:#fff;color:#202124;
    font:14px Arial,sans-serif
}
header{
    padding:20px 6%;display:flex;
    justify-content:space-between;align-items:center;
    border-bottom:1px solid #eee
}
.logo{font-size:19px;font-weight:bold;color:#4285f4}
.status{font-size:12px;color:#188038}
main{width:min(720px,92%);margin:35px auto}
.searchbox{
    display:flex;align-items:center;gap:10px;
    border:1px solid #dfe1e5;border-radius:28px;
    padding:5px 8px 5px 18px;
    box-shadow:0 1px 5px #00000010
}
.searchbox:hover{box-shadow:0 2px 8px #00000020}
input{
    flex:1;min-width:0;border:0;outline:0;
    font-size:16px;padding:12px 0;color:#202124;
    background:transparent
}
button{
    background:#4285f4;color:#fff;border:0;
    border-radius:22px;padding:12px 19px;
    font-size:14px;cursor:pointer
}
button:hover{background:#3367d6}
.tabs{
    display:flex;gap:25px;overflow-x:auto;
    border-bottom:1px solid #ebebeb;
    margin-top:24px;white-space:nowrap
}
.tabs a{
    color:#5f6368;text-decoration:none;
    padding:13px 2px;border-bottom:3px solid transparent
}
.tabs a.active{color:#1a73e8;border-color:#1a73e8}
.count{color:#70757a;font-size:12px;margin:20px 0}
.result{margin:0 0 27px;overflow-wrap:anywhere}
.result a.title{
    color:#1a0dab;text-decoration:none;
    font-size:19px;line-height:1.4
}
.result a.title:hover{text-decoration:underline}
.url{color:#188038;font-size:13px;margin:5px 0 7px}
.result p{
    color:#4d5156;font-size:14px;
    line-height:1.55;margin:0
}
.result img{
    max-width:100%;max-height:230px;
    object-fit:contain;border-radius:8px;
    margin:0 0 10px;background:#f8f9fa
}
.imagegrid{
    display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;margin-top:20px
}
.imagecard{
    border:1px solid #eee;border-radius:10px;
    padding:10px;min-width:0;overflow-wrap:anywhere
}
.imagecard img{
    width:100%;height:160px;object-fit:contain;
    border-radius:7px;background:#f8f9fa
}
.imagecard a{color:#1a0dab;text-decoration:none}
.imagecard p{color:#5f6368;font-size:12px}
.empty{
    padding:20px 0;color:#5f6368;line-height:1.6
}
footer{
    color:#70757a;text-align:center;
    font-size:12px;padding:30px 10px
}
@media(max-width:520px){
    header{padding:17px 5%}
    .logo{font-size:15px}
    main{margin:25px auto}
    .searchbox{padding-left:13px;gap:6px}
    input{font-size:15px}
    button{padding:11px 13px}
    .tabs{gap:20px}
    .result a.title{font-size:18px}
    .imagegrid{gap:9px}
    .imagecard{padding:7px}
    .imagecard img{height:125px}
}
</style>
</head>
<body>
<header>
    <div class="logo"><img src="{{ url_for('static', filename='logo.png') }}" alt="SearchEngineSmart" style="width:64px;height:64px;object-fit:contain;vertical-align:middle;"></div>
    <div class="status">● READY</div>
</header>

<main>
    <form class="searchbox" action="/" method="get">
        <input type="search" name="q"
               placeholder="Search anything..."
               value="{{ q }}" required>
        <input type="hidden" name="category" value="{{ category }}">
        <button type="submit">Search</button>
    </form>

    <nav class="tabs">
        {% for key, label in [
            ('general','Web'),('images','Images'),
            ('news','News'),('videos','Videos')
        ] %}
        <a href="/?q={{ q|urlencode }}&category={{ key }}"
           class="{% if category == key %}active{% endif %}">
            {{ label }}
        </a>
        {% endfor %}
    </nav>

    {% if q %}
        <div class="count">Search results for <b>{{ q }}</b></div>
    {% else %}
        <div class="empty">
            Search the web for information, images, news, and videos.
        </div>
    {% endif %}

    {% if error %}
        <div class="empty">{{ error }}</div>
    {% endif %}

    {% if category == 'images' and results %}
    <div class="imagegrid">
        {% for r in results %}
        <div class="imagecard">
            {% if r.get('img_src') or r.get('thumbnail') %}
            <a href="{{ r.get('url', '#') }}"
               target="_blank" rel="noopener noreferrer">
                <img src="{{ r.get('img_src') or r.get('thumbnail') }}" onerror="this.style.display='none'"
                     alt="{{ r.get('title', 'Image') }}"
                     loading="lazy">
            </a>
            {% endif %}
            <a href="{{ r.get('url', '#') }}"
               target="_blank" rel="noopener noreferrer">
                {{ r.get('title', 'View result') }}
            </a>
        </div>
        {% endfor %}
    </div>
    {% else %}
        {% for r in results %}
        <article class="result">
            {% if category == 'videos' and r.get('thumbnail') %}
            <a href="{{ r.get('url', '#') }}"
               target="_blank" rel="noopener noreferrer">
                <img src="{{ r.get('thumbnail') }}" onerror="this.style.display='none'"
                     alt="{{ r.get('title', 'Video') }}"
                     loading="lazy">
            </a>
            {% endif %}

            <a class="title"
               href="{{ r.get('url', '#') }}"
               target="_blank" rel="noopener noreferrer">
                {{ r.get('title', 'Untitled result') }}
            </a>

            <div class="url">{{ r.get('url', '') }}</div>

            {% if r.get('content') %}
            <p>{{ r.get('content') }}</p>
            {% endif %}
        </article>
        {% endfor %}
    {% endif %}

    {% if q and not results and not error %}
        <div class="empty">
            No results found. Try a different search.
        </div>
    {% endif %}
</main>

<footer>SMART SEARCH ENGINE · Search smarter. Find more.</footer>
</body>
</html>
"""


@app.route("/")
def home():
    q = request.args.get("q", "").strip()[:200]
    category = request.args.get("category", "general")

    if category not in ("general", "images", "news", "videos"):
        category = "general"

    results = []
    error = ""

    if q:
        try:
            api_key = os.environ.get("ENDLESS_API_KEY", "")

            if not api_key:
                error = "API key belum tersedia. Masukkan API key di Termux."
            else:
                response = requests.get(
                    "https://api.endless.sbs/search",
                    params={
                        "q": q,
                        "format": "json",
                        "categories": category
                    },
                    headers={
                        "X-API-Key": api_key,
                        "User-Agent": "SmartSearchEngine/1.0"
                    },
                    timeout=20
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])[:10]

        except Exception:
            error = "Search unavailable. Check your connection, API key, or quota."

    return render_template_string(
        HTML, q=q, results=results,
        error=error, category=category
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
