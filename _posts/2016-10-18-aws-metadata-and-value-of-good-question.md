---
layout: post
title: AWS metadata services and the value of good question
tags: aws, learning
---

>Science begins by asking questions and then seeking answers. Young children understand this intuitively as they explore and try to make sense of their surroundings.

>“It is easier to judge the mind of a man by his questions rather than his answers.” — Pierre-Marc-Gaston, duc de Lévis (1764–1830)

Above is an abstract from [excellent article][0] that I wish everyone read into that. I’m a firm believer that seeking questions are much harder than the answer itself.

Whenever I met someone great (in my eye), it always a challenge for me to figure what question should I ask him/her so that I can get the best value of the limited moment I have with them.

Today in one of the chat group where I’m mostly just lurking around, someone ask about AWS metadata instance. Basically he’s curious to know, how when given query to http://169.254.169.254/latest/meta-data/xxx, it would return some information regarding the instance itself.

To be honest, even have been using AWS for years, I never thought of that question. So the curiosity inside me arose, and I started looking for answer.

My first attempt was to google for “how aws metadata work”. This however didn’t lead to any interesting result. But at least one of the result talking about the [comparison of metadata services from different cloud providers][1]. Ok, at least I learnt that metadata services not just on AWS.

My second attempt was to search for “cloud implement metadata”. Interesting result from here is a link to an issue on github, titled “[Implement ServiceInstance.getMetadata][2]”. It’s from a project called spring-cloud-consul.

This definitely gave an idea to start searching for getMetadata implementation from any of the open source cloud implementation. So I suggested him to try looking into Openstack source code.

But thinking that OpenNebula is more direct re-implementation of AWS API, I try to search for “opennebula metadata”. And among the result is OpenNebula [addon-metadata][3] project. Reading through the project [README][4], I finally found a note:-

>REDIRECT TO 169.254.169.254:80
>
>To comply with EC2, the metadata server should be available from http://169.254.169.254:80. To enable this either:
>
>Setup a redirect rule on the default gateway
>Setup a redirect on each host, using iptables

Exactly what I’m looking for !

While that should be enough, I decided to look a little bit more, this time for OpenStack implementation. Found an article that [introducing the metadata service for OpenStack][5].

Basically the implementation is not much different, just some routing to redirect the request on the local-link address, to some server that will serve the metadata request. Quoting the article:-

>When an instance accesses the metadata service, the request is routed as follows:
>
>1. An HTTP request to 169.259.169.254 is received by a metadata proxy router
>2. The request is forwarded over the inter-edge-net network to metadata proxy edge
>3. The request is then sent to the Nova API service to fetch the desired metadata and then to return the metadata to the instance that requested it.

[0]:https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3596240/
[1]:https://ahmetalpbalkan.com/blog/comparison-of-instance-metadata-services/
[2]:https://github.com/spring-cloud/spring-cloud-consul/issues/162
[3]:https://github.com/OpenNebula/addon-metadata
[4]:https://github.com/OpenNebula/addon-metadata#redirect-to-16925416925480
[5]:http://blogs.vmware.com/openstack/introducing-the-metadata-service/
