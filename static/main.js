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
        var title = document.getElementById('title_data').textContent;
        var code = document.getElementById('code').innerHTML;
        var JsonData = JSON.stringify(code);
        console.log(title);


        download(title + "_data.json", JsonData);

    };


    // var table = document.getElementById("forecast-table"); 
    // var btns = table.getElementsByClassName("btn");
    // for (var i = 0; i < btns.length; i++) {
    //     btns[i].addEventListener("click", function() {
    //         var current = document.getElementsByClassName("active");
    //         current[0].className = current[0].className.replace(" active", "");
    //         this.className += " active";
    //     });
    // }
});