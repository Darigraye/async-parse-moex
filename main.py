import asyncio
import config

import re
import aiohttp

import aiomoex
import pandas as pd


async def run_server(host, port):
    server = await asyncio.start_server(client_callback, host, port)
    await server.serve_forever()


async def get_currency_rate(currency_name):
    request_url = f"{config.DOMAIN_NAME}iss/statistics/engines/currency/markets/selt/rates.json"
    arguments = {"cbrf.columns": (f"CBRF_{currency_name}_LAST,"
                                  f"CBRF_{currency_name}_LASTCHANGEPRCNT,"
                                  f"CBRF_{currency_name}_TRADEDATE,"
                                  "TODAY_DATE")}
    async with aiohttp.ClientSession() as session:
        iss = aiomoex.ISSClient(session, request_url, arguments)
        data = await iss.get()
        df = pd.DataFrame(data["cbrf"])
        pd.set_option('display.max_columns', None)
        return df.to_string()


async def client_callback(reader, writer):
    request = await read_request(reader)
    if request:
        response = await handle_request(request)
        await write_response(writer, response)


async def write_response(writer, response):
    writer.write(response.encode())
    await writer.drain()
    writer.close()


async def handle_request(request):
    """
    handles request: pulls command from request and analyzing it:
    allow currency: u, r, b, e
    """
    response = ''
    command = request.decode('utf-8')
    if re.match(r'^get_currency@[eu]$', command):
        kind_currency = command[-1]
        currency = config.CURRENCY_DICT.get(kind_currency)
        if currency:
            response = await get_currency_rate(currency)
        else:
            response = 'Ooops! You wrote incorrect currency_id. Allowed currency_id: u, e'
    else:
        response = 'Ooops! You wrote incorrect command name. Allowed names: get_currency@e/u'
    return response


async def read_request(reader):
    handled_request = bytearray()
    while True:
        package = await reader.read(config.PACKAGE_SIZE)
        if not package:
            break
        handled_request += package
        if '@' in package.decode('utf-8'):
            return handled_request
    return None


if __name__ == '__main__':
    asyncio.run(run_server(config.HOST, config.PORT))
