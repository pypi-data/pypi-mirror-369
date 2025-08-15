def main():
    import dearpygui.dearpygui as dpg
    import time
    import os
    import base64
    import tempfile

    dpg.create_context()
    
    # Load a better font for crisp text rendering
    with dpg.font_registry():
        default_font = dpg.add_font("/System/Library/Fonts/Helvetica.ttc", 16)
        bold_font = dpg.add_font("/System/Library/Fonts/Helvetica.ttc", 18)
        title_font = dpg.add_font("/System/Library/Fonts/Helvetica.ttc", 24)

    languages = [
        {"name": "C/clang -O3", "time": "0.50s", "color": [70, 130, 180], "y": 100, "logo_y": 0},
        {"name": "Rust", "time": "0.50s", "color": [139, 69, 19], "y": 140, "logo_y": 50},
        {"name": "Java", "time": "0.54s", "color": [255, 140, 0], "y": 180, "logo_y": 100},
        {"name": "Kotlin", "time": "0.56s", "color": [128, 0, 128], "y": 220, "logo_y": 150},
        {"name": "Go", "time": "0.80s", "color": [0, 191, 255], "y": 260, "logo_y": 200},
        {"name": "Js/Bun", "time": "0.80s", "color": [219, 112, 147], "y": 300, "logo_y": 250},
        {"name": "Js/Node", "time": "1.03s", "color": [34, 139, 34], "y": 340, "logo_y": 300},
        {"name": "Js/Deno", "time": "1.06s", "color": [0, 0, 0], "y": 380, "logo_y": 350},
        {"name": "Dart", "time": "1.34s", "color": [0, 191, 255], "y": 420, "logo_y": 400},
        {"name": "PyPy", "time": "1.53s", "color": [169, 169, 169], "y": 460, "logo_y": 450},
        {"name": "PHP", "time": "9.93s", "color": [75, 0, 130], "y": 500, "logo_y": 500},
        {"name": "Ruby", "time": "28.80s", "color": [220, 20, 60], "y": 540, "logo_y": 550},
        {"name": "R", "time": "73.16s", "color": [0, 0, 255], "y": 580, "logo_y": 600},
        {"name": "Python", "time": "74.42s", "color": [255, 215, 0], "y": 620, "logo_y": 650}
    ]

    # Load the logos image
    logo_path = os.path.join(os.path.dirname(__file__), "logos.jpeg")
    width, height, channels, data = dpg.load_image(logo_path)
    
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="logos_texture")

    start_time = time.time()
    WINDOW_WIDTH = 900
    BOX_WIDTH = 280
    BOX_START_X = 100
    FRAME_START_X = 90
    FRAME_WIDTH = 720
    FRAME_HEIGHT = 570
    FRAME_START_Y = 70
    speed_multiplier = [1.0]  # Use list so it can be modified in nested function
    last_real_time = [time.time()]
    accumulated_time = [0.0]

    def update_animation():
        current_real_time = time.time()
        delta_time = current_real_time - last_real_time[0]
        last_real_time[0] = current_real_time
        
        accumulated_time[0] += delta_time * speed_multiplier[0]
        current_time = accumulated_time[0]
        
        for i, lang in enumerate(languages):
            period = float(lang["time"].replace('s', ''))
            cycle_time = current_time % (period * 2)
            
            ball_radius = 15
            box_right_edge = FRAME_START_X + 50 + BOX_WIDTH
            frame_right_edge = FRAME_START_X + FRAME_WIDTH
            
            # Left position: ball's left edge 1 pixel from box right edge
            left_x = box_right_edge + 1 + ball_radius
            # Right position: ball's right edge 1 pixel from frame right edge  
            right_x = frame_right_edge - 1 - ball_radius
            
            travel_distance = right_x - left_x
            
            if cycle_time <= period:
                x = left_x + travel_distance * (cycle_time / period)
            else:
                x = right_x - travel_distance * ((cycle_time - period) / period)
            
            dpg.configure_item(f"ball_{i}", center=[x, lang["y"]])
    
    def speed_callback(sender, app_data):
        speed_multiplier[0] = app_data

    with dpg.window(label="1 Billion nested loop iterations", width=WINDOW_WIDTH, height=700, tag="main"):
        
        with dpg.drawlist(width=WINDOW_WIDTH, height=650, pos=[0, 60]):
            dpg.draw_rectangle([0, 0], [WINDOW_WIDTH, 650], color=[240, 240, 240], fill=[240, 240, 240])
            
            # Draw the frame around the animation area
            dpg.draw_rectangle([FRAME_START_X, FRAME_START_Y], 
                             [FRAME_START_X + FRAME_WIDTH, FRAME_START_Y + FRAME_HEIGHT], 
                             color=[80, 80, 80], thickness=3)
            
            for i, lang in enumerate(languages):
                logo_size = 30
                uv_min = [0, lang["logo_y"] / height]
                uv_max = [width / width, (lang["logo_y"] + 50) / height]
                
                dpg.draw_image("logos_texture", 
                              [FRAME_START_X + 10, lang["y"] - logo_size//2], 
                              [FRAME_START_X + 10 + logo_size, lang["y"] + logo_size//2],
                              uv_min=uv_min, uv_max=uv_max)
                
                dpg.draw_rectangle([FRAME_START_X + 50, lang["y"] - 15], [FRAME_START_X + 50 + BOX_WIDTH, lang["y"] + 15], 
                                 color=[100, 100, 100], fill=[60, 60, 60])
                
                dpg.draw_circle([FRAME_START_X + 50 + BOX_WIDTH + 20, lang["y"]], 15, 
                              color=lang["color"], fill=lang["color"], tag=f"ball_{i}")
        
        # High-quality title text with proper positioning
        title_text = "1 Billion nested loop iterations"
        title_x = (WINDOW_WIDTH // 2) - (len(title_text) * 4)
        dpg.add_text(title_text, pos=[title_x, 30], color=[50, 50, 50])
        dpg.bind_item_font(dpg.last_item(), title_font)
        
        # High-quality text labels - positioned to account for drawlist offset
        for i, lang in enumerate(languages):
            text_x = FRAME_START_X + 50 + (BOX_WIDTH / 2) - len(f"{lang['name']} ({lang['time']})") * 4.5
            # The key: lang["y"] is drawlist coordinates, so add 60 (drawlist offset) minus 8 for centering
            dpg.add_text(f"{lang['name']} ({lang['time']})", 
                        pos=[text_x + 20, lang["y"] - 2], 
                        color=[255, 255, 255])
            dpg.bind_item_font(dpg.last_item(), default_font)
        
        # Speed control slider below the frame
        slider_y = FRAME_START_Y + FRAME_HEIGHT + 32
        slider_width = 300
        slider_start_x = FRAME_START_X + (FRAME_WIDTH - slider_width) // 2
        
        dpg.add_text("Slower", pos=[slider_start_x - 55, slider_y], color=[250, 250, 250])
        dpg.bind_item_font(dpg.last_item(), default_font)

        dpg.add_text("Faster", pos=[slider_start_x + slider_width + 10, slider_y], color=[250, 250, 250])
        dpg.bind_item_font(dpg.last_item(), default_font)

        dpg.add_slider_float(
            label="",
            default_value=1.0,
            min_value=0.1,
            max_value=2.0,
            width=slider_width,
            pos=[slider_start_x, slider_y],
            callback=speed_callback
        )

    dpg.create_viewport(title="Language Performance Visualization", width=WINDOW_WIDTH, height=720)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main", True)

    while dpg.is_dearpygui_running():
        update_animation()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()