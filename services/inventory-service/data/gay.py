items={"NTU":{
    "hood":{
        "Crimson edged with Gold Hood":{
            "Doctor":[
                "Philosophy"
            ]

        },
        "Gold edged with White Hood":{
            "Master":[
                "Engineering"
            ],
            "Bachelor":[
                "Engineering"
            ]
        },
        "Gold edged with Purple Hood":{
            "Masters":[
                "Science"
            ],
            "Bachelor":[
                "Renaissance Engineering"
            ]

        },
        "Navy Blue edged with Light Green Hood":{
            "Bachelor":[
                "Science"
            ]

        },
        "Orange edged with Crimson Hood":{
            "Masters":[
                "Business"
            ]
        },
        "Alizarin Crimson edged with White and Magenta Hood":{
            "Masters":[
                "Arts"
            ]
        },
        "Crimson edged with White Hood":{
            "Bachelor":[
                "Arts"
            ]
        },
        "Purple edged with Grey Hood":{
            "Bachelor":[
                "Medicine"
            ]
        },
        "Orange edged with White Hood":{
            "Bachelor":[
                "Accountancy"
            ]
        },
        "Orange edged with Light Blue Hood":{
            "Bachelor":[
                "Business"
            ]
        },
        "Light Blue edged with Red and White Hood":{
            "Bachelor":[
                "Education (NIE)"
            ]
        },
        "Lustrous Light Cerise Hood":{
            "Masters":[
                "Education (NIE)"
            ]
        },
        "Maroon edged with Black Hood":{
            "Masters":[
                "Communication Studies"
            ],
            "Bachelor":[
                "Communication Studies"
            ]
        
        },
        "Peacock Blue edged with Lustrous Gold Hood":{
            "Masters":[
                "Social Sciences"
            ],
            "Bachelor":[
                "Social Sciences"
            ]
        }
        

    },
    "Gown":{
        "Gown with Gold Front":{
            "Bachelor": ["Engineering"]
        },
        "Blue Gown with Sleeves":{
            "Masters":[
                "Social Sciences","Arts","Engineering","Science","Business","Education (NIE)","Communication Studies"
            ],
            "Bachelor":[
                "Social Sciences","Arts","Science","Business","Education (NIE)","Communication Studies","Accountancy","Medicine","Renaissance Engineering"
            ]

        },
        "Gown with Crimson Front and Sleeves":{
            "Doctor":[
                "Philosophy"
            ]
        }

    },
    "Hat":{
        "Mortarboard":{
            "Masters":[
                "Social Sciences","Arts","Engineering","Science","Business","Education (NIE)","Communication Studies"
            ],
            "Bachelor":[
                "Social Sciences","Arts","Engineering","Science","Business","Education (NIE)","Communication Studies","Accountancy","Medicine","Renaissance Engineering"
            ]
        },
        "Bonnet":{
            "Doctor":["Philosophy"]
        }

    }
},
"SMU":{
    "hood":{
        "Purple Hood":{
            "Masters":["Law"],
            "Bachelor":["Law"],
            "Doctor":["Law"]
        },
        "Golden Yellow Hood":{
            "Bachelor":["Science (Computer Science)", "Science (Information Systems)","Science (Computing and Law)"]
            ,"Masters":["Information Technology in Business"],
            "Doctor":["Engineering","Philosophy in Computer Science","Philosophy in Information Systems"]
        },
        "Drab with Golden Trimmings Hood":{
            "Bachelor":["Accountancy"],
            "Masters":["Accountancy"],
            "Doctor":["Philosophy in Accounting"]
        },
        "Drab Hood":{
            "Bachelor":["Business Management"],
            "Masters":["Business Management"],
            "Doctor": ["Philosophy in Business"]
        },
        "Citron Hood":{
            "Bachelor":["Social Science"],
            "Masters":["Sustainability"],
            "Doctor":["Philosophy in Psychology"]

        },
        "Copper Hood":{
            "Bachelor":["Science (Economics)"],
            "Master":["Science in Financial Economics"],
            "Doctor": ["Philosophy in Economics"]
        }
    
    },
    "Hat":{
        "Black Mortarboard with Tassel":{
            "Bachelor":["Science (Economics)","Social Science","Business Management","Accountancy","Science (Computer Science)", "Science (Information Systems)","Science (Computing and Law)","Law"],
            "Masters":["Law","Information Technology in Business","Accountancy","Business Management","Sustainability","Science in Financial Economics"],
        },
        "Black Bonnet with Gold Tassel":{
            "Doctor":["Philosophy in Economics","Philosophy in Psychology","Philosophy in Business","Philosophy in Accounting","Engineering","Philosophy in Computer Science","Philosophy in Information Systems","Law"]
        

        }

    },
    "Gown":{
        "Black Gown with Pointed Sleeves":{
            "Bachelor":["Science (Economics)","Social Science","Business Management","Accountancy","Science (Computer Science)", "Science (Information Systems)","Science (Computing and Law)","Law"]

        },
        "Black Gown with Oblong Sleeves":{
            "Masters":["Law","Information Technology in Business","Accountancy","Business Management","Sustainability","Science in Financial Economics"]

        },
        "Black Gown with Yellow Front and Sides":{
             "Doctor":["Philosophy in Economics","Philosophy in Psychology","Philosophy in Business","Philosophy in Accounting","Engineering","Philosophy in Computer Science","Philosophy in Information Systems","Law"]
        }

    }
},
"ITE":{
    "Gown":{
        "Gown Robe with Red-Yellow Flap":["Nitec"],
        "Gown Robe with Red-Blue Flap":["Higher Nitec"],
        "Gown Robe with Red-Purple Flap":["Word-Study Diploma","Technical Diploma"],
        
    }

},
"Singapore Polytechnic":{
    "Gown":{
        "Gown Robe with Gold Flap and Gold edges":["Polytechnic Diploma"]
    }
    

},
"Temasek Polytechnic":{
    "Gown":{
        "Gown Robe with Red Front": ["Polytechnic Diploma"]
    }

},
"Nanyang Polytechnic":{
    "Gown":{
        "Navy Blue Graduation Gown with Hood":["Polytechnic Diploma"]
    }

},
}

  # paste your dictionary here


