from flask_smorest import Api

api = Api()


def init_views():
    # Kek
    from . import monitor, auth, billing, transportation_offer, transportation_tag

    apis = (monitor, auth, billing, transportation_offer, transportation_tag)

    # get exported "blp" blueprint objects
    for blp in (a.blp for a in apis):
        api.register_blueprint(blp)
