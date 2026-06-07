# =========================================================
# MAPA DE INTERFAZ FORGE AG (DELL LATITUDE) - V5.0 OPTIMIZADO
# =========================================================

MAPA_UI = {
    "barra_superior": {
        "file": (280, 100),
        "open": (280, 155),
        "save_as": (280, 200)
    },
    
    "directorio_izquierdo": {
        "menu": (300, 245),
        "lookup": (300, 260),  # NUEVA COORDENADA (COLAPSADO)
        "form": (300, 328)     # NUEVA COORDENADA (COLAPSADO)
    },
    
    "vista_menu": {
        "menu_1": (370, 260),
        "menu_2": (365, 276),
        "items": {
            "item_1": {"coords": (850, 230), "accion": "1_click_copiar_borrar"},
            "item_2": {"coords": (850, 255), "accion": "1_click_copiar_borrar"},
            "item_5": {"coords": (850, 315), "accion": "1_click_copiar_borrar"},
            "item_6": {"coords": (850, 333), "accion": "1_click_copiar_borrar"},
            "item_7": {"coords": (850, 350), "accion": "1_click_copiar_borrar"}
        },
        "next_dropdowns": {
            "next_1": {"coords": (1000, 230), "form_2": (1000, 275), "form_5": (1000, 317)},
            "next_2": {"coords": (1000, 255), "form_2": (1000, 296), "form_5": (1000, 335)},
            "next_5": {"coords": (1000, 315), "menu_2": (1000, 490)},
            "next_6": {"coords": (1000, 333), "menu_2": (1000, 509)},
            "next_7": {"coords": (1000, 350), "menu_2": (1000, 528)}
        }
    },
    
    "vista_lookup": {
        "archivos": {
            "1st_lookup": (380, 280),  # REESTRUCTURADO
            "2nd_lookup": (380, 295),  # REESTRUCTURADO
            "3rd_lookup": (380, 310)   # REESTRUCTURADO
        },
        "configuracion": {
            "number_of_fields": {"coords": (640, 220), "accion": "2_delete_para_borrar"},
            "max_length_1": {"coords": (950, 225), "accion": "1_click_copiar_borrar"},
            "max_length_2": {"coords": (950, 245), "accion": "1_click_copiar_borrar"}
        },
        "action_no_match": {
            "continue": (522, 483),
            "show_warning": (522, 505),
            "show_warning_insert": (522, 553)
        }
    },
    
    "vista_form": {
        "seleccion_forms": {
            "form_1": (365, 345),   # REESTRUCTURADO UNIFORME
            "form_2": (365, 362),
            "form_3": (365, 380),
            "form_4": (365, 397),
            "form_5": (365, 415),
            "form_6": (365, 431),
            "form_7": (365, 448),   # REMOVIDA COMPLEJIDAD DE SCROLL
            "form_8": (365, 462),
            "form_9": (365, 480),
            "form_10": (365, 500)
        },
        
        "tabla": {
            "columnas_x": {
                "data_type": 554,
                "prompt": 665,
                "input_type": 765,
                "min_length": 834,
                "max_length": 903,
                "variables_field": 978,
                "more": 1047
            },
            "filas_y": [445, 462, 487, 506, 527, 547, 566, 581],
            
            "logica_data_type": {
                "truco_reset": "n",
                "secuencias": {
                    "nil":        {"tecla": "n", "pulsaciones": 0},
                    "text":       {"tecla": "t", "pulsaciones": 1},
                    "integer":    {"tecla": "i", "pulsaciones": 1},
                    "real":       {"tecla": "r", "pulsaciones": 1},
                    "letter":     {"tecla": "l", "pulsaciones": 1},
                    "auto":       {"tecla": "a", "pulsaciones": 1},
                    "boolean":    {"tecla": "b", "pulsaciones": 1},
                    "lookup":     {"tecla": "l", "pulsaciones": 2},
                    "fixed_data": {"tecla": "f", "pulsaciones": 1},
                    "prompt":     {"tecla": "p", "pulsaciones": 1},
                    "counter":    {"tecla": "c", "pulsaciones": 1},
                    "passdown":   {"tecla": "p", "pulsaciones": 2},
                    "extension":  {"tecla": "e", "pulsaciones": 1},
                    "pause":      {"tecla": "p", "pulsaciones": 3},
                    "alphameric": {"tecla": "a", "pulsaciones": 2}
                }
            },
            
            "formatos_more": {
                "formato_1": ["text", "integer", "real", "letter", "auto", "boolean", "fixed_data", "alphameric"],
                "formato_2": ["lookup", "counter"],
                "formato_3": ["date", "time"],
                "bloqueado": ["prompt", "passdown", "extension", "pause"]
            }
        },
        
        "sub_menus": {
            "lookup": {
                "no_lookup": (717, 224),
                "1st_lookup": (809, 226),
                "2nd_lookup": (718, 251),
                "3rd_lookup": (810, 249)
            },
            "date_time_stamp": {
                "no_time_stamp": (716, 304),
                "add_front": (716, 331),
                "append_end": (716, 357)
            }
        },
        
        "properties": {
            "esc": {
                "coords": (620, 625),
                "comportamiento": "dropdown_teclado",
                "orden": ["Main", "Form 1", "...", "Form 10", "Menu 1", "...", "Menu 10"]
            },
            "next": {
                "coords": (620, 255),
                "comportamiento": "dropdown_teclado"
            },
            "record": {
                "coords": (620, 280),
                "atajo": "p",
                "save": (620, 300)
            }
        }
    }
}