---
layout: post
title: Login to web app using Telegram
tags:
  - telegram
  - auth
  - python
---

I have long thinking about this. The idea is that, to login to the django site, you send a message to a bot which running as webhook in the django app. Upon receiving the message, the bot will create new user using Telegram username. The bot will then return a special url that user should open in order to login. So I decided to build a POC for this.

This should not be specific to Django only. You can use any framework like Laravel or plain PHP to implement this. So let's look at the flow.

When you open the page that need to login, it will provide you with link to a Telegram bot.

![Login page]({{ site.baseurl }}/images/login1.png)

After tapping on the login link, it will open our Telegram app:-

![Login page]({{ site.baseurl }}/images/bot-start.png)

After tapping the "Start" button, we will get another button containing the login link.

![Login page]({{ site.baseurl }}/images/bot-login.png)

Clicking the login link, Telegram will prompt to verify we want to open the external url.

![Login page]({{ site.baseurl }}/images/tg-prompt.png)

Tap on open and it will open the login page, with a confirmation we want to login as the username.

![Login page]({{ site.baseurl }}/images/login-as.png)

After submitting the button, we're logged in !

![Login page]({{ site.baseurl }}/images/dashboard.png)

You can check the code at https://github.com/k4ml/gramlogin.
