from helpers import login, bearerhdr
from werkzeug.datastructures import FileStorage
from models import Sound
import pytest

"""
controllers/api/tracks.py
"""

"""
# TODO
GET /api/tracks/<username_or_id>/<soundslug>

DELETE /api/tracks/<username>/<soundslug>

PATCH /api/tracks/<username>/<soundslug>
w/ tags +/- etc., clearing title, etc.

GET /api/tracks/<username_or_id>/<soundslug>

POST /api/tracks/<username_or_id>/<soundslug>/retry_processing

PATCH /api/tracks/<username>/<soundslug>/artwork

create album; upload track with album; fetch

create album; upload track; fetch; edit add in album; fetch
"""


def test_track_upload(client, session, audio_file_mp3, mocker):
    """
    POST /api/tracks
    """
    m = mocker.patch("tasks.upload_workflow.delay")
    audio_file_mp3.seek(0)

    # Login as user A
    client_id, client_secret, access_token = login(client, "testusera", "testusera")

    datas = {
        "title": "test track upload",
        "licence": 0,  # unspecified, see api/utils/defaults.py
        "description": "test track upload",
        "file": FileStorage(stream=audio_file_mp3, filename="cat.mp3"),
    }
    # Upload track
    resp = client.post("/api/tracks", data=datas, headers=bearerhdr(access_token), content_type="multipart/form-data")
    assert resp.status_code == 200, resp.data
    assert len(resp.json["id"]) == 36
    assert len(resp.json["slug"]) >= 5
    # Save for later
    track_infos = resp.json

    # Get track informations
    resp = client.get(f"/api/tracks/testusera/{resp.json['slug']}", headers=bearerhdr(access_token))
    assert resp.status_code == 200, resp.data
    assert resp.json["account"]["acct"] == "testusera"
    assert isinstance(resp.json["reel2bits"], dict)
    assert resp.json["reel2bits"]["title"] == datas["title"]
    assert resp.json["reel2bits"]["metadatas"]["licence"]["id"] == datas["licence"]
    assert resp.json["content"] == datas["description"]
    assert resp.json["reel2bits"]["private"] is False
    assert resp.json["reel2bits"]["processing"]["transcode_needed"] is False
    assert resp.json["reel2bits"]["processing"]["done"] is False  # the celery workflow isn't ran
    assert len(resp.json["reel2bits"]["media_orig"]) >= 10
    assert len(resp.json["reel2bits"]["media_transcoded"]) >= 10

    # Fetch from database
    sound = Sound.query.filter(Sound.flake_id == track_infos["id"]).one()
    assert sound is not None

    # Assert the celery remoulade
    m.assert_called_once_with(sound.id)


@pytest.mark.parametrize(
    ("title", "description", "tags", "licence"),
    (
        ("testinvalidcombos1", "testinvalidcombos1", "tag1, tag2", 0),
        ("testinvalidcombos2", "", "tag1, tag2", 0),
        ("testinvalidcombos3", "testinvalidcombos3", "", 0),
        ("", "", "", None),
    ),
)
def test_track_upload_invalid_combos(client, session, audio_file_mp3, mocker, title, description, tags, licence):
    """
    POST /api/tracks
    """
    m = mocker.patch("tasks.upload_workflow.delay")
    audio_file_mp3.seek(0)

    # Login as user A
    client_id, client_secret, access_token = login(client, "testusera", "testusera")

    datas = {
        "title": title,
        "description": description,
        "file": FileStorage(stream=audio_file_mp3, filename="cat.mp3"),
    }
    if licence:
        datas["licence"] = licence

    # Upload track
    resp = client.post("/api/tracks", data=datas, headers=bearerhdr(access_token), content_type="multipart/form-data")
    if not licence:
        assert resp.status_code == 400, resp.data
        assert "error" in resp.json
        assert "licence" in resp.json["error"]
    else:
        assert resp.status_code == 200, resp.data
        assert len(resp.json["id"]) == 36
        assert len(resp.json["slug"]) >= 5

    if licence:
        # Save for later
        track_infos = resp.json

        # Get track informations
        resp = client.get(f"/api/tracks/testusera/{resp.json['slug']}", headers=bearerhdr(access_token))
        assert resp.status_code == 200, resp.data
        assert resp.json["account"]["acct"] == "testusera"
        assert isinstance(resp.json["reel2bits"], dict)
        assert resp.json["reel2bits"]["metadatas"]["licence"]["id"] == licence
        assert resp.json["content"] == description
        assert resp.json["reel2bits"]["private"] is False
        assert resp.json["reel2bits"]["processing"]["transcode_needed"] is False
        assert resp.json["reel2bits"]["processing"]["done"] is False  # the celery workflow isn't ran
        assert len(resp.json["reel2bits"]["media_orig"]) >= 10
        assert len(resp.json["reel2bits"]["media_transcoded"]) >= 10
        if title == "":
            assert resp.json["reel2bits"]["title"] == "cat.mp3"
        else:
            assert resp.json["reel2bits"]["title"] == title

        # Fetch from database
        sound = Sound.query.filter(Sound.flake_id == track_infos["id"]).one()
        assert sound is not None

        # Assert the celery remoulade
        m.assert_called_once_with(sound.id)


@pytest.mark.parametrize(
    ("tags", "tags_count"), (("", 0), ("tag1, tag2", 2), ("tag1", 1), ("tag1 tag2", 1),),
)
def test_track_upload_with_tags(client, session, audio_file_mp3, mocker, tags, tags_count):
    """
    POST /api/tracks
    """
    m = mocker.patch("tasks.upload_workflow.delay")
    audio_file_mp3.seek(0)

    # Login as user A
    client_id, client_secret, access_token = login(client, "testusera", "testusera")

    datas = {
        "title": "testtracktags",
        "description": "testtracktags",
        "file": FileStorage(stream=audio_file_mp3, filename="cat.mp3"),
        "licence": 0,
        "tags": tags,
    }

    # Upload track
    resp = client.post("/api/tracks", data=datas, headers=bearerhdr(access_token), content_type="multipart/form-data")
    assert resp.status_code == 200, resp.data
    assert len(resp.json["id"]) == 36
    assert len(resp.json["slug"]) >= 5

    # Save for later
    track_infos = resp.json

    # Get track informations
    resp = client.get(f"/api/tracks/testusera/{resp.json['slug']}", headers=bearerhdr(access_token))
    assert resp.status_code == 200, resp.data
    assert resp.json["account"]["acct"] == "testusera"
    assert isinstance(resp.json["reel2bits"], dict)
    assert resp.json["reel2bits"]["metadatas"]["licence"]["id"] == datas["licence"]
    assert resp.json["content"] == datas["description"]
    assert resp.json["reel2bits"]["private"] is False
    assert resp.json["reel2bits"]["processing"]["transcode_needed"] is False
    assert resp.json["reel2bits"]["processing"]["done"] is False  # the celery workflow isn't ran
    assert len(resp.json["reel2bits"]["media_orig"]) >= 10
    assert len(resp.json["reel2bits"]["media_transcoded"]) >= 10
    assert resp.json["reel2bits"]["title"] == datas["title"]
    assert len(resp.json["reel2bits"]["tags"]) == tags_count
    if tags_count > 0:
        for i in tags.split(","):
            assert i.strip() in resp.json["reel2bits"]["tags"]

    # Fetch from database
    sound = Sound.query.filter(Sound.flake_id == track_infos["id"]).one()
    assert sound is not None

    # Assert the celery remoulade
    m.assert_called_once_with(sound.id)