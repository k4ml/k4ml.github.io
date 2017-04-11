---
layout: post
title: Minimal Django
tags: django
---

Minimal django application. When things become so big and complex as django, sometimes it help to tear it up, broken it into smaller pieces to see how it work. So I start with just this in `app.py`:-

```
from django.core.management import execute_from_command_line
execute_from_command_line()
```

And run it as:-

```
venv/bin/python app.py
```

It run, showing a list of commands, but also show this message in red:-

```
Note that only Django core commands are listed as settings are not properly configured (error: Requested setting INSTALLED_APPS, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.).
```

We need to give it some settings.

```
from django.conf import settings
from django.core.management import execute_from_command_line

settings.configure()
execute_from_command_line()
```

But now when you try to run `venv/bin/python app.py runserver`, it gave this message:-

```
CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
```

So let set DEBUG to True then.

```
from django.conf import settings
from django.core.management import execute_from_command_line

settings.configure(DEBUG=True)
execute_from_command_line()
```

You can run runserver now, but if you try to access http://localhost:8000, you'll get 500 error, with the message on console saying:-

```
AttributeError: 'module' object has no attribute 'ROOT_URLCONF'
```

Ok, to cut long story short, I can't point 'ROOT_URLCONF' to the same `app` module. Django just hang and I'm just lazy to figure what's the issue. So let just create a second module `urls.py` and defined the routing there. So we need two modules then - `app.py` and `urls.py`:-

```
from django.conf import settings
from django.core.management import execute_from_command_line

settings.configure(DEBUG=True, ROOT_URLCONF='urls')
execute_from_command_line()
```

and define our urls.py as:-

```
from django.conf.urls import url
from django.http import HttpResponse

def index(request):
    return HttpResponse('hello')

urlpatterns = [
    url(r'^$', index, name='index'),
]
```

And that's all you need for working django app !
