---
layout: post
title: Trying Kotlin
tags:
  - kotlin
  - java
  - jetty
---

Kotlin, the new programming language from JetBrain suddenly become overnight sensation after Google announcement at IO conference last week, that Kotlin will be officially supported for Android dev. Everyone people talking about how the new language will be the future ... sigh.

Didn't want to miss, I decided to look into this new language. I'm not a mobile dev so I try to look if Kotlin also possible for web dev. Turn out there's a [specific section][1] in Kotlin docs for Web Development. There's 2 tutorials and one is titled [Creating Web Applications with Http Servlets][1]. Let's try it.

The first step of course installing all the Kotlin

```
Exception in thread "main" java.lang.UnsupportedClassVersionError: org/jetbrains/kotlin/preloading/Preloader : Unsupported major.minor version 52.0
    at java.lang.ClassLoader.defineClass1(Native Method)
    at java.lang.ClassLoader.defineClass(ClassLoader.java:800)
    at java.security.SecureClassLoader.defineClass(SecureClassLoader.java:142)
    at java.net.URLClassLoader.defineClass(URLClassLoader.java:449)
    at java.net.URLClassLoader.access$100(URLClassLoader.java:71)
    at java.net.URLClassLoader$1.run(URLClassLoader.java:361)
    at java.net.URLClassLoader$1.run(URLClassLoader.java:355)
    at java.security.AccessController.doPrivileged(Native Method)
    at java.net.URLClassLoader.findClass(URLClassLoader.java:354)
    at java.lang.ClassLoader.loadClass(ClassLoader.java:425)
    at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:308)
    at java.lang.ClassLoader.loadClass(ClassLoader.java:358)
    at sun.launcher.LauncherHelper.checkAndLoadMain(LauncherHelper.java:482)
```

Not really a good start. Next I try installing using homebrew:-

    brew install kotlin

Also got the same error. Searching for the error message, I bumped into this [bug report][arch] on Archlinux website. So indeed I'm having Java 7. So I try to install Java 8:-

    brew cask install java

Now kotlin work !

The tutorial on the Kotlin docs only stop at `gradle war` to build the web app. Then proceeded with example of running that using IntelliJ IDEA. I have no plan to install that mighty IDE yet. There must be a way to run the war from command line, right ? Fortunately, I found a [tutorial on using gretty][gretty]. The changes pretty straigtforward as you can see in the screenshot below:-

<img src="/images/gretty.png"/>

The first try didn't work though. Got this error:-

```
FAILURE: Build failed with an exception.

* Where:
Build file '/Users/kamal/kotlinc/src/kotlin-examples/tutorials/servlet-web-applications/build.gradle' line: 39

* What went wrong:
A problem occurred evaluating root project 'servlet-web-applications'.
> Could not set unknown property 'port' for object of type org.akhikhl.gretty.GrettyExtension.
```

Checking Gretty's github, I noticed some [notes on release 1.2.4][gretty-notes]:-

>Properties servicePort and statusPort are deprecated and not used anymore. Gretty automatically selects available TCP ports for communication with it's runner process.

Hmm, could be related. So I try to remove the port definition from `build.gradle` and run `gradle war` again. It's compiled !

Then the next start just running `gradle appStart` and I got my "Hello world" running. The whole source (with gretty addition) on [my Github][gh].

[1]:https://kotlinlang.org/docs/tutorials/httpservlets.html
[arch]:https://bugs.archlinux.org/task/54151
[gretty]:https://www.petrikainulainen.net/programming/gradle/getting-started-with-gradle-creating-a-web-application-project/
[gretty-notes]:https://github.com/akhikhl/gretty/blob/master/changes.md#version-124
[gh]:https://github.com/k4ml/kotlin-examples/tree/gretty/tutorials/servlet-web-applications
