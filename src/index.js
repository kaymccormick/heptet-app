import {$,jQuery} from 'jquery';
import 'bootstrap'
import 'datatables.net'
import '../node_modules/bootstrap/dist/css/bootstrap.css'
import engage from './dt'

// export for others scripts to use
window.$ = $;
window.jQuery = jQuery;

    $(document).ready(function() {
    $('#domain-table').DataTable();
} );
