
# API

This addon exposes a small API to let you  
create Spaced & Radial ShapeStrings via Python.

<br/>

## Module

The internal module `freecad.ShapeStrings` should  
not be used and may change at any point, instead you  
should use the dedicated `ShapeStrings` module.

```Python
from ShapeStrings import ...
```

<br/>

## Spaced

Create a Spaced ShapeString object with:

```Python
from ShapeStrings import Spaced

Spaced(
    UseBoundingBox = ... ,
    FontFile = ... ,
    String = ... ,
    Offset = ... ,
    Size = ...
)
```

[» Read more about it here.][Spaced]

<br/>

## Radial

Create a Radial ShapeString object with:

```Python
from ShapeStrings import Radial

Radial(
    RotationDirection = ... ,
    StringRotation = ... ,
    StartAngle = ... ,
    Tangential = ... ,
    AngleStep = ... ,
    FontFile = ... ,
    Strings = ... ,
    Radius = ... ,
    Size = ... ,
)
```

[» Read more about it here.][Radial]



[Spaced]: ./Commands/Spaced.md
[Radial]: ./Commands/Radial.md
