---
title: Checker
description: All functions and usage of the checker extension.
---

# Checker

Checker for checking that values provided are valid lavalink URL's, and what types they are.

## Check

Calling this will evaluate if the value provided is a valid Lavalink supported URL.

```py
from ongaku.ext import checker

checker.check("test")
```

The value returned is either `None` or a `checker.Sites`.

If the value is None, it means it is an unsupported lavalink URL.

This can mean one of three things.

- Its not a link, and just a text value.
- Its a link, but unsupported by lavalink.
- Its a link, but its unsupported by the first party lavalink URL's.

In the last two cases, the value can still be a link, but is not detected by the regex's of lavalink.
