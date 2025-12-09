import math
import random
import time
from typing import Callable, Dict, Optional

from inputEvent import key_tap, mouse_move, mouse_down, mouse_up
from inputBitmasks import (
    MOD_NONE,
    MOD_LCTRL,
    MOD_LSHIFT,
    MOD_LALT,
    MOUSE_LEFT,
    KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H, KEY_I,
    KEY_J, KEY_K, KEY_L, KEY_M, KEY_N, KEY_O, KEY_P, KEY_Q, KEY_R,
    KEY_S, KEY_T, KEY_U, KEY_V, KEY_W, KEY_X, KEY_Y, KEY_Z,
    KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9,
    KEY_SPACE, KEY_DOT, KEY_SLASH, KEY_ENTER, KEY_TAB, KEY_BACKSPACE,
    KEY_F5,
)

CHAR_KEYMAP: Dict[str, tuple[int, int]] = {
    "a": (KEY_A, MOD_NONE),
    "b": (KEY_B, MOD_NONE),
    "c": (KEY_C, MOD_NONE),
    "d": (KEY_D, MOD_NONE),
    "e": (KEY_E, MOD_NONE),
    "f": (KEY_F, MOD_NONE),
    "g": (KEY_G, MOD_NONE),
    "h": (KEY_H, MOD_NONE),
    "i": (KEY_I, MOD_NONE),
    "j": (KEY_J, MOD_NONE),
    "k": (KEY_K, MOD_NONE),
    "l": (KEY_L, MOD_NONE),
    "m": (KEY_M, MOD_NONE),
    "n": (KEY_N, MOD_NONE),
    "o": (KEY_O, MOD_NONE),
    "p": (KEY_P, MOD_NONE),
    "q": (KEY_Q, MOD_NONE),
    "r": (KEY_R, MOD_NONE),
    "s": (KEY_S, MOD_NONE),
    "t": (KEY_T, MOD_NONE),
    "u": (KEY_U, MOD_NONE),
    "v": (KEY_V, MOD_NONE),
    "w": (KEY_W, MOD_NONE),
    "x": (KEY_X, MOD_NONE),
    "y": (KEY_Y, MOD_NONE),
    "z": (KEY_Z, MOD_NONE),

    
    "0": (KEY_0, MOD_NONE),
    "1": (KEY_1, MOD_NONE),
    "2": (KEY_2, MOD_NONE),
    "3": (KEY_3, MOD_NONE),
    "4": (KEY_4, MOD_NONE),
    "5": (KEY_5, MOD_NONE),
    "6": (KEY_6, MOD_NONE),
    "7": (KEY_7, MOD_NONE),
    "8": (KEY_8, MOD_NONE),
    "9": (KEY_9, MOD_NONE),

    
    " ": (KEY_SPACE, MOD_NONE),
    ".": (KEY_DOT, MOD_NONE),
    "/": (KEY_SLASH, MOD_NONE),
}


DEFAULT_SEARCH_QUERIES = [
    "simple websites",
    "simple website ideas",
    "how to make ai work when loading an image for a website",
    "website images",
    "best simple websites"
]



def _human_pause(min_s: float = 0.05, max_s: float = 0.30) -> None:
    
    time.sleep(random.uniform(min_s, max_s))


def _left_click(ser) -> None:

    mouse_down(ser, MOUSE_LEFT)
    _human_pause(0.05, 0.18)
    mouse_up(ser)


def type_text(ser, text: str, base_delay: float = 0.07) -> None:

    for ch in text.lower():
        mapping = CHAR_KEYMAP.get(ch)
        if mapping is None:
            continue  # skip unsupported chars

        keycode, modifiers = mapping

        # Per-character dwell time variation
        dwell = base_delay * random.uniform(0.6, 1.6)
        key_tap(ser, keycode, modifiers, delay=dwell)

        # Gap before next key
        _human_pause(0.03, 0.20)

        # Slightly longer pause at spaces sometimes (thinking)
        if ch == " " and random.random() < 0.3:
            _human_pause(0.15, 0.40)


def _random_mouse_move(ser) -> None:

 
    duration = random.uniform(1.0, 3.0)
    start_time = time.time()
    end_time = start_time + duration

    #Initial direction
    angle = random.uniform(0, 2 * math.pi)

    #Base step length
    base_step_len = random.uniform(7.0, 16.0)

    #Initial curvature
    curvature = random.uniform(-0.08, 0.08)
    if abs(curvature) < 0.02:
        curvature = math.copysign(0.02, curvature or (1 if random.random() < 0.5 else -1))

    while True:
        now = time.time()
        if now >= end_time:
            break

        
        t = (now - start_time) / duration
        t = max(0.0, min(1.0, t))

    
        speed_profile = 0.5 - 0.5 * math.cos(math.pi * t)
     
        speed_scale = 0.5 + 2.0 * speed_profile  

        step_len = base_step_len * speed_scale

       
        if random.random() < 0.03:
            curvature = random.uniform(-0.09, 0.09)
            if abs(curvature) < 0.02:
                curvature = math.copysign(0.02, curvature or (1 if random.random() < 0.5 else -1))
        if random.random() < 0.03:
            base_step_len = random.uniform(7.0, 18.0)

        
        angle += curvature

      
        jitter_dx = random.uniform(-0.4, 0.4)
        jitter_dy = random.uniform(-0.4, 0.4)

        dx_f = step_len * math.cos(angle) + jitter_dx
        dy_f = step_len * math.sin(angle) + jitter_dy

        dx = int(round(dx_f))
        dy = int(round(dy_f))

        if dx != 0 and dy != 0:
            mouse_move(ser, dx, dy)

       
        dt = random.uniform(0.0005, 0.0025)
        time.sleep(dt)

    _human_pause(0.01, 0.06)


