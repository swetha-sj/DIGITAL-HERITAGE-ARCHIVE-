"""
Digital Heritage Archive - Audio/Video & Oral History Archive
Delegates to the full Audio-Visual Archive implementation in views.audiovisual.
"""

from views.audiovisual import render_audiovisual


def render_av_oral_history():
    render_audiovisual()


if __name__ == "__main__":
    render_audiovisual()
