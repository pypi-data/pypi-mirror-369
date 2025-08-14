def add_scatter_draw(points, ecolors, fcolors=None, marker='o', size=1, thickness=0.1):
    """add scatter plot by draw api

    Parameters
    ----------
    points : list or tuple
        list or tuple of point (x, y) or (x, y, z)
    ecolors : list or tuple
        edge colors of each point
    fcolors : list, tuple or None, optional
        fill colors of each point, by default None
    marker : str, optional
        marker type, ``'o'``, ``'^'``, ``'s'``, by default 'o'
    size : int, optional
        the size of marker, by default 1
    thickness : float, optional
         the thickness, by default 0.1

    Raises
    ------
    ValueError
        _description_

    Examples
    ---------

    ::

        import dearpygui.dearpygui as dpg
        import dpgbox as dpb
        from math import sin

        dpg.create_context()

        sindatax = []
        sindatay = []
        for i in range(0, 256):
            sindatax.append(i / 256)
            sindatay.append(0.5 + 0.5 * sin(50 * i / 256))

        cmap = 'jet'
        dpb.register_colormap(cmap)
        with dpg.window(label="Scatter plot", width=800, height=400):
            with dpg.group(horizontal=True):
                dpg.add_colormap_scale(colormap=cmap)

                # create plot
                with dpg.plot(tag="plot", label="Scatter Series", height=-1, width=600):
                    
                    dpb.add_scatter_draw(zip(sindatax, sindatay), ecolors=dpb.ind2rgb(range(len(sindatay)), cmap=cmap), fcolors=None, size=0.01)

        dpg.create_viewport(title='Plot', width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    """    


