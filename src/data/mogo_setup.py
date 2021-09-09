import mongoengine


def global_init():
    alias_core = 'core'
    db = 'snake_bnb'
    mongoengine.register_connection(alias=alias_core, name=db)
    # if in production
    # data = dict(
    #     username=user_from_config_or_env,
    #     password=password_from_config_or_env,
    #     host=server_from_config_or_env,
    #     port=port_from_config_or_env,
    #     authentication_source='admin',
    #     authentication_mechanism='SCRAM-SHA-1',
    #     ssl=True,
    #     ssl_cert_reqs=ssl.CERT_NONE
    # )
    # mongoengine.register_connection(alias=alias_core, name=db, **data)
