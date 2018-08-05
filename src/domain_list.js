import 'bootstrap';
import 'script-loader!jquery';
import 'script-loader!../node_modules/datatables.net/js/jquery.dataTables.min';
import 'script-loader!../node_modules/datatables.net-bs4/js/dataTables.bootstrap4.min.js'

import 'script-loader!../node_modules/datatables.net-editor-bs4/js/editor.bootstrap4.js'
import '../node_modules/bootstrap/dist/css/bootstrap.css'
import '../node_modules/datatables.net-bs4/css/dataTables.bootstrap4.css';
import '../node_modules/datatables.net-editor-bs4/css/editor.bootstrap4.css'

$(document).ready(function() {
    $('#domain-table').DataTable();
} );


