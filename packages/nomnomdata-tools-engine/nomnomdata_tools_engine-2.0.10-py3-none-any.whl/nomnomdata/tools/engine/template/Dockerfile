FROM registry.gitlab.com/nomnomdata/tools/nomnomdata-engine:latest as builder

COPY requirements.txt /nomnom/requirements.txt
RUN pip wheel --wheel-dir /python_packages -r /nomnom/requirements.txt

FROM registry.gitlab.com/nomnomdata/tools/nomnomdata-engine:latest-slim

COPY --from=builder /python_packages /python_packages
RUN pip install --no-index --find-links /python_packages /python_packages/* && rm -rf /python_packages
WORKDIR /nomnom/
COPY main.py /nomnom/
COPY pkg/*.* /nomnom/pkg/
CMD python main.py run
