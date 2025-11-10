---
title: Filters
description: Usage and setup of filters.
---

# Filters

Below will show you how to control the filter object, both making a new one, or modifying an existing one.

Setting a players filter can be found [here](./player.md#filters).

## Getting a filter.

There is two methods to get a filter.

You can create a new one, or you can use a pre-existing one (from a player.)

=== "New"

    Creating a new filter.

    ```py
    filters = ongaku.Filters()
    ```

=== "From Player"

    Creating a filter from a pre-existing one.

    ```py
    filters = ongaku.Filters.from_filter(player.filters)
    ```

!!! tip
    If you create a new one, then it will override pre-existing settings on the player.
    If you don't want it to do that, use the `from_filter` method shown above!

## Functions

There is quite a few filters, and almost all have these two methods.

 * `set_xxxx` - This allows you to set new values to the filter.
 * `clear_xxxx` - This will completely clear the values from that filter.

!!! warning
    clear != reset. Clearing sets the value to `None` which **will** override existing values.


### Volume

Setting the volume of the filter settings.

```py
filters.set_volume(200)
```

### Equalizer

Add, remove and clear equalizer filter settings.

![](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#equalizer)

=== "Add"

    Add a new equalizer band

    ```py
    filters.add_equalizer(BandType.HZ100, 0.3)
    ```

=== "Remove"

    Remove a new equalizer band

    ```py
    filters.remove_equalizer(BandType.HZ100)
    ```

=== "Clear"

    Remove all equalizer bands previously set.

    ```py
    filters.clear_equalizer()
    ```

!!! note
    You can use any [BandType][ongaku.filters.BandType] you would like, `BandType.HZ100` is just an example.

### Karaoke

Set or remove karaoke filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#karaoke)

=== "Set"

    Set karaoke values.

    ```py
    filters.set_karaoke(
        level=1,
        mono_level=0,
        filter_band=0.5,
        filter_width=None
    )
    ```
=== "Clear"

    Clear karaoke values.

    ```py
    filters.clear_karaoke()
    ```

### Timescale

Set or remove timescale filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#timescale)

=== "Set"

    Set timescale values.

    ```py
    filters.set_timescale(
        speed=10,
        pitch=1.5,
        rate=None
    )
    ```
=== "Clear"

    Clear timescale values.

    ```py
    filters.clear_timescale()
    ```

### Tremolo

Set or remove tremolo filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#tremolo)

=== "Set"

    Set tremolo values.

    ```py
    filters.set_tremolo(
        frequency=2,
        depth=1
    )
    ```
=== "Clear"

    Clear tremolo values.

    ```py
    filters.clear_tremolo()
    ```

### Vibrato

Set or remove vibrato filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#vibrato)

=== "Set"

    Set vibrato values.

    ```py
    filters.set_vibrato(
        frequency=2,
        depth=1
    )
    ```
=== "Clear"

    Clear vibrato values.

    ```py
    filters.clear_vibrato()
    ```

### Rotation

Set or remove rotation filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#rotation)

=== "Set"

    Set rotation values.

    ```py
    filters.set_rotation(
        rotation_hz=8
    )
    ```

=== "Clear"

    Clear rotation values.

    ```py
    filters.clear_rotation()
    ```

### Distortion

Set or remove distortion filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#distortion)

=== "Set"

    Set distortion values.

    ```py
    filters.set_distortion(
        sin_offset=0.3,
        sin_scale=1,
        cos_offset=4,
        cos_scale=-3,
        tan_offset=4,
        tan_scale=9,
        offset=6.66,
        scale=-1.5,
    )
    ```

=== "Clear"

    Clear distortion values.

    ```py
    filters.clear_distortion()
    ```

### Channel Mix

Set or remove channel mix filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#channel-mix)

=== "Set"

    Set channel mix values.

    ```py
    filters.set_channel_mix(
        left_to_left=0.39,
        left_to_right=1,
        right_to_left=0,
        right_to_right=0.8
    )
    ```

=== "Clear"

    Clear channel mix values.

    ```py
    filters.clear_channel_mix()
    ```

### Low Pass

Set or remove low pass filter settings.

![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Learn More](https://lavalink.dev/api/rest.html#low-pass)

=== "Set"

    Set low pass values.

    ```py
    filters.set_low_pass(
        left_to_left=0.39,
        left_to_right=1,
        right_to_left=0,
        right_to_right=0.8
    )
    ```

=== "Clear"

    Clear low pass values.

    ```py
    filters.clear_low_pass()
    ```

!!! tip
    All values except for the volume, can be one of three values

    * `Float` - The number you wish to set.
    * `None` - Clears that specific value in the filter.
    * `Unset` (DEFAULT) - Leaves it at its current value (only if set prior, otherwise it will be `None`)
