# rsyncsqlite

A Python wrapper around sqlite3_rsync for easy access to remote databases.

## What does it do?

It calls sqlite3_rsync before and after you manipulate the database.


```python
from rsyncsqlite import rsyncopen

with rsyncopen("user@host:some/path.sqlite") as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE name = ?", ("UserX",))
    conn.commit()

```

It stores databases in a local directory, so only the differences need to be
synced. It will try to synchronize committed changes, even if the code in the
context block fails.

## Why would I need this?

**You probably don’t need this!** If your remote location can run SQLite directly, you should
definitely use that instead. However, there are services that won’t allow that — for example, rsync.net.
