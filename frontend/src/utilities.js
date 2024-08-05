import {
    button_size,
    carousel_container_margin_bottom,
    carousel_container_margin_top,
    margin_between_images_bottom,
    responsive_carousel_heights,
    responsive_margins,
    responsive_menu_item_heights,
    responsive_searchbar_heights,
    responsive_searchbar_widths,
    stickybar_responsive_heights
} from "./CONSTANTS";

/* FUNCTION TO GET CONSTANT VALUES */

export function getResponsiveMargin() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return responsive_margins.m_side_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return responsive_margins.m_side_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return responsive_margins.m_side_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return responsive_margins.m_side_1024;
        case document.documentElement.clientWidth > 1200:
            return responsive_margins.m_side_1200;
        default:
            return responsive_margins.m_side_320;
    }
}

export function getStickyBarResponsiveHeight() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return stickybar_responsive_heights.h_sticky_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return stickybar_responsive_heights.h_sticky_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return stickybar_responsive_heights.h_sticky_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return stickybar_responsive_heights.h_sticky_1024;
        case document.documentElement.clientWidth > 1200:
            return stickybar_responsive_heights.h_sticky_1200;
        default:
            return stickybar_responsive_heights.h_sticky_320;
    }
}

export function getButtonSize() {
    return button_size;
}

export function getCarouselContainerMarginTop() {
    return carousel_container_margin_top;
}

export function getCarouselContainerMarginBottom() {
    switch (true) {
        case document.documentElement.clientHeight >= 320 && document.documentElement.clientHeight <= 640:
            return carousel_container_margin_bottom.m_bottom_320;
        case document.documentElement.clientHeight > 640 && document.documentElement.clientHeight <= 900:
            return carousel_container_margin_bottom.m_bottom_640;
        case document.documentElement.clientHeight > 900:
            return carousel_container_margin_bottom.m_bottom_900;
        default:
            return carousel_container_margin_bottom.m_bottom_320;
    }
}

export function getResponsiveMenuItemHeight() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return responsive_menu_item_heights.h_item_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return responsive_menu_item_heights.h_item_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return responsive_menu_item_heights.h_item_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return responsive_menu_item_heights.h_item_1024;
        case document.documentElement.clientWidth > 1200:
            return responsive_menu_item_heights.h_item_1200;
        default:
            return responsive_menu_item_heights.h_item_320;
    }
}


export function getResponsiveCarouselHeight() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return responsive_carousel_heights.h_carousel_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return responsive_carousel_heights.h_carousel_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return responsive_carousel_heights.h_carousel_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return responsive_carousel_heights.h_carousel_1024;
        case document.documentElement.clientWidth > 1200:
            return responsive_carousel_heights.h_carousel_1200;
        default:
            return responsive_carousel_heights.h_carousel_320;
    }
}

export function getResponsiveSearchBarHeight() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return responsive_searchbar_heights.h_searchbar_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return responsive_searchbar_heights.h_searchbar_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return responsive_searchbar_heights.h_searchbar_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return responsive_searchbar_heights.h_searchbar_1024;
        case document.documentElement.clientWidth > 1200:
            return responsive_searchbar_heights.h_searchbar_1200;
        default:
            return responsive_searchbar_heights.h_searchbar_320;
    }
}

export function getResponsiveSearchBarWidth() {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return responsive_searchbar_widths.w_searchbar_320;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return responsive_searchbar_widths.w_searchbar_480;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return responsive_searchbar_widths.w_searchbar_768;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return responsive_searchbar_widths.w_searchbar_1024;
        case document.documentElement.clientWidth > 1200:
            return responsive_searchbar_widths.w_searchbar_1200;
        default:
            return responsive_searchbar_widths.w_searchbar_320;
    }

}

export function getMaxHeightMainImage() {
    if (window.innerHeight >= 500)
        return window.innerHeight - getResponsiveCarouselHeight().replace("px", "")
            - margin_between_images_bottom.replace("px", "") - getStickyBarResponsiveHeight().replace("px", "")
            - getButtonSize().replace("px", "")
            - getCarouselContainerMarginTop().replace("px", "")
            - getCarouselContainerMarginBottom().replace("px", "")
            - 4;
    else
        return window.innerHeight - getStickyBarResponsiveHeight().replace("px", "")
            - getButtonSize().replace("px", "")
            - getCarouselContainerMarginTop().replace("px", "")
            - getCarouselContainerMarginBottom().replace("px", "")
            - 4;
}

/* FUNCTION TO GET URLS */

export function getUrlForImage(path, dataset, host = "") {
    return `${host}/${dataset}/resized_images/${path}`;
}