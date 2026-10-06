# Harness image: the AirPatch steps (propose, apply, plan, verify, report).
# Candidate programs never run in this image; they run in the plain base image.
ARG BASE_IMAGE=python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d
FROM ${BASE_IMAGE}
COPY src/airpatch /opt/airpatch/airpatch
ENV PYTHONPATH=/opt/airpatch \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    TZ=UTC \
    LC_ALL=C.UTF-8
USER 65534:65534
ENTRYPOINT ["python3", "-m", "airpatch"]
