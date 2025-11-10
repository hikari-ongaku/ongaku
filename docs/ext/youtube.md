---
title: Youtube
description: All functions and usage of the youtube extension.
---

# Youtube

Allows for control of the YouTube plugin and its endpoints.

## Fetch YouTube

Fetch the current YouTube information.

```py
from ongaku.ext import youtube

youtube_information = youtube.fetch_youtube(session)
```

!!! warning
    The session value is required[^1].

## Fetch YouTube OAuth

Fetch the current YouTube OAuth information.

```py
from ongaku.ext import youtube

youtube_oauth_information = youtube.fetch_youtube_oauth(session)
```

!!! warning
    The session value is required[^1].

## Update Youtube

Update the current YouTube information.

```py
from ongaku.ext import youtube

youtube.update_youtube(
    session,
    refresh_token="refresh_token",
    skip_initialization=False,
    po_token="po_token",
    visitor_data="visitor_data",
)
```

!!! warning
    The session value is required[^1].

!!! note
    All arguments except the `session` values are optional.

    However, at least one value is required to be set, otherwise an error will be returned.


[^1]:
    It can be received by the client via calling the following:

    ```py
    client.handler.get_session()
    ```
