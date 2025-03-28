gear_modes = [
    (
        "User Defined",  # Name
        0,          # Column count
        (           # Gears
            (),
        )
    ),
    (
        "1 Gear",
        1,
        (
            (
                ("D", "num1"),
                ("R", "num0")
            ),
        )
    ),
    (
        "3 Gears",
        2,
        (
            (
                ("1", "num1"), ("3", "num3"),
                ("2", "num2"), ("R", "num0")
            ),
        )
    ),
    (
        "5 Gears",
        3,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"),
                ("2", "num2"), ("4", "num4"), ("R", "num0")
            ),
        )
    ),
    (
        "7 Gears",
        4,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
            ),
        )
    ),
    (
        "6 Gears (Double 5)",
        4,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("5", "num5"),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
            ),
        )
    ),
    (
        "9 Gears",
        5,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("9", "num9"),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
            ),
        )
    ),
    (
        "12 Gears (2 Layers)",
        4,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("", ""),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
            ),
            (
                ("7", "num7"), ("9", "num9"), ("11", "f14"), ("", ""),
                ("8", "num8"), ("10", "f13"), ("12", "f15"), ("R", "num0")
            ),
        )
    ),
    (
        "16 Gears (2 Layers)",
        5,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("", ""),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
            ),
            (
                ("9", "num9"), ("11", "f14"), ("13", "f16"), ("15", "f18"), ("", ""),
                ("10", "f13"), ("12", "f15"), ("14", "f17"), ("16", "f19"), ("R", "num0")
            ),
        )
    )
]