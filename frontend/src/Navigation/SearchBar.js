import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import SearchIcon from '@mui/icons-material/Search';
import UploadOutlinedIcon from '@mui/icons-material/UploadOutlined';
import {IconButton, InputBase} from "@mui/material";
import Preview from "./FileUploader";
import {getResponsiveSearchBarHeight, getResponsiveSearchBarWidth} from "../utilities";


export default function SearchBar(props) {
    const [inputValue, setInputValue] = useState("");
    const host = useRef(props.host);
    const searchBarIsBlocked = useRef(props.searchBarIsBlocked);
    const onGoingRequest = useRef(props.onGoingRequest);
    const root = useRef(null);

    useEffect(() => {
        searchBarIsBlocked.current = props.searchBarIsBlocked;
    }, [props.searchBarIsBlocked]);

    useEffect(() => {
        onGoingRequest.current = props.onGoingRequest;
    }, [props.onGoingRequest]);


    const sendText = (text) => {
        // Close the upload div if it is open
        props.removeUploadDiv();
        props.setOnGoingRequest(true);
        props.setStageIsInteractive(false);
        let url = host.current + '/api/image-text?collection=' + props.selectedDataset["name"] + '&text=' + text + '&page=1';
        const options = {
            method: 'GET',
        };
        fetch(url, options)
            .then(response => {
                if (!response.ok)
                    throw new Error('Data could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                return response.json();
            })
            .then(firstGet => {
                url = host.current + '/api/image-to-tile?index=' + firstGet.index + '&collection=' + props.selectedDataset["name"] + "_image_to_tile";
                return fetch(url, options)
                    .then(response => {
                        if (!response.ok)
                            throw new Error('Data could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                        return response.json();
                    })
                    .then(secondGet => {
                        return {
                            firstGet: firstGet,
                            secondGet: secondGet
                        };
                    });
            })
            .then(result => {
                // Group result into object with fields tile and image. Tile is an array of three elements, while image contains
                // the global position of the image, and its width and height.
                let groupedResult = {};
                // noinspection JSUnresolvedVariable
                groupedResult.tile = result.secondGet.tile;
                groupedResult.image = {};
                // noinspection JSUnresolvedVariable
                groupedResult.image.x = result.firstGet.x;
                // noinspection JSUnresolvedVariable
                groupedResult.image.y = result.firstGet.y;
                groupedResult.image.width = result.firstGet.width;
                groupedResult.image.height = result.firstGet.height;
                groupedResult.image.index = result.firstGet.index;
                // Set result in parent component
                props.setShowCarousel(false);
                props.setSearchData(groupedResult);
                props.setOnGoingRequest(false);
            })
            .catch(error => {
                // Handle any errors that occur during the fetch operation
                console.error('Error:', error);
                props.setOnGoingRequest(false);
            });
    };

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
    };

    const handleEnter = (event) => {
        if (event.key === 'Enter') {
            document.getElementById("search-bar-id").blur();
            handleClickSearch(event);
        }
    }

    const handleClickSearch = () => {
        if (inputValue !== "") {
            document.getElementById("search-bar-id").blur();
            if (!props.searchBarIsClicked)
                props.setSearchBarIsClicked(true);
            if (!searchBarIsBlocked.current && !onGoingRequest.current)
                // noinspection JSIgnoredPromiseFromCall
                sendText(inputValue);
        }
    };

    const onUploadClick = () => {
        if (searchBarIsBlocked.current || onGoingRequest.current) return;
        if (document.getElementById('upload-div')) return;
        // Create div for upload
        const div = document.createElement('div');
        div.id = 'upload-div';
        document.body.appendChild(div);
        root.current = createRoot(div);
        root.current.render(
            <Preview
                host={props.host}
                setSearchData={props.setSearchData}
                setShowCarousel={props.setShowCarousel}
                selectedDataset={props.selectedDataset}
                onGoingRequest={onGoingRequest.current}
                searchBarIsBlocked={searchBarIsBlocked.current}
                setOnGoingRequest={props.setOnGoingRequest}
                setStageIsInteractive={props.setStageIsInteractive}
                removeUploadDiv={props.removeUploadDiv}
            />
        );
        // Set upload div open
        props.setUploadDivOpen(true);
    }

    return (
        <div id="search-bar" className={`w-searchbar h-searchbar flex justify-evenly items-center z-10 bg-white rounded-full pointer-events-auto
        ${props.searchBarIsClicked ? 'searchBarPositionTransition' : 'searchBarCentered'}`}>
            <InputBase
                id="search-bar-id"
                style={{width: getResponsiveSearchBarWidth().replace("px", "")
                        - 2.3 * getResponsiveSearchBarHeight().replace("px", ""),
                    paddingLeft: "1.5%"}}
                className="h-full font-bar"
                label={"Search Images by Text"}
                placeholder={"Search for an image"}
                value={inputValue}
                onClick={() => {
                    props.removeUploadDiv();
                    props.setUploadDivOpen(false);
                }}
                onChange={handleInputChange}
                onKeyDown={handleEnter}
            />
            <IconButton type="button" onClick={handleClickSearch} onTouchStart={handleClickSearch} id="search-button" style={
                {
                    color: "gray",
                    height: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                    width: getResponsiveSearchBarHeight().replace("px", "") * 0.9
                }
            }>
                <SearchIcon id="search-button-icon" style={
                    {
                        height: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                        width: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                    }
                }/>
            </IconButton>
            <div>
                <IconButton onClick={onUploadClick} onTouchStart={onUploadClick} type="button" style={
                    {
                        color: "gray",
                        height: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                        width: getResponsiveSearchBarHeight().replace("px", "") * 0.9
                    }
                }>
                    <UploadOutlinedIcon style={
                        {
                            height: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                            width: getResponsiveSearchBarHeight().replace("px", "") * 0.9,
                        }
                    }/>
                </IconButton>
            </div>
        </div>
    );
}