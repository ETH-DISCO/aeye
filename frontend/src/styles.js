/* Some common styles defines in js */

import {getResponsiveMenuItemHeight} from "./utilities";


export const itemsStyle = {
    height: getResponsiveMenuItemHeight(),
    fontSize: getResponsiveMenuItemHeight(),
    fontWeight: 500,
    fontFamily: "Roboto Slab, serif",
    marginLeft: "7%",
    textAlign: "center",
    lineHeight: 1.07
};

export const iconStyle = {
    width: getResponsiveMenuItemHeight().replace("px", "") * 1 + "px",
    height: getResponsiveMenuItemHeight().replace("px", "") * 1 + "px",
    color: "white"
};
