from raylibpy import (
    set_trace_log_level, LOG_NONE,
    init_window, set_target_fps, close_window,
    window_should_close,
    begin_drawing as scene,
    end_drawing as cut,
    clear_background as wipe,
    draw_text as echo,
    draw_circle as orb,
    draw_pixel as spark,
    draw_line as beam,
    draw_rectangle as frame,
    draw_triangle as shard,
    draw_ellipse as aura,
    draw_ring as halo,
    draw_poly as sigil,
    draw_grid,
    draw_cube, draw_cube_wires,
    draw_sphere, draw_sphere_wires,
    draw_cylinder, draw_cylinder_wires,
    draw_plane, draw_ray,
    draw_model, draw_model_ex,
    draw_model_wires, draw_model_wires_ex,
    draw_bounding_box,
    draw_billboard, draw_billboard_rec, draw_billboard_pro,
    begin_mode3d as scene3d,
    end_mode3d as cut3d,
    Camera3D, Vector3, Vector2, Ray,
    get_mouse_position as cursor,
    is_key_down as trigger,
    is_mouse_button_down as click,
    KEY_SPACE, KEY_ENTER, KEY_ESCAPE, KEY_W, KEY_A, KEY_S, KEY_D,
    MOUSE_LEFT_BUTTON, MOUSE_RIGHT_BUTTON,
    BLACK, WHITE, RED, BLUE, GREEN, YELLOW, GRAY, VIOLET, RAYWHITE,
    load_texture as skin,
    draw_texture as stamp,
    draw_texture_rec as stamp_rec,
    unload_texture as discard,
    Texture2D,
    load_model as mesh,
    unload_model as dissolve,
    Model,
    get_frame_time as delta,
    get_time as clock,
    get_screen_width as width,
    get_screen_height as height,
    Rectangle, check_collision_point_rec,
    Color
)

# ── Initialization ───────────────────────────
def init(w=960, h=540, title="pyorb"):
    set_trace_log_level(LOG_NONE)
    init_window(w, h, title)
    set_target_fps(60)

def close():
    close_window()

def run():
    return not window_should_close()

# ── Filesystem ───────────────────────────────
from os.path import join as path

# ── Codyfied GUI ─────────────────────────────
def button(x, y, w, h, label, color=GRAY, text_color=BLACK):
    rect = Rectangle(x, y, w, h)
    mx, my = cursor().x, cursor().y
    point = Vector2(mx, my)

    hovered = check_collision_point_rec(point, rect)
    clicked = click(MOUSE_LEFT_BUTTON) and hovered

    frame(x, y, w, h, color)
    echo(label, x + 10, y + 10, 20, text_color)

    return clicked

# ── Custom Color ─────────────────────────────
def color(r, g, b, a=255):
    return Color(r, g, b, a)