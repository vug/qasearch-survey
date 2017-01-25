# Survey for qa-search

## cli system examples

First set `FLASK_APP` environment variable. 
`set FLASK_APP=api.py` on Windows. 
`export FLASK_APP=api.py` on Unix.

`flask init_db` to create tables
`flask test_data` to insert two example emails

Run an interactive session via `flask shell`. Enter commands

```
import api
api.db.init_app(app)
api.has_registered('foo')
api.has_registered('student1@nyu.edu')
```

If you make a change on the file. Reload the module without restarting the interpreter.
First `import imp` then at each change `imp.reload(api)`
