import 'bootstrap';
import 'script-loader!../node_modules/jquery/dist/jquery.slim.min';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import qq from '../node_modules/fine-uploader/fine-uploader/fine-uploader.js'
import '../node_modules/fine-uploader/fine-uploader/fine-uploader.css'
//import 'node_modules/fine-uploader/jquery.fine-uploader/fine-uploader.css'

const uploader = new qq.FineUploader( {  element: document.getElementById("uploader"),
request: { endpoint: '/upload' } } )

