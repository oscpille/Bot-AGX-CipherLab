# =========================================================
# MAPA DE INTERFAZ FORGE AG - MODELO 8200 (20 chars x 8 lines)
# =========================================================

MAPA_UI = {
    "barra_superior": {
        "file": (190, 35),
        "open": (190, 90),
        "save_as": (190, 130)
    },
    
    "directorio_izquierdo": {
        "menu": (213, 180),
        "lookup": (213, 370),
        "form": (213, 437)
    },
    
    "vista_menu": {
        "menu_1": (280, 200),
        "menu_2": (280, 214),
        "items": {
            "item_1": {"coords": (900, 180), "accion": "1_click_copiar_borrar"},
            "item_2": {"coords": (900, 195), "accion": "1_click_copiar_borrar"},
            "item_5": {"coords": (900, 260), "accion": "1_click_copiar_borrar"},
            "item_6": {"coords": (900, 275), "accion": "1_click_copiar_borrar"},
            "item_7": {"coords": (800, 300), "accion": "1_click_copiar_borrar"}
        },
        "next_dropdowns": {
            "next_1": {"coords": (1100, 180)},
            "next_2": {"coords": (1100, 195)},
            "next_5": {"coords": (1100, 260)},
            "next_6": {"coords": (1100, 275)},
            "next_7": {"coords": (1100, 300)}
        }
    },
    
    "vista_lookup": {
        "archivos": {
            "1st_lookup": (300, 386),
            "2nd_lookup": (300, 403),
            "3rd_lookup": (300, 418)
        },
        "configuracion": {
            "number_of_fields": {"coords": (563, 164), "accion": "2_clics_escribir"},
            "max_length_1": {"coords": (1000, 170), "accion": "1_click_copiar_borrar"},
            "max_length_2": {"coords": (1000, 190), "accion": "1_click_copiar_borrar"}
        },
        "action_no_match": {
            "continue": (445, 504),
            "show_warning": (445, 530),
            "show_warning_insert": (445, 587)
        }
    },
    
    "vista_form": {
        "seleccion_forms": {
            "form_1": (280, 453),
            "form_2": (280, 470),
            "form_3": (280, 486),
            "form_4": (280, 505),
            "form_5": (280, 520),
            "form_6": (280, 535),
            "form_7": (280, 555),
            "form_8": (280, 570),
            "form_9": (280, 585),
            "form_10": (280, 605)
        },
        
        # NUEVA PROPIEDAD PARA EL MODELO 8200 (SCROLL OBLIGATORIO)
        "scroll_tabla": {
            "origen": (1176, 156),
            "destino": (1176, 300)
        },

        "tabla": {
            "columnas_x": {
                "data_type": 520,
                "prompt": 640,
                "input_type": 675,
                "min_length": 840,
                "max_length": 920,
                "variables_field": 1000,
                "more": 1090
            },
            # Calculadas con tu diagonal (Delta Y = 20 píxeles por fila)
            "filas_y": [380, 400, 420, 440, 460, 480, 500, 520],
            
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
                    "alphameric": {"tecla": "a", "pulsaciones": 2},
                    "serial":     {"tecla": "s", "pulsaciones": 1} # NUEVO DATO MODELO 8200
                }
            },
            
            "formatos_more": {
                "formato_1": ["text", "integer", "real", "letter", "auto", "boolean", "fixed_data", "alphameric"],
                "formato_2": ["lookup", "counter"],
                "formato_3": ["date", "time"],
                "bloqueado": ["prompt", "passdown", "extension", "pause", "serial"]
            }
        },
        
        "sub_menus": {
            "lookup": {
                "no_lookup": (700, 165),
                "1st_lookup": (700, 190),
                "2nd_lookup": (700, 217),
                "3rd_lookup": (700, 244)
            },
            "date_time_stamp": {
                "no_time_stamp": (700, 310),
                "add_front": (700, 343),
                "append_end": (700, 375)
            }
        },
        
        "properties": {
            "esc": {
                "coords": (570, 165),
                "comportamiento": "atajo_teclado_f_m"
            },
            "next": {
                "coords": (570, 190),
                "comportamiento": "atajo_teclado_f_m"
            },
            "record": {
                "coords": (570, 225),
                "atajo": "p_s_x4"
            }
        }
        
    },
    
    "vista_more": {
        "columna_more_x": 1090,
        "formato_1": {
            "check_prefix": (458, 307),
            "campo_prefix": (600, 307),
            "check_input_mark": (458, 370),
            "campo_input_mark": (600, 370)
        },
        "formato_2": {
            "check_save_field": (596, 300),
            "check_prefix": (596, 400),
            "campo_prefix": (732, 400)
        },
        "formato_3": {
            "check_show_time": (597, 360)
        },
        "grid_ascii": {
            "origen_x": 400,
            "origen_y": 191,
            "delta_x": 40,
            "delta_y": 20,
            "btn_ok": (1000, 530),
            "btn_clear": (900, 555),
            "btn_cancel": (1000, 570)
        }
    }
}