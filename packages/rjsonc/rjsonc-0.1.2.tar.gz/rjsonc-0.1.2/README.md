# rjsonc
Remove JSON comments, **FAST**. No, really. I'm not paying bills for the slow Regex snail.

Supports Python typing.

```sh
$ pip install rjsonc
```

## Usage
Quite literally. I mean, all it does is removing comments. What else do you expect?

```python
import rjsonc

JSON = """{
    "name": "John Dough",  // now that's action packed
    "age": 69,
    /*

    DEPRECATED, I PROMISE!
    
    "criminal_records": ["stealing"]

    */
    "is_cool": true // that's what i'm talkin' about!
}"""

rjsonc.loads(JSON)
# {'name': 'John Dough', 'age': 69, 'is_cool': True}
```

## <kbd>def</kbd> loads
```python
def loads(s: str | bytes) -> Any
```

Loads JSON, tolerating comments.
