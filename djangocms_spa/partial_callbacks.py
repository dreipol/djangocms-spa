from menus.menu_pool import menu_pool


def get_cms_menu_data_dict(request, renderer=None):
    if not renderer:
        renderer = menu_pool.get_renderer(request)

    nodes = renderer.get_nodes()

    def get_menu_node(node):
        if not node.visible:
            return False

        menu_node = {
            'path': node.get_absolute_url(),
            'label': node.title
        }

        if node.children:
            child_menu_nodes = []
            for child_node in node.children:
                child_menu_node = get_menu_node(child_node)
                if child_menu_node:
                    child_menu_nodes.append(child_menu_node)

            if child_menu_nodes:
                menu_node['children'] = child_menu_nodes

        return menu_node

    menu_nodes = []
    for node in nodes:
        if node.level == 0:
            menu_nodes.append(get_menu_node(node))

    data = {
        'type': 'generic',
        'content': {
            'menu': menu_nodes
        }
    }

    return data
