# tree_types

A module that help with identifying the types of objects in a list or dictionary.

# How to use

After installing it with pip install, import in your project and use as follows:

```
from tree_types import TreeTypes

obj = {
    'v1': [1, 2, 3, 4],
    'v2': {
        'v1': 1,
        'v2': 2
    }
}

tt = TreeTypes(obj)
tt.process()

print(tt)
>> <TreeTypes(type=dict[str,list[int]|dict[str,int]])>
```

## Print Mode

You can chose how the Class will print the class tree by using the arg ```print_mode``` during instancing of class.

The arg receives a instance of the class ```PrintMode``` that is defined in this module too. It is defined as a Enum that has 2 modes:

- Class mode: the Tree is printed as a Class like the exemple above.
- Pretty mode: the Tree is printed as a text class, with indication of the itens in the object with the type of the item.