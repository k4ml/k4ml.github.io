---
layout: post
title: Bagaimana Password Dijana Dalam 2 Framework Open Source
tags: php, django, learning
---

Password adalah satu komponen penting dalam sebuah aplikasi web. Selain melindungi aplikasi daripada akses yang tidak sepatutnya, penjanaan password juga penting untuk melindungi password itu sendiri. Kenapa begitu ?

Ini kerana kebiasaan pengguna untuk menggunakan password yang sama dalam semua aplikasi yang mereka ingin capai. Jadi kebocoran password pada satu aplikasi, boleh menjadi tindak balas berantai untuk menyebabkan pencerobohan kepada aplikasi lain menggunakan password yang terbocor tadi.

Satu "best practice" yang diamalkan setakat ini melibatkan password adalah untuk tidak menyimpan password tersebut pada mana-mana storan dalam aplikasi. Ini mengurangkan risiko kebocoran password seperti di atas. Teknik ini dipanggil _hashing_, dimana hanya _hash_ kepada password yang disimpan, bukan password itu sendiri. Hash tersebut tidak boleh ditukar semula kepada password dan untuk memeriksa password semasa proses pengesahan (authentication), hash dijana semula daripada password yang dimasukkan oleh pengguna, dan dibandingkan dengan hash yang disimpan dalam aplikasi. Jika padan, maka boleh dianggap pengguna telah memasukkan password yang betul.

Terdapat banyak cara bagaimana hash boleh dihasilkan. Ada cara yang sudah tidak boleh digunakan kerana ia menghasilkan hash yang tidak selamat. Dalam tulisan ini, mari kita tengok bagaimana password disimpan dalam 2 framework open source yang terkenal iaitu PHP Laravel dan Python Django.

## Laravel
