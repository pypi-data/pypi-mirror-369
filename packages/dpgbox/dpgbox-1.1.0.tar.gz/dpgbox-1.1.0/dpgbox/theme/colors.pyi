def mplcmap(cmap):
    """returns matplotlib's colormap

    Parameters
    ----------
    cmap : str
        colormap name

    Returns
    -------
    object
        matplotlib's colormap
    """    

def mplcm2dpgc(name='viridis', ncolors=256):
    r"""convert matplotlib's colormap to dearpygui's

    Parameters
    ----------
    name : str, optional
        the name of colormap, by default ``'viridis'``
    ncolors : int, optional
        the number of colors, by default ``256``

    Returns
    -------
    list
        colormap value in dearpygui formation

    Examples
    ----------

    ::

        import dpgbox as dpb
        import dearpygui.dearpygui as dpg

        dpg.create_context()

        rows, cols = 256, 256
        data = np.random.rand(rows, cols)
        data[128:130, 128:130] = 10
        data /= data.max()

        dpb.register_colormap("parula")

        with dpg.window(label="Matplotlib Colormap Heat Series"):
            with dpg.plot(label="Heat Series", height=400, width=400, tag="heatDemo"):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="X Axis", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Y Axis", tag="y_axis")
                
                heat_series = dpg.add_heat_series(data, rows=rows, cols=cols, label="Customized Colormap",
                                                bounds_min=[0, 0], bounds_max=[rows, cols],
                                                parent="y_axis", format="")

            # dpg.bind_colormap("heatDemo", dpb.mplcm2dpgc("plasma"))
            # dpg.bind_colormap("heatDemo", dpb.parula)
            dpg.bind_colormap("heatDemo", "parula")
            # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Viridis)
            # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Plasma)

        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    """

def ind2rgb(ind, cmap, ncolors=256, alpha=255, drange=(0, 255), dtype='uint8', ofmt='RGBA'):
    """convert indexed value to RGB or RGBA color

    Args:
        ind (list, tuple or array): indexing data
        cmap (str or colormap): colormap name
        ncolors (int, optional): the number of colors. Defaults to 256.
        alpha (list, tuple, array or None, optional): the  alpha channel of colors. Defaults to 255.
        drange (tuple, optional): output data range. Defaults to (0, 255).
        dtype (str, optional): output data dtype. Defaults to ``'uint8'``.
        ofmt (str, optional): output formation ``'RGB'`` or ``'RGBA'``. Defaults to ``'RGBA'``.

    Returns:
        array: RGB or RGBA array

    Examples:
    
        ::

            import dpgbox as dpb
            import dearpygui.dearpygui as dpg

            dpg.create_context()

            rows, cols = 256, 256
            data = np.random.rand(rows, cols)
            data[128:130, 128:130] = 255
            data /= data.max()
            
            cmap = 'plasma'
            dpb.register_colormap(cmap)

            with dpg.window(label="Matplotlib Colormap Heat Series"):
                with dpg.group(horizontal=True):
                    dpg.add_colormap_scale(colormap=cmap)
                    with dpg.plot(label="Heat Series", height=400, width=400, tag="heatDemo"):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="X Axis", tag="x_axis")
                        dpg.add_plot_axis(dpg.mvYAxis, label="Y Axis", tag="y_axis")
                        
                        heat_series = dpg.add_heat_series(data, rows=rows, cols=cols, label="Customized Colormap",
                                                        bounds_min=[0, 0], bounds_max=[rows, cols],
                                                        parent="y_axis", format="")
                        dpg.draw_circle(center=[128, 128], radius=30, color=dpb.ind2rgb(255, cmap))    
                    dpg.bind_colormap("heatDemo", dpb.mplcm2dpgc("plasma"))
                    # dpg.bind_colormap("heatDemo", dpb._parula)
                    dpg.bind_colormap("heatDemo", cmap)
                    # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Viridis)
                    # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Plasma)

            dpg.create_viewport()
            dpg.setup_dearpygui()
            dpg.show_viewport()
            dpg.start_dearpygui()
            dpg.destroy_context()

    """    

def register_colormap(name="parula", ncolors=256, tag=None):
    """register colormap

    Parameters
    ----------
    name : str, optional
        colormap name, by default ``"parula"``
    ncolors : int, optional
        the number of colors, by default 256
    tag : str, int or None, optional
        tag of colormap, by default None (same as :attr:`name`)

    Examples
    --------

    ::

        import dpgbox as dpb
        import dearpygui.dearpygui as dpg

        dpg.create_context()

        rows, cols = 256, 256
        data = np.random.rand(rows, cols)
        data[128:130, 128:130] = 10
        data /= data.max()

        cmap = 'plasma'
        dpb.register_colormap(cmap)

        with dpg.window(label="Matplotlib Colormap Heat Series"):
            with dpg.group(horizontal=True):
                dpg.add_colormap_scale(colormap=cmap)
                with dpg.plot(label="Heat Series", height=400, width=400, tag="heatDemo"):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="X Axis", tag="x_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Y Axis", tag="y_axis")
                    
                    heat_series = dpg.add_heat_series(data, rows=rows, cols=cols, label="Customized Colormap",
                                                    bounds_min=[0, 0], bounds_max=[rows, cols],
                                                    parent="y_axis", format="")

                # dpg.bind_colormap("heatDemo", dpb.mplcm2dpgc("plasma"))
                # dpg.bind_colormap("heatDemo", dpb._parula)
                dpg.bind_colormap("heatDemo", cmap)
                # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Viridis)
                # dpg.bind_colormap("heatDemo", dpg.mvPlotColormap_Plasma)

        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    """    


