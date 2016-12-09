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
Tampak disini Laravel cuma menggunakan function built-in daripada PHP `password_hash()`. Bagaimana function ini menjana hash ?

[1]:https://laravel.com/docs/5.3/hashing
