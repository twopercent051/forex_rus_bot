from create_bot import config


def fiat_calc(market_fiat: float):
    deposit_fiat = int(market_fiat * (1 - config.params.deposit_commission))
    client_fiat = int(market_fiat * (1 - config.params.client_commission))
    worker_fiat = int(client_fiat * (1 + config.params.worker_commission))
    result = dict(deposit_fiat=deposit_fiat,
                  client_fiat=client_fiat,
                  worker_fiat=worker_fiat,
                  profit_fiat=deposit_fiat - worker_fiat)
    return result
