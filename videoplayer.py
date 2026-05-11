from flask import Flask, render_template, send_from_directory, abort, url_for
import os

app = Flask(__name__)

MISC_DIR = os.path.join(app.root_path, "static", "videos")
MOVIE_DIR = os.path.join(app.root_path, "static", "movies")
SHOW_DIR = os.path.join(app.root_path, "static", "shows")

VIDEO_EXTENSIONS = (".mp4", ".mkv")


def list_video_files(folder):
    if not os.path.exists(folder):
        return []
    return sorted(
        [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith(VIDEO_EXTENSIONS)
        ]
    )


def format_title(filename):
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").replace("-", " ").title()


def build_flat_items(files, category):
    return [
        {"filename": f, "title": format_title(f), "category": category} for f in files
    ]


def list_show_names():
    if not os.path.exists(SHOW_DIR):
        return []

    shows = []
    for show_name in sorted(os.listdir(SHOW_DIR)):
        show_path = os.path.join(SHOW_DIR, show_name)
        if os.path.isdir(show_path):
            shows.append({"name": show_name, "slug": show_name})
    return shows


def list_seasons(show_name):
    show_path = os.path.join(SHOW_DIR, show_name)
    if not os.path.exists(show_path) or not os.path.isdir(show_path):
        return []

    seasons = []
    for season_name in sorted(os.listdir(show_path)):
        season_path = os.path.join(show_path, season_name)
        if os.path.isdir(season_path):
            seasons.append({"name": season_name, "show_name": show_name})
    return seasons


def list_episodes(show_name, season_name):
    season_path = os.path.join(SHOW_DIR, show_name, season_name)
    if not os.path.exists(season_path) or not os.path.isdir(season_path):
        return []

    episodes = []
    for episode in sorted(os.listdir(season_path)):
        episode_path = os.path.join(season_path, episode)
        if os.path.isfile(episode_path) and episode.lower().endswith(VIDEO_EXTENSIONS):
            relative_path = os.path.join(show_name, season_name, episode).replace(
                "\\", "/"
            )
            episodes.append(
                {
                    "filename": relative_path,
                    "title": format_title(episode),
                    "show_name": show_name,
                    "season_name": season_name,
                }
            )
    return episodes


@app.route("/")
def index():
    misc_videos = build_flat_items(list_video_files(MISC_DIR), "misc")
    movies = build_flat_items(list_video_files(MOVIE_DIR), "movie")
    shows = list_show_names()

    return render_template(
        "index.html", misc_videos=misc_videos, movies=movies, shows=shows
    )


@app.route("/shows/<show_name>")
def show_detail(show_name):
    seasons = list_seasons(show_name)
    if not seasons:
        abort(404)

    return render_template("show_detail.html", show_name=show_name, seasons=seasons)


@app.route("/shows/<show_name>/<season_name>")
def season_detail(show_name, season_name):
    episodes = list_episodes(show_name, season_name)
    if not episodes:
        abort(404)

    return render_template(
        "season_detail.html",
        show_name=show_name,
        season_name=season_name,
        episodes=episodes,
    )


@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(MISC_DIR, filename)


@app.route("/movies/<filename>")
def serve_movie(filename):
    return send_from_directory(MOVIE_DIR, filename)


@app.route("/show/<path:filename>")
def serve_show(filename):
    return send_from_directory(SHOW_DIR, filename)


@app.route("/watch/<category>/<path:filename>")
def watch(category, filename):
    if category == "movie":
        video_url = url_for("serve_movie", filename=filename)
        label = "Movie"
        title = format_title(filename)
    elif category == "show":
        video_url = url_for("serve_show", filename=filename)
        label = "TV Show"
        title = format_title(os.path.basename(filename))
    elif category == "misc":
        video_url = url_for("serve_video", filename=filename)
        label = "Misc Video"
        title = format_title(filename)
    else:
        abort(404)

    return render_template(
        "watch.html", title=title, filename=filename, video_url=video_url, label=label
    )


if __name__ == "__main__":
    app.run(debug=True)
