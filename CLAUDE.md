# FroxComposband (Asciiverse packaging)

FroxComposband 7.3.2 by Gliktch, the maintained fork of FrogComposband
(an Angband variant by way of Zangband, Hengband and PosChengband), its
terminal version, packaged for the Asciiverse catalog and as system
packages. Upstream is active (github.com/Gliktch/froxcomposband, remote
`upstream`): don't change the game; list anything we change in PATCHES.md.

- Chosen over FrogComposband itself (sulkasormi/frogcomposband, quiet since
  2023): Frox carries Frog on with fixes and loads its saves.
- `origin` is to be github.com/theasciiverse/froxcomposband.
- Release: tag `v<upstream version>-av.<n>` (first: `v7.3.2-av.1`) and push
  it. For a new upstream release, merge its tag into `main`.
- Local build: `sh asciiverse/build.sh` (needs libncurses-dev) leaves
  `src/froxcomposband` and generated help in `lib/help`. Static build:
  `docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh`.
- Data in `lib/` next to the binary (`asciiverse/froxcomposband` runs it
  from there); saves in ~/.local/share/FroxComposband.
- Licence is the Moria/Angband non-commercial notice (asciiverse/COPYING).
- Preview: `sh asciiverse/stage.sh && python3 asciiverse/record-preview.py`
  (needs pyte; it runs the staged game). Levels are random: keep a take
  with a fight.
