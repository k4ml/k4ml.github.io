---
layout: post
title: Protobuf lesson
tags: protobuf, json
---

I've wrote [before][1] on the value of good question. Tonight, when someone post about [protobuf] in our [Telegram group], a question was asked:-

>Does protocol buffers usually depend on protocol or just a another serialization format? Cause i see they are using it to communicate between browser and server.

[Jeff]'s reply was short:-

>There is no serialized format. Everyone does that differently. Tensorflow has their own way of doing it. Tfrecords iirc

But it raised more question to us. So he took a plunge to explain that to us, and we got a nice lesson tonight on protobuf. Basically protobuf schema (the one that we define in .proto) file on concern of a single record of data. Most of the times however, we deal with multiple records of data. Take for example the following data in CSV format:-

    username,address,phone
    kamal,jb,80191991
    ali,kb,8191991
    yusuf,kl,819199191

Above, we have 3 records of people, where each record is separated with new lines. In protobuf however, there's no standard way how to represent a list of records. As explained on their [website][2]:-

>If you want to write multiple messages to a single file or stream, it is up to you to keep track of where one message ends and the next begins. The Protocol Buffer wire format is not self-delimiting, so protocol buffer parsers cannot determine where a message ends on their own. The easiest way to solve this problem is to write the size of each message before you write the message itself. When you read the messages back in, you read the size, then read the bytes into a separate buffer, then parse from that buffer. (If you want to avoid copying bytes to a separate buffer, check out the CodedInputStream class (in both C++ and Java) which can be told to limit reads to a certain number of bytes.)

Dask issue - https://github.com/dask/dask/issues/1434

Why jsonlines ?

[1]: http://k4ml.me/aws-metadata-and-value-of-good-question/
[protobuf]: https://developers.google.com/protocol-buffers/
[Telegram group]: https://telegram.me/devkini
[Jeff]: https://github.com/Jeffrey04
[2]: https://developers.google.com/protocol-buffers/docs/techniques
