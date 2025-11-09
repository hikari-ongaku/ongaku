---
title: Sessions
description: Using, switching and creating session handlers
---

# sessions

## Adding a session

Adding a session for the ongaku client to connect, and play music through.

```py
client.create_session(
    ssl=False,
    host="127.0.0.1",
    port=2333,
    password="youshallnotpass"
)
```

!!! tip
    You can have more than one session connected to a singular client!

    This will give your bot more sessions to fallback on, if one fails.

!!! warning
    On another note, you must have at least one session added to the client,
    otherwise nothing within the client will work, like playing music.


## Changing The default Session Handler

The way you change your session handler, is when you create your client.

```py
client = ongaku.Client(
    bot,
    handler=ongaku.BasicHandler
)
```

!!! note
    There is no need to specify a session handler by default.
    You only need to set one, if you wish to use a different session handler.

    Changing the session handler can be useful for multiple different reasons.
    You may want load balancing, or you may want regional server selection.

## Session Handlers

Below is all the available session handlers.

### BasicHandler

The basic session handler simply just fetches (and stores) the current session.

It will only give a different session, if the current session closes, or errors out.

!!! note
    This session handler is the default session handler if no **other** session handler is set.
