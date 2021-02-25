# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
from synthtool import gcp
from synthtool.languages import python

gapic = gcp.GAPICBazel()
common = gcp.CommonTemplates()
version = "v2"

library = gapic.py_library(
    service="bigquery",
    version=version,
    bazel_target=f"//google/cloud/bigquery/{version}:bigquery-{version}-py",
    include_protos=True,
)

s.move(
    library,
    excludes=[
        "*.tar.gz",
        "docs/index.rst",
        "docs/bigquery_v2/*_service.rst",
        "docs/bigquery_v2/services.rst",
        "README.rst",
        "noxfile.py",
        "setup.py",
        "scripts/fixup_bigquery_v2_keywords.py",
        library / f"google/cloud/bigquery/__init__.py",
        library / f"google/cloud/bigquery/py.typed",
        # There are no public API endpoints for the generated ModelServiceClient,
        # thus there's no point in generating it and its tests.
        library / f"google/cloud/bigquery_{version}/services/**",
        library / f"tests/unit/gapic/bigquery_{version}/**",
    ],
)

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
    cov_level=100,
    samples=True,
    microgenerator=True,
    split_system_tests=True,
)

# BigQuery has a custom multiprocessing note
s.move(
    templated_files,
    excludes=[
        "noxfile.py",
        "docs/multiprocessing.rst",
        ".coveragerc",
        # Include custom SNIPPETS_TESTS job for performance.
        # https://github.com/googleapis/python-bigquery/issues/191
        ".kokoro/presubmit/presubmit.cfg",
    ]
)

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------

python.py_samples()

# Do not expose ModelServiceClient, as there is no public API endpoint for the
# models service.
s.replace(
    "google/cloud/bigquery_v2/__init__.py",
    r"from \.services\.model_service import ModelServiceClient",
    "",
)
s.replace(
    "google/cloud/bigquery_v2/__init__.py",
    r"""["']ModelServiceClient["'],""",
    "",
)

# Adjust Model docstring so that Sphinx does not think that "predicted_" is
# a reference to something, issuing a false warning.
s.replace(
    "google/cloud/bigquery_v2/types/model.py",
    r'will have a "predicted_"',
    "will have a `predicted_`",
)

s.replace(
    "docs/conf.py",
    r'\{"members": True\}',
    '{"members": True, "inherited-members": True}'
)

# Avoid breaking change due to change in field renames.
# https://github.com/googleapis/python-bigquery/issues/319
s.replace(
  "google/cloud/bigquery_v2/types/standard_sql.py",
  r"type_ ",
  "type "
)

# Tell Sphinx to ingore autogenerated docs files.
s.replace(
    "docs/conf.py",
    r'"samples/snippets/README\.rst",',
    '\g<0>\n    "bigquery_v2/services.rst",  # generated by the code generator',
)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
