# -*- coding: utf8 -*-

from libcrowds_analyst.core import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'],
            debug=app.config['DEBUG'])
else:
    app = create_app()
