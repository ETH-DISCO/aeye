import React from 'react';
import SearchBar from "./SearchBar";
// import {Spin as Hamburger} from 'hamburger-react'
import {TfiInfoAlt} from "react-icons/tfi";
import {iconStyle} from "../styles";
import SelectDataset from "./SelectDataset";


const StickyBar = (props) => {
    const removeUploadDiv = () => {
        if (document.getElementById('upload-div')) {
            document.body.removeChild(document.getElementById('upload-div'));
        }
        props.setUploadDivOpen(false);
    }

    return (
        <div
            id="sticky-bar"
            className="fixed top-0 w-full h-sticky flex flex-row justify-between items-center bg-transparent px-1/80 z-50 pointer-events-none"
            onClick={() => {
                if (props.page === "home")
                    props.setShowCarousel(false)
            }}>
            <div>
                <div style={
                    {
                        height: iconStyle.height,
                        width: iconStyle.width,
                        cursor: "pointer",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center"
                    }
                }>
                    <SelectDataset datasets={props.datasets} setSelectedDataset={props.setSelectedDataset}
                                   setClickedImageIndex={props.setClickedImageIndex}
                                   setShowCarousel={props.setShowCarousel}
                                   removeUploadDiv={removeUploadDiv}/>
                </div>
            </div>
            {props.hasSearchBar &&
                <SearchBar host={props.host}
                           setSearchData={props.setSearchData}
                           setShowCarousel={props.setShowCarousel}
                           selectedDataset={props.selectedDataset}
                           searchBarIsClicked={props.searchBarIsClicked}
                           setSearchBarIsClicked={props.setSearchBarIsClicked}
                           searchBarIsBlocked={props.searchBarIsBlocked}
                           onGoingRequest={props.onGoingRequest}
                           setOnGoingRequest={props.setOnGoingRequest}
                           setStageIsInteractive={props.setStageIsInteractive}
                           setUploadDivOpen={props.setUploadDivOpen}
                           removeUploadDiv={removeUploadDiv}
                />
            }
            <div>
                {/*<Hamburger color={"white"} toggle={props.setMenuOpen} toggled={props.menuOpen}/>*/}

                <div onClick={() => {
                    removeUploadDiv();
                    props.setPage("about");
                }} style={
                    {
                        height: iconStyle.height,
                        width: iconStyle.width,
                        cursor: "pointer",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        pointerEvents: "auto"
                    }
                }>
                    <TfiInfoAlt style={iconStyle}/>
                </div>
            </div>
        </div>
    );
}

export default StickyBar;