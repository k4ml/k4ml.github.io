---
layout: post
title: "Software archeology: PDFMake in InvoiceNinja"
tags: php, archeology, pdf
---

Inspired by this [article][1], where it is the first time I found the term “*software archaeology*” being used, I decided to look into how PDF generation library called PDFMake being used in InvoiceNinja.

Based on this HackerNews post, [PDFMake was announced][2] on June, 1st 2015, almost a year ago. InvoiceNinja on the other hand was [first released 2 years ago][3]. So there must be some discussion somewhere (as in any typical open source project) where the developers discussed about integrating PDFMake into the project.

The first mention about pdfmake is in this [commit][4]. The first mention about pdfmake in the support forum:-

>We don’t currently support Hebrew. We’re in the process of switching from jsPDF to PDFmake which should enable support for Hebrew in the future.
>https://github.com/bpampuch/pdfmake/wiki/Custom-Fonts—client-side
>Translating the GUI mainly requires translating the following file.

I was unable to dig further and this post just sitting in the draft for too long, I'll just post it as it is now.

[1]:http://web.archive.org/web/20160414102840/http://mapleoin.github.io/perma/python-class-meta
[2]:https://news.ycombinator.com/item?id=9630431
[3]:https://laravel.io/forum/03-11-2014-invoice-ninja-a-large-open-source-laravel-application-is-live
[4]:https://github.com/invoiceninja/invoiceninja/commit/69f474cc67fafcbcfb45c423bc89c4a0ceb892b8
