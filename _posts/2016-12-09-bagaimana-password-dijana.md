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
Jika dirujuk pada [dokumentasi][1], Laravel menyediakan function `Hash::make()` yang boleh digunakan untuk menjana hash bagi password. Implementasi function tersebut agak simple:-

```
<?php
namespace Illuminate\Hashing;
use RuntimeException;
use Illuminate\Contracts\Hashing\Hasher as HasherContract;

class BcryptHasher implements HasherContract
{
    /**
     * Default crypt cost factor.
     *
     * @var int
     */
    protected $rounds = 10;
    /**
     * Hash the given value.
     *
     * @param  string  $value
     * @param  array   $options
     * @return string
     *
     * @throws \RuntimeException
     */
    public function make($value, array $options = [])
    {
        $cost = isset($options['rounds']) ? $options['rounds'] : $this->rounds;
        $hash = password_hash($value, PASSWORD_BCRYPT, ['cost' => $cost]);
        if ($hash === false) {
            throw new RuntimeException('Bcrypt hashing not supported.');
        }
        return $hash;
    }
```
Tampak disini Laravel cuma menggunakan function built-in daripada PHP `password_hash()`. Bagaimana function ini menjana hash ? Ada 2 parameter penting yang perlu diberikan kepada function ini iaitu password yang hendak dijana hash dan hashing algorithm yang hendak digunakan. Secara default, PHP akan menggunakan `bcrypt` sebagai hashing algorithm. Parameter optional yang boleh diberikan kepada function ini adalah `cost` dan `salt`. `cost` adalah jumlah pengulangan (iteration) dalam menjana hash tersebut supaya proses meneka hash ini akan memakan masa yang lebih lama. Jumlah default `cost` adalah 10. `salt` pula bertujuan menjadikan setiap hash unik dan tidak boleh diteka menggunakan kaedah dipanggil `rainbow table`. Parameter `salt` ini bagaimanapun sudah _deprecated_ dalam PHP 7. Developer PHP lebih menggalakkan `salt` yang dijana secara rawak oleh PHP sendiri.

Jom kita tengok bagaimana hash ini dijana oleh PHP:-

```
<?php

$hash = password_hash('abc123', PASSWORD_DEFAULT);
print $hash;
print_r(password_get_info($hash));
```
Ia akan menghasilkan output seperti berikut:-

```
$2y$10$RxSuRFfpRTsIZxwoZHzudeFl7nhiNx86pyl1Lcr6V95GM5j7GotYK
Array
(
    [algo] => 1
    [algoName] => bcrypt
    [options] => Array
        (
            [cost] => 10
        )

)
```
String yang pertama adalah hash yang dijana, manakala array yang kedua adalah maklumat berkaitan hash tersebut seperti algorithm yang digunakan dan nilai `cost`. `salt` tidak dipaparkan di sini kerana sudah dimasukkan sekali dalam hash yang dijana. Hash tersebut sentiasa dalam format:-

```
$algo$cost$salthash
```
Untuk memeriksa semula password tersebut, kita tidak memerlukan `salt` kerana ia boleh dikendalikan oleh function `password_verify()` tetapi jika ingin tahu juga nilai `salt` yang digunakan, ia adalah 22 karakter yang pertama daripada hash.

## Django
Seterusnya, jom kita lihat pula kaedah penjanaan hash oleh Django. Django membekalkan developer dengan function `make_passwor()` yang boleh diimport daripada module `django.contrib.auth.hashers`. Parameter yang perlu diberikan kepada function ini hampir sama dengan function PHP `password_hash()` iaitu password, salt dan hashing algorithm yang hendak digunakan. Secara default django akan menggunakan PBKDF2 tetapi turut menyediakan algorithm lain seperti dalam senarai di bawah:-

```
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
```
Parameter `cost` ataupun dipanggil `iterations` dalam Django tidak boleh ditukar melalui function `make_password` tetapi dengan subclass hashing algorithm yang hendak digunakan dan _override_ _attribute_ `iterations`.


[1]:https://laravel.com/docs/5.3/hashing
