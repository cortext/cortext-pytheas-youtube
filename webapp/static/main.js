
$(document).ready( function () {
    // have to put conditions to all this
    $('.dataTableView').DataTable();

    // chooser data template
    $('#chooseDataList a').on('click', function (e) {
      e.preventDefault();
      $(this).tab('show');
    })


    // WARNING ALL OF THESE IS AWFULL...
    var buttonPlaylist = document.getElementsByClassName("enterUrlPlaylist")[0];
    buttonPlaylist.addEventListener("click", function(el) {
        if (buttonPlaylist.offsetWidth > 0 && buttonPlaylist.offsetHeight > 0) {
            console.log('visible !');

            var input = document.getElementById("userinputPlaylist");
            var listUrlId = document.getElementById("listUrlIdPlaylist");

            var li = document.createElement("li");
            li.className = 'list-group-item';

            var inputEl = document.createElement('input');
            inputEl.type = 'checkbox';
            inputEl.name = 'list_url_id';
            inputEl.value = input.value;
            inputEl.checked = true;

            var label = document.createElement('label');
            label.textContent = input.value;

            li.appendChild(inputEl);
            li.appendChild(label);
            li.setAttribute('dtype', 'playlistId');


            console.log(listUrlId);
            listUrlId.appendChild(li);
        }
    });


    // catch multiselect for channel
    var multiSelect = document.getElementsByClassName('multiSelect');
    Object.keys(multiSelect).forEach(function(el) {
        // tricky tips to get one button (same class/only one visible)
        var buttonUsername = multiSelect[el].getElementsByClassName("enterUrl")[0];
        var buttonChannel = multiSelect[el].getElementsByClassName("enterUrl")[1];
        
        buttonUsername.addEventListener("click", function() {
            if (multiSelect[el].offsetWidth > 0 && multiSelect[el].offsetHeight > 0) {
                console.log('visible !');

                var input = multiSelect[el].getElementsByClassName("userinput")[0];
                var listUrlUsername = document.getElementById("listUrlUsername");
                var li = document.createElement("li");
                li.className = 'list-group-item';

                var inputEl = document.createElement('input');
                inputEl.type = 'checkbox';
                inputEl.name = 'list_url_username';
                inputEl.value = input.value;
                inputEl.checked = true;

                var label = document.createElement('label');
                label.textContent = input.value;

                li.appendChild(inputEl);
                li.appendChild(label);el
                li.setAttribute('dtype', 'username');


                console.log(listUrlUsername);
                listUrlUsername.appendChild(li);
            }
        });

        buttonChannel.addEventListener("click", function() {
            if (multiSelect[el].offsetWidth > 0 && multiSelect[el].offsetHeight > 0) {
                console.log('visible !');

                var input = multiSelect[el].getElementsByClassName("userinput")[1];
                var listUrlId = document.getElementById("listUrlId");

                var li = document.createElement("li");
                li.className = 'list-group-item';

                var inputEl = document.createElement('input');
                inputEl.type = 'checkbox';
                inputEl.name = 'list_url_id';
                inputEl.value = input.value;
                inputEl.checked = true;

                var label = document.createElement('label');
                label.textContent = input.value;

                li.appendChild(inputEl);
                li.appendChild(label);
                li.setAttribute('dtype', 'channelId');


                console.log(listUrlId);
                listUrlId.appendChild(li);
            }
        });
        
    })

} );
