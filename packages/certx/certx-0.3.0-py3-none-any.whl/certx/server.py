import ssl

from certx import app
from certx.common import service
from certx.conf import CONF


def start():
    service.prepare_command()

    if CONF.enable_https:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(CONF.server_cert, CONF.server_key, password=CONF.key_pass)
    else:
        ssl_context = None

    app.run(host=CONF.host, port=CONF.port,
            debug=CONF.debug,
            threaded=CONF.threaded,
            ssl_context=ssl_context)


if __name__ == '__main__':
    start()
