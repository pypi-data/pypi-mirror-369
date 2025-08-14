"""
# tradingdate
Manages trade dates.

## Usage
### Get a calendar
```py
>>> import tradingdate as td
>>> cal = td.get_calendar("chinese") # by default "chinese"
>>> cal
TradingCalendar(20040102 ~ 20251231, 'chinese')
>>> list(cal)[:3]
[TradingDate(20040102), TradingDate(20040105), TradingDate(20040106)]
```

### Get a trading date
```py
>>> date = td.get_trading_date(20250116)
>>> date
TradingDate(20250116)
>>> print(date.year, date.month, date.day)
2025 01 16

>>> date - 20
TradingDate(20241218)
>>> date + 100
TradingDate(20250617)

>>> date.week.start, date.week.end
(TradingDate(20250113), TradingDate(20250117))
>>> date.month.start, date.month.end
(TradingDate(20250102), TradingDate(20250127))
>>> date.year.start, date.year.end
(TradingDate(20250102), TradingDate(20251231))
```

### Get iterator of trading dates
```py
>>> list(td.get_trading_dates(20250101, 20250106))
[TradingDate(20250102), TradingDate(20250103), TradingDate(20250106)]
```

### Make a new calendar
```py
>>> td.make_calendar("user-defined", [20250101, 20250115, 20250201])
TradingCalendar(20250101 ~ 20250201, 'user-defined')
>>> list(td.get_trading_dates(20250101, 20250131, calendar_id="user-defined"))
[TradingDate(20250101), TradingDate(20250115)]
```

## See Also
### Github repository
* https://github.com/Chitaoji/tradingdate/

### PyPI project
* https://pypi.org/project/tradingdate/

## License
This project falls under the BSD 3-Clause License.

"""

from typing import List

from . import core
from .__version__ import __version__
from .core import *

__all__: List[str] = []
__all__.extend(core.__all__)
