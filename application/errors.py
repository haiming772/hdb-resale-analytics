# application/errors.py

from flask import render_template


def init_error_handlers(app):
    """
    Register global error handlers on the given Flask app instance.
    Called from create_app() to avoid circular imports.
    """

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500
