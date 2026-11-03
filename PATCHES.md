# Changes from upstream

This is the Asciiverse packaging of FroxComposband 7.3.2 by Gliktch
(github.com/Gliktch/froxcomposband), the maintained fork of
FrogComposband, itself grown from PosChengband, Hengband and Zangband.
`main` is upstream's `v7.3.2` tag, with upstream's history; the
`upstream` remote points there.

We ship the terminal (curses) version only.

## The game

Unchanged. No file under `src/` or `lib/` differs from `v7.3.2`. The
version line says "(Development)" because the tag sets
`VERSION_IS_DEVELOPMENT`, as in upstream's own release builds.

## Build settings

`asciiverse/build.sh` configures `--with-no-install` (data read from
`./lib`) and adds `-DUSE_PRIVATE_PATHS -DPRIVATE_USER_PATH="/var/tmp"`,
the two defines `--with-private-dirs` would add (configure accepts only
one of the two options). So the game reads its data next to it and keeps
saves, scores, bones and its data cache in
`${XDG_DATA_HOME:-~/.local/share}/FroxComposband`, upstream's own
per-user folder. Then, as upstream's release does, a first run generates
the class, race and monster help pages (`scripts/release/generate-help.sh`).
That run happens once, in the x86_64 Linux build; the macOS builds take
its pages (`HELP_FROM`, `scripts/release/apply-generated-help.sh`), as
upstream's release workflow does. The helper script runs the game under
`timeout`, which macOS runners lack, so a run there made no pages.

## Packaging

- `asciiverse/froxcomposband` (new): the start script, for the av archive
  and the system packages; runs the game from the folder that holds `lib/`.
- `asciiverse/build.sh`, `asciiverse/stage.sh`, `asciiverse/nfpm.yaml`
  (new): static Linux build in Alpine, native macOS builds, the av
  archive, and .deb/.rpm/.apk/Arch packages.
- `asciiverse/macos-ncursesw-config` (new): stands in for the
  `ncursesw6-config` script that configure looks for and macOS lacks.
- `asciiverse/COPYING` (new): the repository has no licence file; this
  quotes the Moria/Angband notice its sources carry.
- `asciiverse/record-preview.py` (new): records the catalog preview.
- `.github/workflows/release.yml` (new): builds all of it on a tag.
- `.github/workflows/release-builds.yml` (removed): upstream's release
  job fires on every `v*` tag, so on our `v7.3.2-av.1` it would have built
  and published its own Windows, macOS and Linux files into our release.
- `.gitignore`: `stage/`.

## Not changed

- No graphical front ends (X11, SDL, Cocoa) and no Windows build.
- Licence: the Moria/Angband notice, free to share but not for profit,
  hence `LicenseRef-Free-Noncommercial`.
