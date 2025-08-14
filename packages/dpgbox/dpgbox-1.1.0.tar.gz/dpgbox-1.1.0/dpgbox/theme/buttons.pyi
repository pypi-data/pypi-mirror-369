def register_button_theme(name="RoundBorder", tag=None):
    """register button theme

    Parameters
    ----------
    name : str, optional
        name of theme, by default "RoundBorder"
    tag : str, int or None, optional
        tag of button them, by default None (same as :attr:`name`)

    Examples
    ---------

    ::

        import dearpygui.dearpygui as dpg
        import dpgbox as dpb

        dpg.create_context()

        dpb.register_button_theme(tag="themeButtonRoundBorder")

        with dpg.window(label="Button Theme Demo"):
            dpg.add_button(label="Default Button")
            dpg.add_button(label="Round Theme Button")
            dpg.bind_item_theme(dpg.last_item(), "themeButtonRoundBorder")

        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    """


