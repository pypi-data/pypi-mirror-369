def register_font_theme(file=None, size=20, name="ChineseFont", tag=None):
    """register font theme

    Parameters
    ----------
    file : str, optional
        font file path
    size : int, optional
        font size
    name : str, optional
        name of theme, by default "RoundBorder"
    tag : str, int or None, optional
        tag of font them, by default None (same as :attr:`name`)

    Examples
    ---------

    ::

        import dearpygui.dearpygui as dpg
        import dpgbox as dpb

        dpg.create_context()

        dpb.register_font_theme(tag="themeFontChinese")

        with dpg.window(label="Font Theme Demo"):
            dpg.add_button(label="你好")
            dpg.add_button(label="你好")
            dpg.bind_item_font(dpg.last_item(), "themeFontChinese")
            # dpg.bind_font("themeFontChinese")

        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    """


