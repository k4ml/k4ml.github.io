---
layout: post
title: Bagaimana menghantar email secara manual ?
tags: learning,email,smtp
---

Biasanya bila kita nak hantar email, kita cuma buka email client, (atau kebanyakkan sekarang menggunakan web based email service seperti Gmail), tapi alamat dan message yang hendak dihantar dan klik butang "Send".

Tapi bagaimana jika mahu melakukan secara manual, supaya kita lebih faham proses sebenar bagaimana sesuatu email itu boleh sampai ke alamat yang kita maksudkan ?

Kita ambil contoh alamat email `aduan@cfm.org.my`.  Pertama sekali kita kena pastikan ialah di mana email server bagi alamat di atas. Ada 2 cara. Pertama, kita anggap saja bahagian selepas `@` itu adalah email server yang akan menjadi destinasi mesej yang kita nak hantar. Maknanya disini adalah `cfm.org.my`.

Langkah kedua adalah membuka saluran komunikasi dengan server tersebut. Ianya adalah bahasa mudah untuk penjelasan teknikal untuk membuat "connection" ke soket TCP server tersebut supaya penghantaran data dapat dilakukan. Email server biasanya menerima email pada soket bernombor 25 (TCP port 25). Bagaimana hendak melakukannya ?

Tools yang paling asas boleh digunakan untuk membuat perhubungan dengan sesebuah komputer adalah `telnet`. Jadi kita boleh jalankan arahan berikut:-

```
telnet cfm.org.my 25
```

Dan biasanya kita akan dapat prompt seperti:-

```
Trying 110.4.45.130...
Connected to cfm.org.my.
Escape character is '^]'.
```

Ini bermakna kita sudah berhubung dengan komputer tersebut. Saluran komunikasi berjaya dibuka. Apa yang kita tulis dan kemudian tekan `ENTER`, akan dihantar ke server tersebut. Sama ada server tersebut akan menerima data yang kita hantar atau tidak, itu soal kedua.

Setelah saluran komunikasi dibuka, kita perlu "bercakap" dengan server tersebut dan memberitahunya ada mesej yang kita hendak hantar. "Percakapan" kita dengan server tersebut bagaimanapun tidak boleh sebarangan. Ada protokol khusus yang perlu dituruti. Ia dipanggil SMTP atau Simple Mail Transfer Protocol.

Sesi "bercakap" dengan dengan server tersebut akan kelihatan seperti ini:-

```
helo cfm.org.my
220-magneto.mschosting.com ESMTP Exim 4.88 #1 Sun, 16 Apr 2017 09:20:15 +0800
220-We do not authorize the use of this system to transport unsolicited,
220 and/or bulk e-mail.```
250 magneto.mschosting.com Hello ec2-52-74-127-79.ap-southeast-1.compute.amazonaws.com [52.74.127.79]
mail from: support@p1.com.my
250 OK
rcpt to: aduan@cfm.org.my
250 Accepted
data
354 Enter message, ending with "." on a line by itself
Subject: Test email with telnet

Test test
.
```

Aku bagaimana pun tidak tekan `ENTER` selepas karakter dot, jadi tidak tahu apa respon server tersebut. Server gmail bagaimanapun akan menolak mesej tersebut dengan mesej:-

```
550-5.7.1 [115.164.179.56] The IP you're using to send mail is not authorized to
550-5.7.1 send email directly to our servers. Please use the SMTP relay at your
550-5.7.1 service provider instead. Learn more at
550 5.7.1  https://support.google.com/mail/?p=NotAuthorizedError w12si7326803ioe.193 - gsmtp
```

Jadi seperti yang dinyatakan sebelum ini, bergantung kepada server tersebut untuk menerima mesej yang kita hantar atau tidak. Ini kerana email sentiasa disalahgunakan untuk menghantar spam jadi banyak mekanisma yang digunakan oleh email server dalam memastikan mesej yang dihantar ke server mereka adalah mesej betul dan bukannya spam. Antara yang mereka periksa adalah seperti:-

* Domain atau alamat email. Email server hanya akan menerima mesej yang dihantar ke domain mereka. Jika mesej itu untuk domain yang lain, maka kita perlu melalui proses authentication terlebih dahulu. Ini untuk mengelakkan server tersebut daripada menjadi "open relay" yang boleh digunakan untuk menghantar email ke mana sahaja sesuka hati.
* Dalam kes gmail di atas, domain saja tidak cukup. Mereka hanya menerima email dari IP yang sah. Maknanya untuk sesuatu email server menghantar email ke gmail.com, mereka perlu memastikan alamat IP mereka disahkan. Mekanisma untuk mengesahkan IP ini bagaimana pun diluar skop tulisan ini, mungkin untuk topik akan datang.

Ok, kita telah tengok bagaimana hendak mengenalpasti email server sesuatu alamat email dengan mengambil terus bahagian selepas @ sebagai email server bagi alamat tersebut. Bagaimanapun ada kes di mana email server bagi sesuatu email menggunakan alamat server yang lain. Dalam kes ini kita perlu melihat kepada apa yang dipanggil MX record domain tersebut. Tools yang biasa digunakan adalah dig tapi kita boleh juga menggunakan web based tools dengan mencari "mx record lookup" melalui Google.

Antara yang anda akan jumpa adalah https://mxtoolbox.com/. Bagaimana pun untuk tulisan ini aku akan menggunakan command line tools yang dipanggil dig.

```
dig -t mx gmail.com
```

Dan kita akan dapat result seperti:-

```
;; ANSWER SECTION:
gmail.com.    3599  IN  MX  10 alt1.gmail-smtp-in.l.google.com.
gmail.com.    3599  IN  MX  5 gmail-smtp-in.l.google.com.
gmail.com.    3599  IN  MX  40 alt4.gmail-smtp-in.l.google.com.
gmail.com.    3599  IN  MX  30 alt3.gmail-smtp-in.l.google.com.
gmail.com.    3599  IN  MX  20 alt2.gmail-smtp-in.l.google.com.
```

Jadi untuk menghantar email ke alamat gmail, kita boleh mencuba mana-mana server yang disenaraikan di atas. Secara praktisnya, email server akan melihat kewujudan MX record terlebih dahulu sebagai destinasi untuk menghantar email. Hanya jika MX record tidak wujud, maka nama domain selepas `@a` akan dianggap sebagai destinasi email tersebut.

Setakat ini dahulu, diharap anda semua akan lebih jelas bagaimana proses penghantaran email dilakukan.
