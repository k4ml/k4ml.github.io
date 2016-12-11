---
layout: qna
title:  "Interface (Programming Language)"
categories: programming
---

>Baru faham sikit interface itu apa.
>
>Class
>We can extend the class.Multiple inheritance is not supported by class.
>Interface
>We can implement the interface. Interface can support multiple inheritance.
>
>Atau dengan lain perkataan class boleh berbuah sekali sahaja macam pisang. Interface pula boleh berbuah banyak kali macam mangga ...
>
>http://creativedev.in/2012/01/php-interface-explained/

A:
Salah - walaupun class boleh implement multiple interface, ia tetap tidak sama dengan multiple inheritance sebab interface tidak boleh mengandungi implementation.

Fahami dulu konsep asas interface baru cuba contoh dalam language yang anda guna. Interface adalah cara sesuatu komponen berhubung dengan komponen yang lain. Komponen disini adalah satu istilah umum merujuk kepada semua benda. Contoh, antara radio dengan manusia apakah 'interface'nya ? Mungkin tombol volume, suis on/off, punat utk eject/close cd tray dsbnya.

Konsep diatas seterusnya dibawah ke dalam design bahasa pengaturcaraan. Dalam bahasa OOP apakah komponen terlibat - mungkin object. Dalam bahasa procedural apakah komponen - mungkin function. Bagaimaina object atau function ini berhubung antara satu sama lain - melalui method call ataupun function call. Interface diwujudkan utk menyatakan secara formal bagaimana komponen-komponen ini berhubung. Keyword disini adalah FORMAL. Dalam bahasa yang tiada sokongan interface, spesifikasi bagaimana sesuatu object berhubung akan dinyatakan melalui convention.

    function drive_vehicle($vehicle) {
        $vehicle->startEngine();
    } 

Contohnya utk semua class yang implement KONSEP VEHICLE, ia mesti mempunyai method startEngine(). Di sini bergantung kepada programmer utk ikut convention yang ditetapkan. Dalam kod di atas, selagi mana object $vehicle mempunyai method startEngine() ia akan dapat berjalan tanpa sebarang masalah. Namun jika ada programmer yang tidak implement method startEngine(), ia hanya akan diketahui apabila function tersebut dijalankan (runtime) - mungkin semasa testing jika bernasib baik atau mungkin dalam production oleh user. Kelebihan bahasa yang ada konsep interface adalah convention tadi boleh di'enforce'kan ke dalam kod itu sendiri.

    function drive_vehicle(IVehicle $vehicle) {
        $vehicle->startEngine();
    }

Dalam function di atas, ia menyatakan secara FORMAL bahawa ia hanya akan menerima object yang implement interface IVehicle. Jika programmer pass object yang tidak implement interface tersebut ataupun object yang implement interface IVehicle tetapi tidak implement salah satu method yang ditetapkan dalam IVehicle, ia akan fail semasa compile time. Dalam bahasa dynamic spt PHP, benefit ini tidak ada kerana error tetap hanya dapat diketahui semasa runtime. Jadi sekiranya code tersebut tidak menggunakan interface tetapi mempunyai unit test, ia tetap akan dapat dikenalpasti.

http://en.wikipedia.org/wiki/Interface_(computing)