# start from 28 because 1–27 already exist
style_counter = 28

style_map = {}  # (institution, item_type, item_name) -> style_id
styles_sql = []
packages_sql = []


price_defaults = {
    "hood": (45.00, 20.00, 30.00),
    "gown": (75.00, 40.00, 40.00),
    "hat": (15.00, 10.00, 5.00)
}


def get_style_id(institution, item_type, item_name):
    global style_counter

    key = (institution, item_type, item_name)

    if key not in style_map:
        style_map[key] = style_counter

        price, rental, deposit = price_defaults.get(item_type.lower(), (50, 20, 20))

        styles_sql.append(
            f"""INSERT INTO InventoryStyle
(style_id, item_name, color, item_type, item_price, rental_fee, deposit)
VALUES ({style_counter}, '{item_name}', NULL, '{item_type}', {price}, {rental}, {deposit});"""
        )

        style_counter += 1

    return style_map[key]


for institution, categories in items.items():

    package_map = {}

    for item_type, item_data in categories.items():

        for item_name, edu_data in item_data.items():

            style_id = get_style_id(institution, item_type.lower(), item_name)

            # ITE / Polytechnic case (list instead of dict)
            if isinstance(edu_data, list):

                for level in edu_data:

                    key = (institution, level)

                    if key not in package_map:
                        package_map[key] = {
                            "hat": None,
                            "hood": None,
                            "gown": None
                        }

                    package_map[key]["gown"] = style_id

            else:

                for edu_level, faculties in edu_data.items():

                    for faculty in faculties:

                        key = (institution, edu_level, faculty)

                        if key not in package_map:
                            package_map[key] = {
                                "hat": None,
                                "hood": None,
                                "gown": None
                            }

                        package_map[key][item_type.lower()] = style_id


    for key, styles in package_map.items():

        if len(key) == 2:
            institution, level = key
            faculty = level
            education = level
        else:
            institution, education, faculty = key

        hat = "NULL" if styles["hat"] is None else styles["hat"]
        hood = "NULL" if styles["hood"] is None else styles["hood"]
        gown = "NULL" if styles["gown"] is None else styles["gown"]

        packages_sql.append(
            f"""INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('{education}', '{institution}', '{faculty}', {hat}, {hood}, {gown});"""
        )


with open("generated_inserts.sql", "w") as f:

    f.write("-- InventoryStyle Inserts\n\n")
    for s in styles_sql:
        f.write(s + "\n")

    f.write("\n\n-- Package Inserts\n\n")

    for p in packages_sql:
        f.write(p + "\n")


print("SQL file generated: generated_inserts.sql")