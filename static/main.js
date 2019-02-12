'use strict'

$(document).ready( function () {
    $('.dataTableView').DataTable();

    $('#myList a').on('click', function (e) {
      e.preventDefault()
      $(this).tab('show')
    })
} );

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
});