'use strict'

$(document).ready( function () {
    // have to put conditions to all this
    $('.dataTableView').DataTable();

    // chooser data template
    $('#chooseDataList a').on('click', function (e) {
      e.preventDefault()
      $(this).tab('show')
    })


    var button = document.getElementById("enter");
    var input = document.getElementById("userinput");
    var listUrl = document.getElementById("listUrl");

    button.addEventListener("click", function() {
      var li = document.createElement("li");
      li.className = 'list-group-item';
      
      var inputEl = document.createElement('input');
      inputEl.type = 'checkbox';
      inputEl.name = 'list_url';
      inputEl.value = input.value;

      var label = document.createElement('label');
      label.textContent = input.value;

      li.appendChild(inputEl);
      li.appendChild(label);
      listUrl.appendChild(li);
    })
} );



