<!--
SPDX-FileCopyrightText: 2024 Helge

SPDX-License-Identifier: MIT
-->

# Changes

## 0.2.15

- Include release_helper in CI [pasture#23](https://codeberg.org/funfedidev/python_fediverse_pasture/issues/23)
- Add doctest to `ActivitySender.init_note` [pasture#16](https://codeberg.org/funfedidev/python_fediverse_pasture/issues/16)
- Make logged error in `entry.apply_to` contain a stacktrace [pasture#18](https://codeberg.org/funfedidev/python_fediverse_pasture/issues/18)
- Make ids more explicit [pasture#21](https://codeberg.org/funfedidev/python_fediverse_pasture/issues/21)

## fediverse_pasture 0.2.14

- Add ability to supply nodeinfo in one_actor with `--with_nodeinfo` flag. See [Issue 152](https://codeberg.org/helge/funfedidev/issues/152)

## fediverse_pasture 0.2.11

- Make `python -mfediverse_pasture verify APPLICATION` to check an application

## fediverse_pasture 0.2.10

- Repair misskey

## fediverse_pasture 0.2.9

- Use object_id instead of published in `fetch_activity`
- Multiple tries for `fetch_activity`

## fediverse_pasture 0.2.8

- Improve tooling to create applications

## fediverse_pasture 0.2.7

- Repair link in README.md

## fediverse_pasture 0.2.5

- Fix missing timeout parameter to build_app

## fediverse_pasture 0.2.4

- Add timeout parameter to verify_actor
- Enable choosing which actors to run verify_actor with
