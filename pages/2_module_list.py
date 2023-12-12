from streamlit_component.module import get_search_module, get_search_tags, search_modules_by_name_and_tags, \
    set_modules_to_state, module_side_bar, get_current_module, display_module

if __name__ == '__main__':
    name = get_search_module()
    tags = get_search_tags()
    set_modules_to_state(search_modules_by_name_and_tags(name, tags))
    module_side_bar()
    if get_current_module() is not None:
        display_module(get_current_module())