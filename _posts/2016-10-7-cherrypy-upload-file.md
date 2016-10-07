---
layout: post
title: CherryPy file upload
tags: python, cherrypy
---

Testing [cherrypy] file upload and spent more than an hour trying to figure out why the uploaded file ended up as empty. My initial code basically like this:-

```python
class API(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, myfile):
        with open('newfile.upload', 'wb') as newfile:
            newfile.write(myfile.read())
        return {"status": size}
```

For the HTML, I'm just following [this ajax upload tutorial][ajax-tutorial], and the JavaScript code basically look like this:-

```javascript
(function() {
var form = document.getElementById('file-form');
var fileSelect = document.getElementById('file-select');
var uploadButton = document.getElementById('upload-button');

form.onsubmit = function(event) {
    event.preventDefault();
    uploadButton.innerHTML = 'Uploading ...';

    var files = fileSelect.files;
    var formData = new FormData();

    formData.append('myfile', files[0], files[0].name);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'api/upload', true);

    xhr.onload = function () {
      if (xhr.status === 200) {
        // File(s) uploaded.
        uploadButton.innerHTML = 'Upload';
      } else {
        alert('An error occurred!');
      }
    };
    xhr.send(formData);
}
})();
```

Inspecting through `pdb` confirm that whenever I called `myfile.read()`, it just return empty binary string. To make sure that it's not the problem with AJAX upload, I try sending the file using curl:-

```
curl -v -X POST -F "myfile=@/Users/kamal/Pictures/scrum.jpg" -H "Content-Type: multipart/form-data" localhost:8080/api/upload
```

Nope, it still the same. Finally, I decided to try following the example in this [documentation][doc] where it looping reading the file. So my code end up like this:-

```python
class API(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {"key": "value"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, myfile):
        with open('newfile.upload', 'wb') as newfile:
            size = 0
            while True:
                data = myfile.file.read(8192)
                if not data:
                    break
                size += len(data)
                newfile.write(data)
        return {"status": size}
```

It's work ! So it mean the file object that cherrypy pass to your function, it should be iterated in order to get all it's content. Phew ...

[cherrypy]: http://cherrypy.org/
[ajax-tutorial]: http://blog.teamtreehouse.com/uploading-files-ajax
[doc]: http://docs.cherrypy.org/en/3.3.0/progguide/files/uploading.html
