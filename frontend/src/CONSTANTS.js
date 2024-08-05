export const responsive_margins = {
    m_side_320: getComputedStyle(document.documentElement).getPropertyValue("--m-canvas-side-320"),
    m_side_480: getComputedStyle(document.documentElement).getPropertyValue("--m-canvas-side-480"),
    m_side_768: getComputedStyle(document.documentElement).getPropertyValue("--m-canvas-side-768"),
    m_side_1024: getComputedStyle(document.documentElement).getPropertyValue("--m-canvas-side-1024"),
    m_side_1200: getComputedStyle(document.documentElement).getPropertyValue("--m-canvas-side-1200"),
};

export const stickybar_responsive_heights = {
    h_sticky_320: getComputedStyle(document.documentElement).getPropertyValue("--h-sticky-320"),
    h_sticky_480: getComputedStyle(document.documentElement).getPropertyValue("--h-sticky-480"),
    h_sticky_768: getComputedStyle(document.documentElement).getPropertyValue("--h-sticky-768"),
    h_sticky_1024: getComputedStyle(document.documentElement).getPropertyValue("--h-sticky-1024"),
    h_sticky_1200: getComputedStyle(document.documentElement).getPropertyValue("--h-sticky-1200"),
};

export const responsive_menu_item_heights = {
    h_item_320: getComputedStyle(document.documentElement).getPropertyValue("--h-item-320"),
    h_item_480: getComputedStyle(document.documentElement).getPropertyValue("--h-item-480"),
    h_item_768: getComputedStyle(document.documentElement).getPropertyValue("--h-item-768"),
    h_item_1024: getComputedStyle(document.documentElement).getPropertyValue("--h-item-1024"),
    h_item_1200: getComputedStyle(document.documentElement).getPropertyValue("--h-item-1200"),
};

export const button_size = getComputedStyle(document.documentElement).getPropertyValue("--button-size");

export const carousel_container_margin_top = getComputedStyle(document.documentElement).getPropertyValue("--carousel-container-margin-top");

export const carousel_container_margin_bottom = {
    m_bottom_320: getComputedStyle(document.documentElement).getPropertyValue("--carousel-container-margin-bottom-320"),
    m_bottom_640: getComputedStyle(document.documentElement).getPropertyValue("--carousel-container-margin-bottom-640"),
    m_bottom_900: getComputedStyle(document.documentElement).getPropertyValue("--carousel-container-margin-bottom-900")
};

export const height_transition = getComputedStyle(document.documentElement).getPropertyValue("--height-transition");

export const margin_between_images_bottom = getComputedStyle(document.documentElement).getPropertyValue("--margin-between-images");

export const responsive_carousel_heights = {
    h_carousel_320: getComputedStyle(document.documentElement).getPropertyValue("--h-carousel-320"),
    h_carousel_480: getComputedStyle(document.documentElement).getPropertyValue("--h-carousel-480"),
    h_carousel_768: getComputedStyle(document.documentElement).getPropertyValue("--h-carousel-768"),
    h_carousel_1024: getComputedStyle(document.documentElement).getPropertyValue("--h-carousel-1024"),
    h_carousel_1200: getComputedStyle(document.documentElement).getPropertyValue("--h-carousel-1200"),
};

export const responsive_searchbar_heights = {
    h_searchbar_320: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-height-320"),
    h_searchbar_480: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-height-480"),
    h_searchbar_768: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-height-768"),
    h_searchbar_1024: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-height-1024"),
    h_searchbar_1200: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-height-1200"),
};

export const responsive_searchbar_widths = {
    w_searchbar_320: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-width-320"),
    w_searchbar_480: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-width-480"),
    w_searchbar_768: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-width-768"),
    w_searchbar_1024: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-width-1024"),
    w_searchbar_1200: getComputedStyle(document.documentElement).getPropertyValue("--searchbar-width-1200"),
};
