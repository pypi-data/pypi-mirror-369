## Python usage

```
import baodebug

baodebug.debugutils.ConfigureRootLogger("info")  # config logger format
baodebug.debugutils.SetDebugPath("/root/visz/")  # create debug folder here and set to os.environ["DEBUG_PATH"]

import logging
logger = logging.getLogger(__name__)

logger.info("this will be printed in green")
```
