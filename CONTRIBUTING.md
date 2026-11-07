# Contributing

Use Python 3.11–3.13 and run uv sync. Propose a focused change with its Maplewood
scenario, observed behavior, protocol reference and validation.

1. Run pytest, Ruff, validate_gym and the example runner.
2. Capture changed traffic with scripts/wiretap.py; redact credentials.
3. Check protobuf and the pinned SDK instead of copying older tutorials.
4. Keep tasks deterministic, offline and small. Starters fail; solutions pass.
   Design quality requires human review.
5. Clear notebook outputs. Keep credentials and learner work out of commits.

Generated content comes from common/course_catalog.json, gym/exercise_specs.json
and scripts/build_course.py. Modify authoring sources before regenerating.
Review the diff; do not overwrite learner work.

Report security concerns privately through GitHub security reporting if enabled,
or through a maintainer's published contact route.
