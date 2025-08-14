import rjsonc

JSON = """{
    name: "John Dough",  // now that's action packed
    "age": 69,
    /*

    DEPRECATED, I PROMISE!
    
    "criminal_records": ["stealing"]

    */
    "is_cool": true // that's what i'm talkin' about!
}"""

print(rjsonc.loads(JSON))
