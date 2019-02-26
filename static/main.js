'use strict'

$(document).ready( function () {
    // have to put conditions to all this
    $('.dataTableView').DataTable();

    // chooser data template
    $('#chooseDataList a').on('click', function (e) {
      e.preventDefault()
      $(this).tab('show')
    })
} );
