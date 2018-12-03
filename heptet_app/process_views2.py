import json
import logging
import argparse
import sys

from pyramid.scripts.common import get_config_loader, parse_vars

logger = logging.getLogger()


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--app-name',
        dest='app_name',
        metavar='NAME',
        help="Load the named application (default main)")

    parser.add_argument(
        '--server-name',
        dest='server_name',
        metavar='SECTION_NAME',
        help=("Use the named server as defined in the configuration file "
              "(default: main)"))

    parser.add_argument(
        '-s', '--server',
        dest='server',
        metavar='SERVER_TYPE',
        help="Use the named server.")
    parser.add_argument(
        '-o', '--output-file',
        dest='output_file',
        metavar='OUTPUT_FILE',
        help='Output the information to the named file.')

    parser.add_argument(
        'config_uri',
        nargs='?',
        default=None,
        help='The URI to the configuration file.',
    )
    parser.add_argument(
        'config_vars',
        nargs='*',
        default=(),
        help="Variables required by the config file. For example, "
             "`http_port=%%(http_port)s` would expect `http_port=8080` to be "
             "passed here.",
    )

    args = parser.parse_args(argv)

    config_uri = args.config_uri
    config_vars = parse_vars(args.config_vars)
    app_spec = args.config_uri
    app_name = args.app_name

    loader = get_config_loader(config_uri)
    loader.setup_logging(config_vars)

    # pserve_file_config(loader, global_conf=config_vars)

    server_name = args.server_name
    if args.server:
        server_spec = 'egg:pyramid'
        assert server_name is None
        server_name = args.server
    else:
        server_spec = app_spec

    server_loader = loader
    if server_spec != app_spec:
        server_loader = get_config_loader(server_spec)

    server = server_loader.get_wsgi_server(server_name, config_vars)

    app = loader.get_wsgi_app(app_name, config_vars)
    environ = {'SCRIPT_NAME': '/entry_points/json',
               'PATH_INFO': '/entry_points/json',
               'SERVER_NAME': 'localhost',
                'wsgi.url_scheme': 'http'}
    with app.request_context(environ) as request:
        response = app.handle_request(request);
        assert response.status_code == 200
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(response.text)
        else:
            print(response.text)








if __name__ == '__main__':
    main(sys.argv[1:])
