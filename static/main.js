
$(document).ready( function () {
    // have to put conditions to all this
    $('.dataTableView').DataTable();

    // chooser data template
    $('#chooseDataList a').on('click', function (e) {
      e.preventDefault();
      $(this).tab('show');
    })




    // WARNING ALL OF THESE IS AWFULL...
    // catch multiselect
    var multiSelect = document.getElementsByClassName('multiSelect');

    Object.keys(multiSelect).forEach(function(el) {
        // tricky tips to get one button (same class/only one visible)
        var button = multiSelect[el].getElementsByClassName("enterUrl")[0];
        var button2 = multiSelect[el].getElementsByClassName("enterUrl")[1];
        
        button.addEventListener("click", function() {
            if (multiSelect[el].offsetWidth > 0 && multiSelect[el].offsetHeight > 0) {
                console.log('visible !');

                var input = multiSelect[el].getElementsByClassName("userinput")[0];
                var listUrl = multiSelect[el].getElementsByClassName("listUrl")[0];

                var li = document.createElement("li");
                li.className = 'list-group-item';

                var inputEl = document.createElement('input');
                inputEl.type = 'checkbox';
                inputEl.name = 'list_url';
                inputEl.value = input.value;
                inputEl.checked = true;

                var label = document.createElement('label');
                label.textContent = input.value;

                li.appendChild(inputEl);
                li.appendChild(label);

                console.log(listUrl);
                listUrl.appendChild(li);
            }
        });

        button2.addEventListener("click", function() {
            if (multiSelect[el].offsetWidth > 0 && multiSelect[el].offsetHeight > 0) {
                console.log('visible !');

                var input = multiSelect[el].getElementsByClassName("userinput")[1];
                var listUrl = multiSelect[el].getElementsByClassName("listUrl")[0];

                var li = document.createElement("li");
                li.className = 'list-group-item';

                var inputEl = document.createElement('input');
                inputEl.type = 'checkbox';
                inputEl.name = 'list_url';
                inputEl.value = input.value;
                inputEl.checked = true;

                var label = document.createElement('label');
                label.textContent = input.value;

                li.appendChild(inputEl);
                li.appendChild(label);

                console.log(listUrl);
                listUrl.appendChild(li);
            }
        });
        
    })

} );
