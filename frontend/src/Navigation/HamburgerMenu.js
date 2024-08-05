/* Create component for the menu */
import {slide as Menu} from 'react-burger-menu'
import './hamburgerMenu.css';
import SelectDataset from "./SelectDataset";
import {SlHome, SlQuestion} from "react-icons/sl";
import {iconStyle, itemsStyle} from "../styles";


const HamburgerMenu = (props) => {
    return (
        <div>
            <Menu id="hamburger-menu" isOpen={props.menuOpen} right
                  customBurgerIcon={false}
                  customCrossIcon={false}
                  noOverlay>
                <div onClick={() => {
                    props.setMenuOpen(false);
                    props.setPage("home");
                }} style={{cursor: "pointer"}}>
                    <div className="flex flex-row items-center justify-items-start w-full">
                        <SlHome style={iconStyle}/>
                        <h1 style={itemsStyle}>
                            Home
                        </h1>
                    </div>
                </div>
                <div onClick={() => {
                    props.setMenuOpen(false);
                    props.setPage("about");
                }} style={{cursor: "pointer"}}>
                    <div className="flex flex-row items-center justify-items-start w-full">
                        <SlQuestion style={iconStyle}/>
                        <h1 style={itemsStyle}>
                            About
                        </h1>
                    </div>
                </div>
                <SelectDataset datasets={props.datasets} setSelectedDataset={props.setSelectedDataset}/>
            </Menu>
        </div>
    );
};

export default HamburgerMenu;