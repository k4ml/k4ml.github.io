---
layout: post
title: Docker multi-stage builds image size
tags:
  - docker, container, python
---

I have been fixing Dockerfile in our Labzero project as a preparation for PyconMY 2023 next week.
I've been using multi-stage builds for quite some time to reduce the final image size.
The general pattern is something like this:-

```
FROM python:3.10-buster as py-build

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
     && apt-get -y install --no-install-recommends netcat util-linux \
        vim bash-completion yamllint postgresql-client python3-dev \
	libpq-dev

COPY . /app
WORKDIR /app
ENV PATH=/opt/poetry/bin:$PATH
RUN ls /opt/poetry
RUN poetry config virtualenvs.in-project true && poetry install

FROM node:14.20.0 as js-build

COPY . /app
WORKDIR /app
RUN npm install && npm run production

FROM python:3.10-slim-buster

EXPOSE 8000
COPY --from=py-build /app /app
COPY --from=js-build /app/static /app/static
WORKDIR /app
CMD /app/.render/run.sh
```

The build is split into two parts. In the first part (py-build) we're building all the Python dependencies as this is a Python app.
In the second part (js-build) we're building JS dependencies for the frontend part.
The idea is that after the build is done, we can just copy the results, in case of Python the app dir + `.venv` directory while for the frontend, the generated css and js assets.

This actually save quite a lot. If we're not using multi-stage builds, the final image could be more than 1GB in size.
With multi-stage builds the final image is about 300+ MB.

But it turns out copying just the `venv` directory is not enough for Python app.
In my case about, `psycopg2` failed to load because of missing `libpg.so.5`.
Initially I try to copy only that file from `/usr/lib` using the same `COPY --from` command:-

```
COPY --from=py-build /usr/lib/x86_64-linux-gnu/libpq.so /usr/lib/x86_64-linux-gnu/libpq.so
```

But then some other files are missing as well, to the point that it just too much files to copy one by one like above. So in the end I just `apt-get` in the final stage to install the whole packages.

```
RUN apt-get update && apt-get -y install libpq-dev
```
That unfortunately increase the image size to almost 400MB, sigh.
