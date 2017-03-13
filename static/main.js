'use strict'

$(function() {

    function download(filename, text) {
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
    }


    var jsonExport = document.getElementById('json');
    jsonExport.onclick = function() {
      var title =  document.getElementById('title_data').textContent;
      var code =  document.getElementById('code').innerHTML;
      var JsonData = JSON.stringify(code);
      console.log(title);


      download(title + "_data.json", JsonData);

    };


    // $("#json").click(function(){
    //
    //
    // 	var blob = new Blob([JsonData], {type: "application/json"});
    // 	var downloadUrl = URL.createObjectURL(blob);
    // 	document.getElementById("code").href = downloadUrl;
    // });

    // var csvExport = document.getElementById('csv');
    // csvExport.onclick = function() {
    //     alert('button was csv');
    //     console.log('csv');
    // };

});
