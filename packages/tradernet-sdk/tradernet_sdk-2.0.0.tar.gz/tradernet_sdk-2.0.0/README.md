# tradernet-sdk

Python Software Development Kit for Tradernet.

## Installation

Installing tradernet with pip is straightforward:  
`python -m pip install tradernet-sdk`  
Instead of `python` you can use here and further `pypy3` depending on your preferences.

## Usage

Import the client library into your script:  
`from tradernet import Tradernet as tn`  
Initialize it with your credentials:  
`connection = tn("public_key", "private_key")`  
or create a config file `tradernet.ini` with the following content:  
```
[auth]
public   = public_key
private  = private_key
```
and initialize the client with `connection = tn.from_config("tradernet.ini")`  
Call any of its public methods, for example:  
`connection.user_info()`  

### How to trade

Import and instantiate `Tradernet` class as usual:  
```
from tradernet import Tradernet as tn


connection = tn.from_config("tradernet.ini")
```
Now let's buy 1 share of FRHC.US at the market price:  
```
connection.buy("FRHC.US")
```

### Websockets

Websocket API can be accessed via another class `TradernetWebsocket`. It
implements the asynchronous interface for Tradernet API, and its usage is a bit
more complicated. First of all, it uses an instance of the `Core` or its subclass, for example, `Tradernet` for authentication.
So it should be created first:  
`connection = Core.from_config("tradernet.ini")`  
Second, the `TradernetWebsocket` class should be used as a context manager within a coroutine as in the example below:
```
from asyncio import run
from tradernet import Tradernet as tn, TradernetWebsocket as tnws


async def main(connection: tn) -> None:  # coroutine
    async with tnws(connection) as wscon:  # type: tnws
        async for quote in wscon.market_depth("FRHC.US"):
            print(quote)


if __name__ == "__main__":
    core = tn.from_config('tradernet.ini')
    run(main(core))
```

### Password authentication

Password authentication has been completely disabled since version 2.0.0.

### Options

The notation of options in Tradernet now can easily be deciphered:
```
from tradernet import TradernetOption as tno


option = tno("+FRHC.16SEP2022.C55")
print(option)  # FRHC.US @ 55 Call 2022-09-16
```

### Wrapping market data

Another feature is to get handy pandas.DataFrame objects with market data:
```
from pandas import DataFrame
from tradernet import TradernetSymbol as tns, Tradernet as tn


connection = tn("public_key", "private_key")
symbol = tns("AAPL.US", connection).get_data()
market_data = DataFrame(
    symbol.candles,
    index=symbol.timestamps,
    columns=["high", "low", "open", "close"]
)
print(market_data.head().to_markdown())
# | date                |     high |      low |     open |    close |
# |:--------------------|---------:|---------:|---------:|---------:|
# | 1980-12-12 00:00:00 | 0.128876 | 0.12834  | 0.12834  | 0.12834  |
# | 1980-12-15 00:00:00 | 0.122224 | 0.121644 | 0.122224 | 0.121644 |
# | 1980-12-16 00:00:00 | 0.113252 | 0.112716 | 0.113252 | 0.112716 |
# | 1980-12-17 00:00:00 | 0.116064 | 0.115484 | 0.115484 | 0.115484 |
# | 1980-12-18 00:00:00 | 0.119412 | 0.118876 | 0.118876 | 0.118876 |
```

## License

The package is licensed under permissive MIT License. See the `LICENSE` file in
the top directory for the full license text.
