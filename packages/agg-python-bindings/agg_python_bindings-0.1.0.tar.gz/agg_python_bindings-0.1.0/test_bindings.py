import agg_python_bindings
import os


def test():
    test_file = "../agi_computer_control/web_gui_terminal_recorder/record_viewer/vim_rectangle_selection_test/vim_rectangle_selection.cast"
    png_output_path = "./png_output_test"
    print("Asciicast test file: " + test_file)
    print("PNG output path: " + png_output_path)
    os.makedirs(png_output_path, exist_ok=True)
    if os.path.exists(test_file):
        print("File exists")
        agg_python_bindings.load_asciicast_and_save_png_screenshots(test_file, png_write_dir=png_output_path)
    else:
        print("File does not exist")

if __name__ == "__main__":
    test()
