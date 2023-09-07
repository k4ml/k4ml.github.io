---
layout: post
title: Local Python is not for the System
tags: python
---

More than 10 years ago I wrote about [System Python is not for you](/system-python-is-not-for-you/) to explain that we should not use system python for our development purpose.

But the opposite also true. The local python you have is not for the system (OS) to use. And I bumped into this situation today.
I have 2 users that I use in my Manjaro laptop. I created second user few years back when I want to try using KDE instead of Gnome.
But to avoid messing up current Gnome setup, I created second user that will use KDE as desktop environment instead.

Fast forward today, I think we experiment with KDE can be concluded - I'm happy with it.
So I decided to get back to my first user account and make it use KDE as well.
All went well until I want to listen to some music.
I'm using Lollypop in the second user but when I try to open it in my first user, nothing happened.
Knowing well this could be the program errored somewhere, I try to start it from the terminal, KDE konsole actually.
And right there is the error.

```
ImportError: cannot import name '_gi' from 'gi'
```

`gi` is namespace name for Python GObject. In Archlinux system, it's provided by `python-gobject` package. Trying to `pamac reinstall python-gobject`, no dice.
The error message showed that it using Python 3.11, which is the default system python for archlinux. But when I checked through terminal, `which python` showed that I'm using python-3.6, provided by pyenv.

So long time ago while I'm still doing development on this laptop (these days I'm using Gitpod), I have installed pyenv to help getting different python versions for each of different project I'm working on.

The first thing I did is to remove `eval "$(pyenv init -)"` from my `.bash_profile` and reload (or should I call `re-source`) it. But that doesn't remove pyenv's shim from the PATH.

To verify that this indeed caused by pyenv, I just overwrite my `PATH` to just `/usr/bin:/usr/sbin` and launch lollypop.
Yay, it running!
But to remove pyenv from the kde environment is not easy. So somehow KDE also sourcing `.bash_profile` (since `pyenv init` called here).
So the only way to get new environment without pyenv in `PATH` is to logout.
After logout and login again, lollypop is running.

What is the take away? I'm not sure this is pyenv fault or KDE's fault. Should desktop environment also read from our `$HOME`'s dotfile?
But I definitely will avoid installing `pyenv` in my `$HOME` going forward.

Also this whole thing of mucking around environment to change what python to use always doesn't feels right to me.
I always advocate of [explicitly invoking][invoke] the exact python that you want.

[invoke]:https://dev.to/k4ml/python-virtualenv-no-activate-21ln