def _scroll_burst(ser) -> None:
    lines = random.randint(1, 4)
   
    direction = -1 if random.random() < 0.75 else 1

    for _ in range(lines):
        wheel_delta = direction * random.randint(1, 3)
        mouse_move(ser, 0, 0, wheel=wheel_delta)
        _human_pause(0.01, 0.06)


def _move_far_up_right(ser) -> None:

    duration = random.uniform(0.6, 1.2)
    end_time = time.time() + duration

    while time.time() < end_time:
        
        dx = random.randint(10, 20)
        dy = -random.randint(8, 18)
        mouse_move(ser, dx, dy)

        time.sleep(random.uniform(0.0008, 0.003))

def _local_wander_move(ser) -> None:

    duration = random.uniform(0.4, 1.2)
    end_time = time.time() + duration

    
    angle = random.uniform(0, 2 * math.pi)

    while time.time() < end_time:
        
        angle += random.uniform(-0.7, 0.7)

        step_len = random.uniform(2.0, 8.0)

        jitter_dx = random.uniform(-0.4, 0.4)
        jitter_dy = random.uniform(-0.4, 0.4)

        dx_f = step_len * math.cos(angle) + jitter_dx
        dy_f = step_len * math.sin(angle) + jitter_dy

        dx = int(round(dx_f))
        dy = int(round(dy_f))

        if dx != 0 or dy != 0:
            mouse_move(ser, dx, dy)

        time.sleep(random.uniform(0.0008, 0.003))

    _human_pause(0.01, 0.06)


def routine_1_random_mouse_moves(ser) -> None:
    # 1–5 fast movements, each 1–3 seconds
    moves = random.randint(1, 5)
    for _ in range(moves):
        _random_mouse_move(ser)
        _human_pause(0.02, 0.12)


def routine_2_random_mouse_moves_with_clicks(ser) -> None:

   
    _move_far_up_right(ser)
    _human_pause(0.02, 0.10)

   
    inner_moves = random.randint(1, 5)
    for _ in range(inner_moves):
        _local_wander_move(ser)

        if random.random() < 0.7:
            _left_click(ser)
            _human_pause(0.02, 0.10)

        _human_pause(0.01, 0.08)



def routine_3_random_mouse_moves_with_scrolls(ser) -> None:
    moves = random.randint(1, 5)
    for _ in range(moves):
        _scroll_burst(ser)
        _random_mouse_move(ser)
        _human_pause(0.02, 0.12)


def routine_4_random_mouse_moves_with_scrolls_and_final_click(ser) -> None:
    routine_3_random_mouse_moves_with_scrolls(ser)
    _human_pause(0.03, 0.15)
    _left_click(ser)


def routine_5_open_google_tab_and_search(
    ser,
    query: Optional[str] = None,
) -> None:

    if query is None:
        query = random.choice(DEFAULT_SEARCH_QUERIES)

    key_tap(ser, KEY_T, MOD_LCTRL)
    time.sleep(random.uniform(0.4, 0.9))

    type_text(ser, query, base_delay=0.07)
    _human_pause(0.10, 0.40)

    key_tap(ser, KEY_ENTER, MOD_NONE)
    time.sleep(random.uniform(1.0, 2.0))  


def routine_6_alt_tab_cycle(
    ser,
    min_cycles: int = 2,
    max_cycles: int = 5,
) -> None:
 
    even_options = [n for n in range(min_cycles, max_cycles + 1) if n % 2 == 0]

    if not even_options:
        
        cycles = max(2, min_cycles + (min_cycles % 2))
    else:
        cycles = random.choice(even_options)

    _human_pause(0.10, 0.40)
    for _ in range(cycles):
        
        key_tap(ser, KEY_TAB, MOD_LALT)
        _human_pause(0.25, 0.90)



def routine_7_close_current_tab(ser) -> None:

    key_tap(ser, KEY_W, MOD_LCTRL)
    _human_pause(0.05, 0.20)



ROUTINES: Dict[str, Callable[..., None]] = {
    "routine_1": routine_1_random_mouse_moves,
    "routine_2": routine_2_random_mouse_moves_with_clicks,
    ##"routine_3": routine_3_random_mouse_moves_with_scrolls,
    ##"routine_4": routine_4_random_mouse_moves_with_scrolls_and_final_click,
    "routine_5": routine_5_open_google_tab_and_search,
    "routine_6": routine_6_alt_tab_cycle,
    "routine_7": routine_7_close_current_tab,
}


def run_random_routine(ser) -> None:

    while True:
        
        phase1_funcs = [
            routine_1_random_mouse_moves,
            routine_3_random_mouse_moves_with_scrolls,
            routine_6_alt_tab_cycle,
        ]
        random.shuffle(phase1_funcs)

        for func in phase1_funcs:
            reps = random.randint(3, 5)
            for _ in range(reps):
                func(ser)
                _human_pause(.5, 3)

       
        routine_5_open_google_tab_and_search(ser)

       
        phase3_funcs = [
            routine_1_random_mouse_moves,
            ##routine_2_random_mouse_moves_with_clicks,
            routine_3_random_mouse_moves_with_scrolls,
            ##routine_4_random_mouse_moves_with_scrolls_and_final_click,
            routine_6_alt_tab_cycle,
        ]
        random.shuffle(phase3_funcs)

        for func in phase3_funcs:
            reps = random.randint(1, 2)
            for _ in range(reps):
                func(ser)
                _human_pause(2, 5)

       
        routine_7_close_current_tab(ser)

